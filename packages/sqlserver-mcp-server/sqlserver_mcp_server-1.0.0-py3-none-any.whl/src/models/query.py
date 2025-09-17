"""
Query models for SQL Server MCP Server.

This module defines the data models for SQL query execution,
including parameters, results, and history tracking.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field, validator
import uuid


class QueryParameter(BaseModel):
    """A parameter for a parameterized SQL query."""
    
    name: str = Field(..., min_length=1, description="Parameter name")
    value: Any = Field(..., description="Parameter value")
    type: Optional[str] = Field(None, description="Parameter data type")
    
    @validator('name')
    def validate_name(cls, v):
        """Validate parameter name."""
        if not v or not v.strip():
            raise ValueError("Parameter name cannot be empty")
        return v.strip()
    
    @validator('type')
    def validate_type(cls, v):
        """Validate parameter type."""
        if v is not None:
            valid_types = ["string", "int", "float", "bool", "datetime"]
            if v not in valid_types:
                raise ValueError(f"Parameter type must be one of: {', '.join(valid_types)}")
        return v


class QueryRequest(BaseModel):
    """Request to execute a SQL query."""
    
    query: str = Field(..., min_length=1, max_length=10000, description="SQL query to execute")
    database: Optional[str] = Field(None, description="Target database name")
    timeout: int = Field(30, ge=1, le=300, description="Query timeout in seconds")
    parameters: Optional[List[QueryParameter]] = Field(None, description="Query parameters")
    
    @validator('query')
    def validate_query(cls, v):
        """Validate SQL query."""
        if not v or not v.strip():
            raise ValueError("Query cannot be empty")
        return v.strip()
    
    @validator('database')
    def validate_database(cls, v):
        """Validate database name pattern."""
        if v is not None:
            # Pattern: ^[a-zA-Z_][a-zA-Z0-9_]*$
            if not v or not v[0].isalpha() and v[0] != '_':
                raise ValueError("Database name must start with letter or underscore")
            if not all(c.isalnum() or c == '_' for c in v):
                raise ValueError("Database name can only contain letters, numbers, and underscores")
        return v
    
    def generate_query_id(self) -> str:
        """Generate a unique query ID."""
        return f"query_{uuid.uuid4().hex[:8]}"


class ColumnInfo(BaseModel):
    """Information about a result column."""
    
    name: str = Field(..., description="Column name")
    type: str = Field(..., description="Column data type")
    nullable: bool = Field(..., description="Whether the column allows null values")
    
    @validator('name')
    def validate_name(cls, v):
        """Validate column name."""
        if not v or not v.strip():
            raise ValueError("Column name cannot be empty")
        return v.strip()


class QueryResult(BaseModel):
    """Result of a SQL query execution."""
    
    success: bool = Field(..., description="Whether the query executed successfully")
    data: List[Dict[str, Any]] = Field(default_factory=list, description="Query result data rows")
    columns: List[ColumnInfo] = Field(default_factory=list, description="Column metadata")
    row_count: int = Field(0, ge=0, description="Number of rows returned")
    execution_time_ms: float = Field(0.0, ge=0, description="Query execution time in milliseconds")
    query_id: str = Field(..., description="Unique identifier for this query execution")
    error_message: Optional[str] = Field(None, description="Error message if query failed")
    
    @validator('query_id')
    def validate_query_id(cls, v):
        """Validate query ID."""
        if not v or not v.strip():
            raise ValueError("Query ID cannot be empty")
        return v.strip()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "success": self.success,
            "data": self.data,
            "columns": [col.dict() for col in self.columns],
            "row_count": self.row_count,
            "execution_time_ms": self.execution_time_ms,
            "query_id": self.query_id,
            "error_message": self.error_message
        }


class QueryMetadata(BaseModel):
    """Metadata for a query execution."""
    
    database: Optional[str] = Field(None, description="Database name")
    server: Optional[str] = Field(None, description="Server name")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Query execution timestamp")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "database": self.database,
            "server": self.server,
            "timestamp": self.timestamp.isoformat()
        }


class QueryHistory(BaseModel):
    """Historical record of a query execution."""
    
    query_id: str = Field(..., description="Unique identifier for this query execution")
    query: str = Field(..., description="SQL query that was executed")
    database: str = Field(..., description="Database name")
    execution_time_ms: float = Field(0.0, ge=0, description="Query execution time in milliseconds")
    row_count: int = Field(0, ge=0, description="Number of rows returned")
    status: str = Field(..., description="Query execution status")
    error_message: Optional[str] = Field(None, description="Error message if query failed")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Query execution timestamp")
    parameters: List[QueryParameter] = Field(default_factory=list, description="Query parameters used")
    
    @validator('status')
    def validate_status(cls, v):
        """Validate query status."""
        valid_statuses = ["success", "error", "timeout"]
        if v not in valid_statuses:
            raise ValueError(f"Status must be one of: {', '.join(valid_statuses)}")
        return v
    
    @validator('query_id')
    def validate_query_id(cls, v):
        """Validate query ID."""
        if not v or not v.strip():
            raise ValueError("Query ID cannot be empty")
        return v.strip()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "query_id": self.query_id,
            "query": self.query,
            "database": self.database,
            "execution_time_ms": self.execution_time_ms,
            "row_count": self.row_count,
            "status": self.status,
            "error_message": self.error_message,
            "timestamp": self.timestamp.isoformat(),
            "parameters": [param.dict() for param in self.parameters]
        }


class QueryStatistics(BaseModel):
    """Statistics for query execution history."""
    
    total_queries: int = Field(0, ge=0, description="Total number of queries executed")
    successful_queries: int = Field(0, ge=0, description="Number of successful queries")
    failed_queries: int = Field(0, ge=0, description="Number of failed queries")
    average_execution_time_ms: float = Field(0.0, ge=0, description="Average execution time in milliseconds")
    total_execution_time_ms: float = Field(0.0, ge=0, description="Total execution time in milliseconds")
    
    def calculate_success_rate(self) -> float:
        """Calculate the success rate as a percentage."""
        if self.total_queries == 0:
            return 0.0
        return (self.successful_queries / self.total_queries) * 100.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "total_queries": self.total_queries,
            "successful_queries": self.successful_queries,
            "failed_queries": self.failed_queries,
            "average_execution_time_ms": self.average_execution_time_ms,
            "total_execution_time_ms": self.total_execution_time_ms,
            "success_rate_percent": self.calculate_success_rate()
        }


# Legacy dataclass versions for backward compatibility
@dataclass
class QueryParameterLegacy:
    """Legacy dataclass version of QueryParameter."""
    name: str
    value: Any
    type: str


@dataclass
class QueryRequestLegacy:
    """Legacy dataclass version of QueryRequest."""
    query: str
    database: Optional[str] = None
    timeout: int = 30
    parameters: Optional[List[QueryParameterLegacy]] = None


@dataclass
class QueryResultLegacy:
    """Legacy dataclass version of QueryResult."""
    success: bool
    data: List[Dict[str, Any]]
    columns: List[Dict[str, Any]]
    row_count: int
    execution_time_ms: float
    query_id: str
    error_message: Optional[str] = None


@dataclass
class QueryHistoryLegacy:
    """Legacy dataclass version of QueryHistory."""
    query_id: str
    query: str
    database: str
    execution_time_ms: float
    row_count: int
    status: str
    error_message: Optional[str]
    timestamp: datetime
    parameters: List[QueryParameterLegacy]