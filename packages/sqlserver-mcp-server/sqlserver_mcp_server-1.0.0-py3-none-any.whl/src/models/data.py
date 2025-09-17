"""
Data models for SQL Server MCP Server.

This module defines the data models for table data retrieval,
including pagination, filtering, and result formatting.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, validator


class GetTableDataRequest(BaseModel):
    """Request model for getting table data."""
    
    table_name: str = Field(..., min_length=1, description="Name of the table")
    schema_name: Optional[str] = Field(None, description="Schema name (defaults to 'dbo')")
    database: Optional[str] = Field(None, description="Database name")
    limit: int = Field(100, ge=1, le=10000, description="Maximum number of rows to return")
    offset: int = Field(0, ge=0, description="Number of rows to skip")
    columns: Optional[List[str]] = Field(None, description="Specific columns to retrieve")
    where_clause: Optional[str] = Field(None, description="WHERE clause for filtering")
    order_by: Optional[str] = Field(None, description="ORDER BY clause for sorting")
    
    @validator('table_name')
    def validate_table_name(cls, v):
        """Validate table name."""
        if not v or not v.strip():
            raise ValueError("Table name cannot be empty")
        return v.strip()
    
    @validator('schema_name')
    def validate_schema_name(cls, v):
        """Validate schema name."""
        if v is not None and not v.strip():
            raise ValueError("Schema name cannot be empty")
        return v.strip() if v else None
    
    @validator('columns')
    def validate_columns(cls, v):
        """Validate column names."""
        if v is not None:
            for col in v:
                if not col or not col.strip():
                    raise ValueError("Column name cannot be empty")
        return v


class ColumnData(BaseModel):
    """Information about a column in the result set."""
    
    name: str = Field(..., description="Column name")
    data_type: str = Field(..., description="Column data type")
    value: Any = Field(..., description="Column value")
    is_null: bool = Field(False, description="Whether the value is NULL")


class RowData(BaseModel):
    """A single row of data."""
    
    columns: List[ColumnData] = Field(..., description="Column data for this row")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert row to dictionary."""
        return {col.name: col.value for col in self.columns}


class GetTableDataResult(BaseModel):
    """Result model for getting table data."""
    
    success: bool = Field(..., description="Whether the operation was successful")
    data: List[RowData] = Field(default_factory=list, description="Table data rows")
    columns: List[ColumnData] = Field(default_factory=list, description="Column information")
    total_rows: int = Field(0, ge=0, description="Total number of rows in the table")
    returned_rows: int = Field(0, ge=0, description="Number of rows returned")
    execution_time_ms: float = Field(0.0, ge=0, description="Query execution time in milliseconds")
    query_id: str = Field(..., description="Unique query identifier")
    error_message: Optional[str] = Field(None, description="Error message if operation failed")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    
    @validator('query_id')
    def validate_query_id(cls, v):
        """Validate query ID."""
        if not v or not v.strip():
            raise ValueError("Query ID cannot be empty")
        return v.strip()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary."""
        return {
            "success": self.success,
            "data": [row.to_dict() for row in self.data],
            "columns": [
                {
                    "name": col.name,
                    "data_type": col.data_type,
                    "is_null": col.is_null
                }
                for col in self.columns
            ],
            "total_rows": self.total_rows,
            "returned_rows": self.returned_rows,
            "execution_time_ms": self.execution_time_ms,
            "query_id": self.query_id,
            "error_message": self.error_message,
            "metadata": self.metadata
        }


class TableDataMetadata(BaseModel):
    """Metadata for table data operations."""
    
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Operation timestamp")
    table_name: str = Field(..., description="Table name")
    schema_name: Optional[str] = Field(None, description="Schema name")
    database: Optional[str] = Field(None, description="Database name")
    server: Optional[str] = Field(None, description="Server name")
    connection_id: Optional[str] = Field(None, description="Connection ID used")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert metadata to dictionary."""
        return {
            "timestamp": self.timestamp.isoformat(),
            "table_name": self.table_name,
            "schema_name": self.schema_name,
            "database": self.database,
            "server": self.server,
            "connection_id": self.connection_id
        }


# Legacy dataclass versions for backward compatibility
from dataclasses import dataclass


@dataclass
class GetTableDataRequestLegacy:
    """Legacy dataclass version of GetTableDataRequest."""
    table_name: str
    schema_name: Optional[str] = None
    database: Optional[str] = None
    limit: int = 100
    offset: int = 0
    columns: Optional[List[str]] = None
    where_clause: Optional[str] = None
    order_by: Optional[str] = None


@dataclass
class GetTableDataResultLegacy:
    """Legacy dataclass version of GetTableDataResult."""
    success: bool
    data: List[Dict[str, Any]]
    columns: List[Dict[str, Any]]
    total_rows: int
    returned_rows: int
    execution_time_ms: float
    query_id: str
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = None
