"""
List Databases MCP Tool for SQL Server MCP Server.

This module implements the list_databases tool that allows
listing all available databases on the SQL Server instance.
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

from ..models.schema import DatabaseInfo
from ..services.schema_service import SchemaService
from ..services.connection_manager import ConnectionManager
from ..lib.exceptions import SchemaError, ConnectionError


logger = structlog.get_logger(__name__)


class ListDatabasesTool:
    """MCP tool for listing databases."""
    
    def __init__(self, connection_manager: ConnectionManager, schema_service: SchemaService):
        """Initialize the list databases tool."""
        self.connection_manager = connection_manager
        self.schema_service = schema_service
    
    def get_tool_definition(self) -> Tool:
        """Get the tool definition for MCP."""
        return Tool(
            name="list_databases",
            description="List all available databases on the SQL Server instance",
            inputSchema={
                "type": "object",
                "properties": {
                    "include_system": {
                        "type": "boolean",
                        "description": "Include system databases (master, tempdb, model, msdb)",
                        "default": False
                    },
                    "include_metadata": {
                        "type": "boolean",
                        "description": "Include additional metadata like size and recovery model",
                        "default": True
                    }
                }
            }
        )
    
    async def execute(
        self, 
        arguments: Dict[str, Any],
        connection_id: str
    ) -> List[TextContent]:
        """Execute the list databases tool."""
        try:
            # Parse and validate arguments
            include_system = arguments.get("include_system", False)
            include_metadata = arguments.get("include_metadata", True)
            
            # Validate arguments
            if not isinstance(include_system, bool):
                raise ValueError("include_system must be a boolean")
            if not isinstance(include_metadata, bool):
                raise ValueError("include_metadata must be a boolean")
            
            # Get database list
            databases = await self.schema_service.get_database_list(
                connection_id, include_system, include_metadata
            )
            
            # Format response
            response = self._format_response(databases, include_system, include_metadata)
            
            return [TextContent(type="text", text=response)]
            
        except Exception as e:
            logger.error("List databases tool failed", error=str(e))
            error_response = self._format_error_response(str(e))
            return [TextContent(type="text", text=error_response)]
    
    def _format_response(
        self, 
        databases: List[DatabaseInfo], 
        include_system: bool, 
        include_metadata: bool
    ) -> str:
        """Format database list as text response."""
        if not databases:
            return "No databases found."
        
        response_parts = [
            f"Found {len(databases)} databases:",
            "=" * 50,
            ""
        ]
        
        # Separate system and user databases
        system_dbs = [db for db in databases if db.is_system]
        user_dbs = [db for db in databases if not db.is_system]
        
        # User databases
        if user_dbs:
            response_parts.append("USER DATABASES:")
            response_parts.append("-" * 20)
            for db in user_dbs:
                response_parts.append(f"  {db.name}")
                if include_metadata:
                    if db.size_mb is not None:
                        response_parts.append(f"    Size: {db.size_mb:.2f} MB")
                    if db.status:
                        response_parts.append(f"    Status: {db.status}")
                    if db.recovery_model:
                        response_parts.append(f"    Recovery Model: {db.recovery_model}")
                response_parts.append(f"    Created: {db.create_date.strftime('%Y-%m-%d %H:%M:%S')}")
                response_parts.append(f"    Collation: {db.collation_name}")
                response_parts.append("")
        
        # System databases
        if include_system and system_dbs:
            response_parts.append("SYSTEM DATABASES:")
            response_parts.append("-" * 20)
            for db in system_dbs:
                response_parts.append(f"  {db.name}")
                if include_metadata:
                    if db.size_mb is not None:
                        response_parts.append(f"    Size: {db.size_mb:.2f} MB")
                    if db.status:
                        response_parts.append(f"    Status: {db.status}")
                    if db.recovery_model:
                        response_parts.append(f"    Recovery Model: {db.recovery_model}")
                response_parts.append(f"    Created: {db.create_date.strftime('%Y-%m-%d %H:%M:%S')}")
                response_parts.append(f"    Collation: {db.collation_name}")
                response_parts.append("")
        
        # Summary
        response_parts.append("SUMMARY:")
        response_parts.append("-" * 10)
        response_parts.append(f"Total databases: {len(databases)}")
        response_parts.append(f"User databases: {len(user_dbs)}")
        if include_system:
            response_parts.append(f"System databases: {len(system_dbs)}")
        
        return "\n".join(response_parts)
    
    def _format_error_response(self, error_message: str) -> str:
        """Format error response."""
        return f"Error listing databases: {error_message}"


# Global tool instance
_list_databases_tool = None


def get_list_databases_tool() -> ListDatabasesTool:
    """Get the global list databases tool instance."""
    global _list_databases_tool
    if _list_databases_tool is None:
        # This will be initialized by the MCP server
        raise RuntimeError("List databases tool not initialized")
    return _list_databases_tool


def initialize_list_databases_tool(
    connection_manager: ConnectionManager, 
    schema_service: SchemaService
) -> None:
    """Initialize the global list databases tool instance."""
    global _list_databases_tool
    _list_databases_tool = ListDatabasesTool(connection_manager, schema_service)