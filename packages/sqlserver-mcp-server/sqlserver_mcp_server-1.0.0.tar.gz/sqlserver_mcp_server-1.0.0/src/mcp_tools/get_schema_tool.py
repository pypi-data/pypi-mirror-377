"""
Get Schema MCP Tool for SQL Server MCP Server.

This module implements the get_schema tool that allows
retrieving database schema information.
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

from ..models.schema import TableInfo
from ..services.schema_service import SchemaService
from ..services.connection_manager import ConnectionManager
from ..lib.exceptions import SchemaError, ConnectionError


logger = structlog.get_logger(__name__)


class GetSchemaTool:
    """MCP tool for retrieving database schema information."""
    
    def __init__(self, connection_manager: ConnectionManager, schema_service: SchemaService):
        """Initialize the get schema tool."""
        self.connection_manager = connection_manager
        self.schema_service = schema_service
    
    def get_tool_definition(self) -> Tool:
        """Get the tool definition for MCP."""
        return Tool(
            name="get_schema",
            description="Get database schema information including tables, columns, indexes, and relationships",
            inputSchema={
                "type": "object",
                "properties": {
                    "database": {
                        "type": "string",
                        "description": "Database name (optional, uses default if not specified)",
                        "pattern": "^[a-zA-Z_][a-zA-Z0-9_]*$"
                    },
                    "table": {
                        "type": "string",
                        "description": "Specific table name to get schema for (optional)",
                        "pattern": "^[a-zA-Z_][a-zA-Z0-9_]*$"
                    },
                    "include_relationships": {
                        "type": "boolean",
                        "description": "Include foreign key relationships",
                        "default": True
                    },
                    "include_indexes": {
                        "type": "boolean",
                        "description": "Include index information",
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
        """Execute the get schema tool."""
        try:
            # Parse and validate arguments
            database = arguments.get("database")
            table = arguments.get("table")
            include_relationships = arguments.get("include_relationships", True)
            include_indexes = arguments.get("include_indexes", True)
            
            # Validate arguments
            if database and not isinstance(database, str):
                raise ValueError("Database must be a string")
            if table and not isinstance(table, str):
                raise ValueError("Table must be a string")
            if not isinstance(include_relationships, bool):
                raise ValueError("include_relationships must be a boolean")
            if not isinstance(include_indexes, bool):
                raise ValueError("include_indexes must be a boolean")
            
            # Get schema information
            if table:
                # Get specific table schema
                table_info = await self.schema_service.get_table_schema(
                    connection_id, table, database, include_indexes=include_indexes,
                    include_relationships=include_relationships
                )
                response = self._format_table_schema_response(table_info)
            else:
                # Get all tables
                tables = await self.schema_service.get_table_list(
                    connection_id, database
                )
                response = self._format_table_list_response(tables)
            
            return [TextContent(type="text", text=response)]
            
        except Exception as e:
            logger.error("Get schema tool failed", error=str(e))
            error_response = self._format_error_response(str(e))
            return [TextContent(type="text", text=error_response)]
    
    def _format_table_schema_response(self, table_info: TableInfo) -> str:
        """Format table schema information as text response."""
        response_parts = [
            f"Table: {table_info.schema}.{table_info.name}",
            "=" * 50,
            ""
        ]
        
        # Columns
        response_parts.append("COLUMNS:")
        response_parts.append("-" * 20)
        for col in table_info.columns:
            nullable = "NULL" if col.is_nullable else "NOT NULL"
            identity = " IDENTITY" if col.is_identity else ""
            default = f" DEFAULT {col.default_value}" if col.default_value else ""
            
            type_info = col.data_type
            if col.max_length and col.max_length != -1:
                type_info += f"({col.max_length})"
            elif col.precision and col.scale is not None:
                type_info += f"({col.precision},{col.scale})"
            elif col.precision:
                type_info += f"({col.precision})"
            
            response_parts.append(f"  {col.name}: {type_info} {nullable}{identity}{default}")
        response_parts.append("")
        
        # Indexes
        if table_info.indexes:
            response_parts.append("INDEXES:")
            response_parts.append("-" * 20)
            for idx in table_info.indexes:
                pk = " (PRIMARY KEY)" if idx.is_primary_key else ""
                unique = " UNIQUE" if idx.is_unique else ""
                response_parts.append(f"  {idx.name}: {idx.type}{unique}{pk}")
                response_parts.append(f"    Columns: {', '.join(idx.columns)}")
            response_parts.append("")
        
        # Relationships
        if table_info.relationships:
            response_parts.append("FOREIGN KEY RELATIONSHIPS:")
            response_parts.append("-" * 30)
            for rel in table_info.relationships:
                response_parts.append(f"  {rel.name}:")
                response_parts.append(f"    References: {rel.referenced_schema}.{rel.referenced_table}")
                for col_mapping in rel.columns:
                    response_parts.append(f"    {col_mapping.column} -> {col_mapping.referenced_column}")
            response_parts.append("")
        
        return "\n".join(response_parts)
    
    def _format_table_list_response(self, tables: List[TableInfo]) -> str:
        """Format table list as text response."""
        if not tables:
            return "No tables found in the database."
        
        response_parts = [
            f"Found {len(tables)} tables:",
            "=" * 30,
            ""
        ]
        
        # Group by schema
        schemas = {}
        for table in tables:
            if table.schema not in schemas:
                schemas[table.schema] = []
            schemas[table.schema].append(table)
        
        for schema_name, schema_tables in schemas.items():
            response_parts.append(f"Schema: {schema_name}")
            response_parts.append("-" * 20)
            for table in schema_tables:
                column_count = len(table.columns)
                response_parts.append(f"  {table.name} ({column_count} columns)")
            response_parts.append("")
        
        return "\n".join(response_parts)
    
    def _format_error_response(self, error_message: str) -> str:
        """Format error response."""
        return f"Error retrieving schema: {error_message}"


# Global tool instance
_get_schema_tool = None


def get_get_schema_tool() -> GetSchemaTool:
    """Get the global get schema tool instance."""
    global _get_schema_tool
    if _get_schema_tool is None:
        # This will be initialized by the MCP server
        raise RuntimeError("Get schema tool not initialized")
    return _get_schema_tool


def initialize_get_schema_tool(
    connection_manager: ConnectionManager, 
    schema_service: SchemaService
) -> None:
    """Initialize the global get schema tool instance."""
    global _get_schema_tool
    _get_schema_tool = GetSchemaTool(connection_manager, schema_service)