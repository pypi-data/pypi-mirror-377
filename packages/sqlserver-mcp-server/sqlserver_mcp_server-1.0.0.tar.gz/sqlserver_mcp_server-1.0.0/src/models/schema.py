"""
Schema models for SQL Server MCP Server.

This module defines the data models for database schema information,
including tables, columns, indexes, and relationships.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, validator


class ColumnInfo(BaseModel):
    """Information about a database column."""
    
    name: str = Field(..., description="Column name")
    data_type: str = Field(..., description="Column data type")
    max_length: Optional[int] = Field(None, ge=0, description="Maximum length for string types")
    precision: Optional[int] = Field(None, ge=0, description="Precision for numeric types")
    scale: Optional[int] = Field(None, ge=0, description="Scale for numeric types")
    is_nullable: bool = Field(..., description="Whether the column allows null values")
    is_identity: bool = Field(False, description="Whether the column is an identity column")
    default_value: Optional[str] = Field(None, description="Default value for the column")
    column_id: int = Field(..., ge=1, description="Column ID in the table")
    
    @validator('name')
    def validate_name(cls, v):
        """Validate column name."""
        if not v or not v.strip():
            raise ValueError("Column name cannot be empty")
        return v.strip()
    
    @validator('data_type')
    def validate_data_type(cls, v):
        """Validate data type."""
        if not v or not v.strip():
            raise ValueError("Data type cannot be empty")
        return v.strip()


class IndexInfo(BaseModel):
    """Information about a database index."""
    
    name: str = Field(..., description="Index name")
    type: str = Field(..., description="Index type")
    is_unique: bool = Field(..., description="Whether the index is unique")
    is_primary_key: bool = Field(..., description="Whether the index is a primary key")
    columns: List[str] = Field(..., description="Column names in the index")
    
    @validator('name')
    def validate_name(cls, v):
        """Validate index name."""
        if not v or not v.strip():
            raise ValueError("Index name cannot be empty")
        return v.strip()
    
    @validator('type')
    def validate_type(cls, v):
        """Validate index type."""
        valid_types = ["CLUSTERED", "NONCLUSTERED", "HEAP", "COLUMNSTORE"]
        if v not in valid_types:
            raise ValueError(f"Index type must be one of: {', '.join(valid_types)}")
        return v
    
    @validator('columns')
    def validate_columns(cls, v):
        """Validate column names."""
        if not v:
            raise ValueError("Index must have at least one column")
        for col in v:
            if not col or not col.strip():
                raise ValueError("Column name cannot be empty")
        return [col.strip() for col in v]


class RelationshipColumn(BaseModel):
    """Column mapping in a foreign key relationship."""
    
    column: str = Field(..., description="Local column name")
    referenced_column: str = Field(..., description="Referenced column name")
    
    @validator('column', 'referenced_column')
    def validate_column_names(cls, v):
        """Validate column names."""
        if not v or not v.strip():
            raise ValueError("Column name cannot be empty")
        return v.strip()


class RelationshipInfo(BaseModel):
    """Information about a foreign key relationship."""
    
    name: str = Field(..., description="Relationship name")
    referenced_table: str = Field(..., description="Referenced table name")
    referenced_schema: str = Field(..., description="Referenced table schema")
    columns: List[RelationshipColumn] = Field(..., description="Column mappings")
    
    @validator('name')
    def validate_name(cls, v):
        """Validate relationship name."""
        if not v or not v.strip():
            raise ValueError("Relationship name cannot be empty")
        return v.strip()
    
    @validator('referenced_table', 'referenced_schema')
    def validate_table_names(cls, v):
        """Validate table and schema names."""
        if not v or not v.strip():
            raise ValueError("Table/schema name cannot be empty")
        return v.strip()
    
    @validator('columns')
    def validate_columns(cls, v):
        """Validate column mappings."""
        if not v:
            raise ValueError("Relationship must have at least one column mapping")
        return v


class TableInfo(BaseModel):
    """Information about a database table."""
    
    name: str = Field(..., description="Table name")
    schema_name: str = Field(..., description="Table schema name")
    columns: List[ColumnInfo] = Field(default_factory=list, description="Table columns")
    indexes: List[IndexInfo] = Field(default_factory=list, description="Table indexes")
    relationships: List[RelationshipInfo] = Field(default_factory=list, description="Foreign key relationships")
    
    @validator('name', 'schema_name')
    def validate_names(cls, v):
        """Validate table and schema names."""
        if not v or not v.strip():
            raise ValueError("Table/schema name cannot be empty")
        return v.strip()
    
    def get_primary_key_columns(self) -> List[str]:
        """Get primary key column names."""
        for index in self.indexes:
            if index.is_primary_key:
                return index.columns
        return []
    
    def get_foreign_key_relationships(self) -> List[RelationshipInfo]:
        """Get foreign key relationships."""
        return [rel for rel in self.relationships]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "name": self.name,
            "schema": self.schema,
            "columns": [col.dict() for col in self.columns],
            "indexes": [idx.dict() for idx in self.indexes],
            "relationships": [rel.dict() for rel in self.relationships]
        }


class DatabaseInfo(BaseModel):
    """Information about a database."""
    
    name: str = Field(..., description="Database name")
    database_id: int = Field(..., ge=1, description="Database ID")
    create_date: datetime = Field(..., description="Database creation date")
    collation_name: str = Field(..., description="Database collation")
    is_system: bool = Field(..., description="Whether this is a system database")
    size_mb: Optional[float] = Field(None, ge=0, description="Database size in MB")
    status: Optional[str] = Field(None, description="Database status")
    recovery_model: Optional[str] = Field(None, description="Recovery model")
    
    @validator('name')
    def validate_name(cls, v):
        """Validate database name."""
        if not v or not v.strip():
            raise ValueError("Database name cannot be empty")
        return v.strip()
    
    @validator('collation_name')
    def validate_collation(cls, v):
        """Validate collation name."""
        if not v or not v.strip():
            raise ValueError("Collation name cannot be empty")
        return v.strip()
    
    @validator('status')
    def validate_status(cls, v):
        """Validate database status."""
        if v is not None:
            valid_statuses = ["ONLINE", "OFFLINE", "RESTORING", "RECOVERING", "RECOVERY_PENDING", 
                            "SUSPECT", "EMERGENCY", "SNAPSHOT", "INACCESSIBLE"]
            if v not in valid_statuses:
                raise ValueError(f"Status must be one of: {', '.join(valid_statuses)}")
        return v
    
    @validator('recovery_model')
    def validate_recovery_model(cls, v):
        """Validate recovery model."""
        if v is not None:
            valid_models = ["FULL", "BULK_LOGGED", "SIMPLE"]
            if v not in valid_models:
                raise ValueError(f"Recovery model must be one of: {', '.join(valid_models)}")
        return v
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "name": self.name,
            "database_id": self.database_id,
            "create_date": self.create_date.isoformat(),
            "collation_name": self.collation_name,
            "is_system": self.is_system,
            "size_mb": self.size_mb,
            "status": self.status,
            "recovery_model": self.recovery_model
        }


class SchemaMetadata(BaseModel):
    """Metadata for schema information."""
    
    server: Optional[str] = Field(None, description="Server name")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Schema retrieval timestamp")
    query_time_ms: float = Field(0.0, ge=0, description="Time taken to retrieve schema")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "server": self.server,
            "timestamp": self.timestamp.isoformat(),
            "query_time_ms": self.query_time_ms
        }


class DatabaseListMetadata(BaseModel):
    """Metadata for database list information."""
    
    server: Optional[str] = Field(None, description="Server name")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="List retrieval timestamp")
    total_databases: int = Field(0, ge=0, description="Total number of databases")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "server": self.server,
            "timestamp": self.timestamp.isoformat(),
            "total_databases": self.total_databases
        }


# Legacy dataclass versions for backward compatibility
@dataclass
class ColumnInfoLegacy:
    """Legacy dataclass version of ColumnInfo."""
    name: str
    data_type: str
    max_length: Optional[int]
    precision: Optional[int]
    scale: Optional[int]
    is_nullable: bool
    is_identity: bool
    default_value: Optional[str]
    column_id: int


@dataclass
class IndexInfoLegacy:
    """Legacy dataclass version of IndexInfo."""
    name: str
    type: str
    is_unique: bool
    is_primary_key: bool
    columns: List[str]


@dataclass
class RelationshipInfoLegacy:
    """Legacy dataclass version of RelationshipInfo."""
    name: str
    referenced_table: str
    referenced_schema: str
    columns: List[Dict[str, str]]


@dataclass
class TableInfoLegacy:
    """Legacy dataclass version of TableInfo."""
    name: str
    schema: str
    columns: List[ColumnInfoLegacy]
    indexes: List[IndexInfoLegacy]
    relationships: List[RelationshipInfoLegacy]


@dataclass
class DatabaseInfoLegacy:
    """Legacy dataclass version of DatabaseInfo."""
    name: str
    database_id: int
    create_date: datetime
    collation_name: str
    is_system: bool
    size_mb: float
    status: str
    recovery_model: str