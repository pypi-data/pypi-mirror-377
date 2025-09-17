"""
Execute Query MCP Tool for SQL Server MCP Server.

This module implements the execute_query tool that allows
executing SQL queries against SQL Server databases.
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

from ..models.query import QueryRequest, QueryParameter
from ..services.query_executor import QueryExecutor
from ..services.connection_manager import ConnectionManager
from ..lib.exceptions import QueryError, ConnectionError


logger = structlog.get_logger(__name__)


class ExecuteQueryTool:
    """MCP tool for executing SQL queries."""
    
    def __init__(self, connection_manager: ConnectionManager, query_executor: QueryExecutor):
        """Initialize the execute query tool."""
        self.connection_manager = connection_manager
        self.query_executor = query_executor
    
    def get_tool_definition(self) -> Tool:
        """Get the tool definition for MCP."""
        return Tool(
            name="execute_query",
            description="Execute a SQL query against a SQL Server database",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "SQL query to execute",
                        "minLength": 1,
                        "maxLength": 10000
                    },
                    "database": {
                        "type": "string",
                        "description": "Target database name (optional)",
                        "pattern": "^[a-zA-Z_][a-zA-Z0-9_]*$"
                    },
                    "timeout": {
                        "type": "integer",
                        "description": "Query timeout in seconds",
                        "minimum": 1,
                        "maximum": 300,
                        "default": 30
                    },
                    "parameters": {
                        "type": "array",
                        "description": "Query parameters for parameterized queries",
                        "items": {
                            "type": "object",
                            "properties": {
                                "name": {
                                    "type": "string",
                                    "description": "Parameter name"
                                },
                                "value": {
                                    "description": "Parameter value"
                                },
                                "type": {
                                    "type": "string",
                                    "description": "Parameter data type",
                                    "enum": ["string", "int", "float", "bool", "datetime"]
                                }
                            },
                            "required": ["name", "value"]
                        }
                    }
                },
                "required": ["query"]
            }
        )
    
    async def execute(
        self, 
        arguments: Dict[str, Any],
        connection_id: str
    ) -> List[TextContent]:
        """Execute the query tool."""
        try:
            # Parse and validate arguments
            query_request = self._parse_arguments(arguments)
            
            # Execute query
            result = await self.query_executor.execute_query(connection_id, query_request)
            
            # Format response
            response = self._format_response(result)
            
            return [TextContent(type="text", text=response)]
            
        except Exception as e:
            logger.error("Execute query tool failed", error=str(e))
            error_response = self._format_error_response(str(e))
            return [TextContent(type="text", text=error_response)]
    
    def _parse_arguments(self, arguments: Dict[str, Any]) -> QueryRequest:
        """Parse and validate tool arguments."""
        # Extract query
        query = arguments.get("query")
        if not query or not isinstance(query, str):
            raise ValueError("Query is required and must be a string")
        
        # Extract database
        database = arguments.get("database")
        if database and not isinstance(database, str):
            raise ValueError("Database must be a string")
        
        # Extract timeout
        timeout = arguments.get("timeout", 30)
        if not isinstance(timeout, int) or timeout < 1 or timeout > 300:
            raise ValueError("Timeout must be an integer between 1 and 300")
        
        # Extract parameters
        parameters = None
        if "parameters" in arguments:
            param_list = arguments["parameters"]
            if not isinstance(param_list, list):
                raise ValueError("Parameters must be a list")
            
            parameters = []
            for param_data in param_list:
                if not isinstance(param_data, dict):
                    raise ValueError("Each parameter must be an object")
                
                param = QueryParameter(
                    name=param_data["name"],
                    value=param_data["value"],
                    type=param_data.get("type")
                )
                parameters.append(param)
        
        return QueryRequest(
            query=query,
            database=database,
            timeout=timeout,
            parameters=parameters
        )
    
    def _format_response(self, result) -> str:
        """Format query result as text response."""
        if not result.success:
            return f"Query failed: {result.error_message}"
        
        response_parts = [
            f"Query executed successfully",
            f"Execution time: {result.execution_time_ms:.2f}ms",
            f"Rows returned: {result.row_count}",
            f"Query ID: {result.query_id}",
            ""
        ]
        
        if result.columns:
            response_parts.append("Columns:")
            for col in result.columns:
                nullable = "NULL" if col.nullable else "NOT NULL"
                response_parts.append(f"  - {col.name}: {col.type} ({nullable})")
            response_parts.append("")
        
        if result.data:
            response_parts.append("Data:")
            for i, row in enumerate(result.data[:10]):  # Limit to first 10 rows
                response_parts.append(f"Row {i+1}:")
                for key, value in row.items():
                    response_parts.append(f"  {key}: {value}")
                response_parts.append("")
            
            if len(result.data) > 10:
                response_parts.append(f"... and {len(result.data) - 10} more rows")
        else:
            response_parts.append("No data returned")
        
        return "\n".join(response_parts)
    
    def _format_error_response(self, error_message: str) -> str:
        """Format error response."""
        return f"Error executing query: {error_message}"


# Global tool instance
_execute_query_tool = None


def get_execute_query_tool() -> ExecuteQueryTool:
    """Get the global execute query tool instance."""
    global _execute_query_tool
    if _execute_query_tool is None:
        # This will be initialized by the MCP server
        raise RuntimeError("Execute query tool not initialized")
    return _execute_query_tool


def initialize_execute_query_tool(
    connection_manager: ConnectionManager, 
    query_executor: QueryExecutor
) -> None:
    """Initialize the global execute query tool instance."""
    global _execute_query_tool
    _execute_query_tool = ExecuteQueryTool(connection_manager, query_executor)