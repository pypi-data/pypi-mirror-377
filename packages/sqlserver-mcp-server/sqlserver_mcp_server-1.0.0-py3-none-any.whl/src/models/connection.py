"""
Connection models for SQL Server MCP Server.

This module defines the data models for managing database connections,
including configuration, status, and health monitoring.
"""

from dataclasses import dataclass, field
from typing import Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, validator


class ConnectionConfig(BaseModel):
    """Configuration for a database connection."""
    
    server: str = Field(..., min_length=1, description="SQL Server instance name or IP")
    database: Optional[str] = Field(None, description="Default database name")
    username: Optional[str] = Field(None, description="SQL Server username (if not using Windows Auth)")
    password: Optional[str] = Field(None, description="SQL Server password (if not using Windows Auth)")
    trusted_connection: bool = Field(True, description="Use Windows Authentication")
    encrypt: bool = Field(True, description="Encrypt connection")
    connection_timeout: int = Field(30, ge=1, le=60, description="Connection timeout in seconds")
    pool_size: int = Field(10, ge=1, le=50, description="Connection pool size")
    
    @validator('server')
    def validate_server(cls, v):
        """Validate server parameter."""
        if not v or not v.strip():
            raise ValueError("Server cannot be empty")
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
    
    def to_connection_string(self) -> str:
        """Convert configuration to ODBC connection string."""
        parts = [
            f"Driver={{ODBC Driver 17 for SQL Server}}",
            f"Server={self.server}",
        ]
        
        if self.database:
            parts.append(f"Database={self.database}")
        
        if self.trusted_connection:
            parts.append("Trusted_Connection=yes")
        else:
            if self.username:
                parts.append(f"User Id={self.username}")
            if self.password:
                parts.append(f"Password={self.password}")
        
        if self.encrypt:
            parts.append("Encrypt=yes")
        
        parts.extend([
            f"Connection Timeout={self.connection_timeout}",
            "Pooling=true",
            f"Min Pool Size=1",
            f"Max Pool Size={self.pool_size}",
        ])
        
        return ";".join(parts)


class ConnectionStatus(BaseModel):
    """Status information for a database connection."""
    
    connection_id: str = Field(..., description="Unique connection identifier")
    connected: bool = Field(..., description="Whether the connection is active")
    server: str = Field(..., description="Server name")
    database: Optional[str] = Field(None, description="Database name")
    authentication_method: str = Field(..., description="Authentication method used")
    last_activity: datetime = Field(default_factory=datetime.utcnow, description="Last activity timestamp")
    pool_status: Dict[str, int] = Field(default_factory=dict, description="Connection pool status")
    response_time_ms: float = Field(0.0, ge=0, description="Response time in milliseconds")
    last_error: Optional[str] = Field(None, description="Last error message")
    error_count: int = Field(0, ge=0, description="Number of errors")
    uptime_seconds: float = Field(0.0, ge=0, description="Connection uptime in seconds")
    
    @validator('connection_id')
    def validate_connection_id(cls, v):
        """Validate connection ID format."""
        if not v or not v.strip():
            raise ValueError("Connection ID cannot be empty")
        return v.strip()
    
    @validator('authentication_method')
    def validate_authentication_method(cls, v):
        """Validate authentication method."""
        valid_methods = [
            "Windows Authentication",
            "SQL Server Authentication", 
            "Azure Active Directory"
        ]
        if v not in valid_methods:
            raise ValueError(f"Authentication method must be one of: {', '.join(valid_methods)}")
        return v
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "connection_id": self.connection_id,
            "connected": self.connected,
            "server": self.server,
            "database": self.database,
            "authentication_method": self.authentication_method,
            "last_activity": self.last_activity.isoformat(),
            "pool_status": self.pool_status,
            "response_time_ms": self.response_time_ms,
            "last_error": self.last_error,
            "error_count": self.error_count,
            "uptime_seconds": self.uptime_seconds
        }


class ConnectionHealth(BaseModel):
    """Health information for a database connection."""
    
    response_time_ms: float = Field(0.0, ge=0, description="Response time in milliseconds")
    last_error: Optional[str] = Field(None, description="Last error message")
    error_count: int = Field(0, ge=0, description="Number of errors")
    uptime_seconds: float = Field(0.0, ge=0, description="Connection uptime in seconds")
    
    def is_healthy(self, max_response_time_ms: float = 1000.0, max_error_count: int = 10) -> bool:
        """Check if connection is healthy based on thresholds."""
        return (
            self.response_time_ms <= max_response_time_ms and
            self.error_count <= max_error_count
        )


class ConnectionMetadata(BaseModel):
    """Metadata for a database connection."""
    
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Connection creation timestamp")
    server_version: Optional[str] = Field(None, description="SQL Server version")
    driver_version: Optional[str] = Field(None, description="Driver version")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "timestamp": self.timestamp.isoformat(),
            "server_version": self.server_version,
            "driver_version": self.driver_version
        }


# Legacy dataclass versions for backward compatibility
@dataclass
class ConnectionConfigLegacy:
    """Legacy dataclass version of ConnectionConfig."""
    server: str
    database: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
    trusted_connection: bool = True
    encrypt: bool = True
    connection_timeout: int = 30
    pool_size: int = 10


@dataclass
class ConnectionStatusLegacy:
    """Legacy dataclass version of ConnectionStatus."""
    connection_id: str
    connected: bool
    server: str
    database: Optional[str]
    authentication_method: str
    last_activity: datetime
    pool_status: Dict[str, int]
    response_time_ms: float
    last_error: Optional[str]
    error_count: int
    uptime_seconds: float