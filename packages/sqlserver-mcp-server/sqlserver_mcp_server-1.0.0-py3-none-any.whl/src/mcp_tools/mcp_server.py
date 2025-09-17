"""
Main MCP Server for SQL Server MCP Server.

This module implements the main MCP server that coordinates
all tools, resources, and services.
"""

import asyncio
import json
import sys
from typing import Any, Dict, List, Optional
import structlog

from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import (
    Resource, Tool, TextContent, ImageContent, EmbeddedResource,
    LoggingLevel
)

from ..services.connection_manager import ConnectionManager
from ..services.query_executor import QueryExecutor
from ..services.schema_service import SchemaService
from ..services.data_service import DataService
from ..lib.logging import setup_logging
from ..lib.exceptions import MCPError

# Import tools
from .execute_query_tool import initialize_execute_query_tool, get_execute_query_tool
from .get_schema_tool import initialize_get_schema_tool, get_get_schema_tool
from .list_databases_tool import initialize_list_databases_tool, get_list_databases_tool
from .get_table_data_tool import initialize_get_table_data_tool, get_get_table_data_tool
from .create_connection_tool import initialize_create_connection_tool, get_create_connection_tool

# Import resources
from .resources import initialize_resources, get_status_resource, get_history_resource, get_performance_resource


logger = structlog.get_logger(__name__)


class SQLServerMCPServer:
    """Main MCP Server for SQL Server operations."""
    
    def __init__(self):
        """Initialize the MCP server."""
        self.server = Server("sqlserver-mcp-server")
        self.connection_manager = ConnectionManager()
        self.query_executor = QueryExecutor(self.connection_manager)
        self.schema_service = SchemaService(self.connection_manager)
        self.data_service = DataService(self.connection_manager, self.query_executor)
        
        # Initialize tools and resources
        self._initialize_components()
        
        # Register handlers
        self._register_handlers()
    
    def _initialize_components(self):
        """Initialize all tools and resources."""
        # Initialize tools
        initialize_execute_query_tool(self.connection_manager, self.query_executor)
        initialize_get_schema_tool(self.connection_manager, self.schema_service)
        initialize_list_databases_tool(self.connection_manager, self.schema_service)
        initialize_get_table_data_tool(self.connection_manager, self.data_service)
        initialize_create_connection_tool(self.connection_manager)
        
        # Initialize resources
        initialize_resources(self.connection_manager, self.query_executor)
        
        logger.info("MCP server components initialized")
    
    def _register_handlers(self):
        """Register MCP protocol handlers."""
        
        @self.server.list_tools()
        async def handle_list_tools() -> List[Tool]:
            """List all available tools."""
            tools = [
                get_execute_query_tool().get_tool_definition(),
                get_get_schema_tool().get_tool_definition(),
                get_list_databases_tool().get_tool_definition(),
                get_get_table_data_tool().get_tool_definition(),
                get_create_connection_tool().get_tool_definition()
            ]
            return tools
        
        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
            """Handle tool calls."""
            try:
                # Route to appropriate tool
                if name == "execute_query":
                    # Extract connection_id from arguments
                    connection_id = arguments.pop("connection_id", None)
                    if not connection_id:
                        return [TextContent(type="text", text="Error: connection_id is required")]
                    
                    return await get_execute_query_tool().execute(arguments, connection_id)
                
                elif name == "get_schema":
                    # Extract connection_id from arguments
                    connection_id = arguments.pop("connection_id", None)
                    if not connection_id:
                        return [TextContent(type="text", text="Error: connection_id is required")]
                    
                    return await get_get_schema_tool().execute(arguments, connection_id)
                
                elif name == "list_databases":
                    # Extract connection_id from arguments
                    connection_id = arguments.pop("connection_id", None)
                    if not connection_id:
                        return [TextContent(type="text", text="Error: connection_id is required")]
                    
                    return await get_list_databases_tool().execute(arguments, connection_id)
                
                elif name == "get_table_data":
                    # Extract connection_id from arguments
                    connection_id = arguments.pop("connection_id", None)
                    if not connection_id:
                        return [TextContent(type="text", text="Error: connection_id is required")]
                    
                    return await get_get_table_data_tool().execute(arguments, connection_id)
                
                elif name == "create_connection":
                    return await get_create_connection_tool().execute(arguments)
                
                else:
                    return [TextContent(type="text", text=f"Unknown tool: {name}")]
                    
            except Exception as e:
                logger.error("Tool execution failed", tool=name, error=str(e))
                return [TextContent(type="text", text=f"Error executing tool {name}: {str(e)}")]
        
        @self.server.list_resources()
        async def handle_list_resources() -> List[Resource]:
            """List all available resources."""
            resources = [
                get_status_resource().get_resource_definition(),
                get_history_resource().get_resource_definition(),
                get_performance_resource().get_resource_definition()
            ]
            return resources
        
        @self.server.read_resource()
        async def handle_read_resource(uri: str) -> str:
            """Handle resource reads."""
            try:
                if uri == "sqlserver://status":
                    return await get_status_resource().get_content()
                elif uri == "sqlserver://history":
                    return await get_history_resource().get_content()
                elif uri == "sqlserver://performance":
                    return await get_performance_resource().get_content()
                else:
                    raise ValueError(f"Unknown resource: {uri}")
                    
            except Exception as e:
                logger.error("Resource read failed", uri=uri, error=str(e))
                error_data = {
                    "error": str(e),
                    "timestamp": asyncio.get_event_loop().time()
                }
                return json.dumps(error_data, indent=2)
        
        @self.server.list_prompts()
        async def handle_list_prompts() -> List[Any]:
            """List available prompts."""
            return []
        
        logger.info("MCP server handlers registered")
    
    async def run(self):
        """Run the MCP server."""
        try:
            logger.info("Starting SQL Server MCP Server")
            
            # Setup logging
            setup_logging()
            
            # Run the server
            async with stdio_server() as (read_stream, write_stream):
                await self.server.run(
                    read_stream,
                    write_stream,
                    InitializationOptions(
                        server_name="sqlserver-mcp-server",
                        server_version="1.0.0",
                        capabilities=self.server.get_capabilities(
                            notification_options=None,
                            experimental_capabilities=None
                        )
                    )
                )
                
        except Exception as e:
            logger.error("MCP server failed", error=str(e))
            raise MCPError(f"Server failed: {e}")
        finally:
            # Cleanup
            await self.connection_manager.close_all_connections()
            logger.info("MCP server shutdown complete")


async def main():
    """Main entry point for the MCP server."""
    try:
        server = SQLServerMCPServer()
        await server.run()
    except KeyboardInterrupt:
        logger.info("Server interrupted by user")
    except Exception as e:
        logger.error("Server failed", error=str(e))
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())