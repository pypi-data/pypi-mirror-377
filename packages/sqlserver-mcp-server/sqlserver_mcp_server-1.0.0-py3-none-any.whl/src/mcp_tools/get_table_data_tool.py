"""
Get Table Data MCP Tool for SQL Server MCP Server.

This module implements the get_table_data tool that allows
retrieving data from database tables with pagination and filtering.
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

from ..models.query import QueryResult
from ..services.data_service import DataService
from ..services.connection_manager import ConnectionManager
from ..lib.exceptions import DataError, ConnectionError


logger = structlog.get_logger(__name__)


class GetTableDataTool:
    """MCP tool for retrieving table data."""
    
    def __init__(self, connection_manager: ConnectionManager, data_service: DataService):
        """Initialize the get table data tool."""
        self.connection_manager = connection_manager
        self.data_service = data_service
    
    def get_tool_definition(self) -> Tool:
        """Get the tool definition for MCP."""
        return Tool(
            name="get_table_data",
            description="Get data from a database table with pagination and filtering options",
            inputSchema={
                "type": "object",
                "properties": {
                    "table": {
                        "type": "string",
                        "description": "Table name to retrieve data from",
                        "pattern": "^[a-zA-Z_][a-zA-Z0-9_]*$"
                    },
                    "database": {
                        "type": "string",
                        "description": "Database name (optional)",
                        "pattern": "^[a-zA-Z_][a-zA-Z0-9_]*$"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of rows to return",
                        "minimum": 1,
                        "maximum": 10000,
                        "default": 100
                    },
                    "offset": {
                        "type": "integer",
                        "description": "Number of rows to skip",
                        "minimum": 0,
                        "default": 0
                    },
                    "where_clause": {
                        "type": "string",
                        "description": "WHERE clause for filtering (without WHERE keyword)"
                    },
                    "order_by": {
                        "type": "string",
                        "description": "ORDER BY clause for sorting (without ORDER BY keyword)"
                    },
                    "columns": {
                        "type": "array",
                        "description": "Specific columns to retrieve (optional, returns all if not specified)",
                        "items": {
                            "type": "string"
                        }
                    }
                },
                "required": ["table"]
            }
        )
    
    async def execute(
        self, 
        arguments: Dict[str, Any],
        connection_id: str
    ) -> List[TextContent]:
        """Execute the get table data tool."""
        try:
            # Parse and validate arguments
            table = arguments.get("table")
            database = arguments.get("database")
            limit = arguments.get("limit", 100)
            offset = arguments.get("offset", 0)
            where_clause = arguments.get("where_clause")
            order_by = arguments.get("order_by")
            columns = arguments.get("columns")
            
            # Validate arguments
            if not table or not isinstance(table, str):
                raise ValueError("Table name is required and must be a string")
            if database and not isinstance(database, str):
                raise ValueError("Database must be a string")
            if not isinstance(limit, int) or limit < 1 or limit > 10000:
                raise ValueError("Limit must be an integer between 1 and 10000")
            if not isinstance(offset, int) or offset < 0:
                raise ValueError("Offset must be a non-negative integer")
            if where_clause and not isinstance(where_clause, str):
                raise ValueError("Where clause must be a string")
            if order_by and not isinstance(order_by, str):
                raise ValueError("Order by must be a string")
            if columns and not isinstance(columns, list):
                raise ValueError("Columns must be a list")
            
            # Get table data
            result = await self.data_service.get_table_data(
                connection_id, table, database, None, columns,
                where_clause, order_by, limit, offset
            )
            
            # Format response
            response = self._format_response(result, table, database)
            
            return [TextContent(type="text", text=response)]
            
        except Exception as e:
            logger.error("Get table data tool failed", error=str(e))
            error_response = self._format_error_response(str(e))
            return [TextContent(type="text", text=error_response)]
    
    def _format_response(self, result: QueryResult, table: str, database: Optional[str]) -> str:
        """Format table data as text response."""
        if not result.success:
            return f"Failed to retrieve data: {result.error_message}"
        
        response_parts = [
            f"Table: {table}",
            f"Database: {database or 'default'}",
            f"Execution time: {result.execution_time_ms:.2f}ms",
            f"Rows returned: {result.row_count}",
            ""
        ]
        
        # Add pagination info if available
        if hasattr(result, 'metadata') and result.metadata:
            pagination = result.metadata.get('pagination', {})
            if pagination:
                response_parts.append("PAGINATION:")
                response_parts.append(f"  Limit: {pagination.get('limit', 'N/A')}")
                response_parts.append(f"  Offset: {pagination.get('offset', 'N/A')}")
                response_parts.append(f"  Total rows: {pagination.get('total_rows', 'N/A')}")
                response_parts.append(f"  Has more: {pagination.get('has_more', 'N/A')}")
                response_parts.append("")
        
        # Column information
        if result.columns:
            response_parts.append("COLUMNS:")
            for col in result.columns:
                nullable = "NULL" if col.nullable else "NOT NULL"
                response_parts.append(f"  {col.name}: {col.type} ({nullable})")
            response_parts.append("")
        
        # Data rows
        if result.data:
            response_parts.append("DATA:")
            response_parts.append("-" * 20)
            
            # Show first few rows
            max_display_rows = 20
            display_rows = result.data[:max_display_rows]
            
            for i, row in enumerate(display_rows):
                response_parts.append(f"Row {i+1}:")
                for key, value in row.items():
                    # Truncate long values
                    str_value = str(value)
                    if len(str_value) > 100:
                        str_value = str_value[:97] + "..."
                    response_parts.append(f"  {key}: {str_value}")
                response_parts.append("")
            
            if len(result.data) > max_display_rows:
                response_parts.append(f"... and {len(result.data) - max_display_rows} more rows")
        else:
            response_parts.append("No data found")
        
        return "\n".join(response_parts)
    
    def _format_error_response(self, error_message: str) -> str:
        """Format error response."""
        return f"Error retrieving table data: {error_message}"


# Global tool instance
_get_table_data_tool = None


def get_get_table_data_tool() -> GetTableDataTool:
    """Get the global get table data tool instance."""
    global _get_table_data_tool
    if _get_table_data_tool is None:
        # This will be initialized by the MCP server
        raise RuntimeError("Get table data tool not initialized")
    return _get_table_data_tool


def initialize_get_table_data_tool(
    connection_manager: ConnectionManager, 
    data_service: DataService
) -> None:
    """Initialize the global get table data tool instance."""
    global _get_table_data_tool
    _get_table_data_tool = GetTableDataTool(connection_manager, data_service)