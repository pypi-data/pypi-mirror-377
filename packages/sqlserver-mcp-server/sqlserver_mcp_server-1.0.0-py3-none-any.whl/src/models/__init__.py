"""
Models package for SQL Server MCP Server.

This package provides Pydantic data models for the application.
"""

from .connection import ConnectionConfig, ConnectionStatus
from .query import QueryRequest, QueryResult
from .schema import (
    ColumnInfo, IndexInfo, RelationshipInfo, TableInfo, DatabaseInfo,
    SchemaMetadata
)
from .data import GetTableDataRequest, GetTableDataResult

# Create aliases for backward compatibility
Column = ColumnInfo
Index = IndexInfo
Relationship = RelationshipInfo
Table = TableInfo
Database = DatabaseInfo
SchemaRequest = SchemaMetadata
SchemaResult = SchemaMetadata

__all__ = [
    "ConnectionConfig",
    "ConnectionStatus",
    "QueryRequest",
    "QueryResult",
    "Column",
    "Index",
    "Relationship",
    "Table",
    "Database",
    "SchemaRequest",
    "SchemaResult",
    "GetTableDataRequest",
    "GetTableDataResult"
]