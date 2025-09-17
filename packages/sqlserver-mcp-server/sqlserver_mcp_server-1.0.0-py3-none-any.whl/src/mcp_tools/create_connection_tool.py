"""
Create Connection MCP Tool for SQL Server MCP Server.

This module implements the create_connection tool that allows
creating new database connections to SQL Server instances.
"""

import asyncio
from typing import Any, Dict, List, Optional
import structlog

from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import (
    Resource, Tool, TextContent, ImageContent, EmbeddedResource,
    LoggingLevel
)

from ..models.connection import ConnectionConfig, ConnectionStatus
from ..services.connection_manager import ConnectionManager
from ..lib.exceptions import ConnectionError, AuthenticationError


logger = structlog.get_logger(__name__)


class CreateConnectionTool:
    """MCP tool for creating database connections."""
    
    def __init__(self, connection_manager: ConnectionManager):
        """Initialize the create connection tool."""
        self.connection_manager = connection_manager
    
    def get_tool_definition(self) -> Tool:
        """Get the tool definition for MCP."""
        return Tool(
            name="create_connection",
            description="Create a new connection to a SQL Server database",
            inputSchema={
                "type": "object",
                "properties": {
                    "server": {
                        "type": "string",
                        "description": "SQL Server instance name or IP address",
                        "minLength": 1
                    },
                    "database": {
                        "type": "string",
                        "description": "Default database name (optional)",
                        "pattern": "^[a-zA-Z_][a-zA-Z0-9_]*$"
                    },
                    "username": {
                        "type": "string",
                        "description": "SQL Server username (required if not using Windows Authentication)"
                    },
                    "password": {
                        "type": "string",
                        "description": "SQL Server password (required if not using Windows Authentication)"
                    },
                    "trusted_connection": {
                        "type": "boolean",
                        "description": "Use Windows Authentication",
                        "default": True
                    },
                    "encrypt": {
                        "type": "boolean",
                        "description": "Encrypt the connection",
                        "default": True
                    },
                    "connection_timeout": {
                        "type": "integer",
                        "description": "Connection timeout in seconds",
                        "minimum": 1,
                        "maximum": 60,
                        "default": 30
                    },
                    "pool_size": {
                        "type": "integer",
                        "description": "Connection pool size",
                        "minimum": 1,
                        "maximum": 50,
                        "default": 10
                    }
                },
                "required": ["server"]
            }
        )
    
    async def execute(
        self, 
        arguments: Dict[str, Any]
    ) -> List[TextContent]:
        """Execute the create connection tool."""
        try:
            # Parse and validate arguments
            config = self._parse_arguments(arguments)
            
            # Create connection
            connection_id = await self.connection_manager.create_connection(config)
            
            # Get connection status
            status = await self.connection_manager.get_connection_status(connection_id)
            
            # Format response
            response = self._format_response(connection_id, status, config)
            
            return [TextContent(type="text", text=response)]
            
        except Exception as e:
            logger.error("Create connection tool failed", error=str(e))
            error_response = self._format_error_response(str(e))
            return [TextContent(type="text", text=error_response)]
    
    def _parse_arguments(self, arguments: Dict[str, Any]) -> ConnectionConfig:
        """Parse and validate tool arguments."""
        # Extract server
        server = arguments.get("server")
        if not server or not isinstance(server, str):
            raise ValueError("Server is required and must be a string")
        
        # Extract database
        database = arguments.get("database")
        if database and not isinstance(database, str):
            raise ValueError("Database must be a string")
        
        # Extract username and password
        username = arguments.get("username")
        password = arguments.get("password")
        if username and not isinstance(username, str):
            raise ValueError("Username must be a string")
        if password and not isinstance(password, str):
            raise ValueError("Password must be a string")
        
        # Extract trusted_connection
        trusted_connection = arguments.get("trusted_connection", True)
        if not isinstance(trusted_connection, bool):
            raise ValueError("trusted_connection must be a boolean")
        
        # Extract encrypt
        encrypt = arguments.get("encrypt", True)
        if not isinstance(encrypt, bool):
            raise ValueError("encrypt must be a boolean")
        
        # Extract connection_timeout
        connection_timeout = arguments.get("connection_timeout", 30)
        if not isinstance(connection_timeout, int) or connection_timeout < 1 or connection_timeout > 60:
            raise ValueError("connection_timeout must be an integer between 1 and 60")
        
        # Extract pool_size
        pool_size = arguments.get("pool_size", 10)
        if not isinstance(pool_size, int) or pool_size < 1 or pool_size > 50:
            raise ValueError("pool_size must be an integer between 1 and 50")
        
        # Validate authentication
        if not trusted_connection:
            if not username or not password:
                raise ValueError("Username and password are required when not using Windows Authentication")
        
        return ConnectionConfig(
            server=server,
            database=database,
            username=username,
            password=password,
            trusted_connection=trusted_connection,
            encrypt=encrypt,
            connection_timeout=connection_timeout,
            pool_size=pool_size
        )
    
    def _format_response(
        self, 
        connection_id: str, 
        status: Optional[ConnectionStatus], 
        config: ConnectionConfig
    ) -> str:
        """Format connection creation response."""
        response_parts = [
            "Connection created successfully!",
            "=" * 40,
            "",
            f"Connection ID: {connection_id}",
            f"Server: {config.server}",
            f"Database: {config.database or 'default'}",
            f"Authentication: {self._get_auth_method(config)}",
            f"Encrypted: {config.encrypt}",
            f"Connection Timeout: {config.connection_timeout}s",
            f"Pool Size: {config.pool_size}",
            ""
        ]
        
        if status:
            response_parts.extend([
                "CONNECTION STATUS:",
                "-" * 20,
                f"Connected: {status.connected}",
                f"Last Activity: {status.last_activity.strftime('%Y-%m-%d %H:%M:%S')}",
                f"Response Time: {status.response_time_ms:.2f}ms",
                f"Pool Status: {status.pool_status}",
                ""
            ])
        
        response_parts.extend([
            "USAGE:",
            "-" * 10,
            f"Use connection ID '{connection_id}' in other tools to execute queries",
            "against this database connection.",
            "",
            "EXAMPLE:",
            "  execute_query(connection_id='{connection_id}', query='SELECT 1')",
            "  get_schema(connection_id='{connection_id}', database='{config.database}')",
            "  list_databases(connection_id='{connection_id}')"
        ])
        
        return "\n".join(response_parts)
    
    def _get_auth_method(self, config: ConnectionConfig) -> str:
        """Get authentication method description."""
        if config.trusted_connection:
            return "Windows Authentication"
        else:
            return "SQL Server Authentication"
    
    def _format_error_response(self, error_message: str) -> str:
        """Format error response."""
        return f"Error creating connection: {error_message}"


# Global tool instance
_create_connection_tool = None


def get_create_connection_tool() -> CreateConnectionTool:
    """Get the global create connection tool instance."""
    global _create_connection_tool
    if _create_connection_tool is None:
        # This will be initialized by the MCP server
        raise RuntimeError("Create connection tool not initialized")
    return _create_connection_tool


def initialize_create_connection_tool(connection_manager: ConnectionManager) -> None:
    """Initialize the global create connection tool instance."""
    global _create_connection_tool
    _create_connection_tool = CreateConnectionTool(connection_manager)