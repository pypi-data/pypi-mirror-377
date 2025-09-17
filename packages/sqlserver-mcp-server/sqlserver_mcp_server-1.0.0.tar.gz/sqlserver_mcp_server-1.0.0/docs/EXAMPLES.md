# SQL Server MCP Server - Examples

This document provides comprehensive examples of using the SQL Server MCP Server, including MCP tools, CLI commands, and integration scenarios.

## Table of Contents

- [MCP Tools Examples](#mcp-tools-examples)
- [CLI Examples](#cli-examples)
- [Integration Examples](#integration-examples)
- [Advanced Usage](#advanced-usage)
- [Error Handling Examples](#error-handling-examples)
- [Performance Examples](#performance-examples)

## MCP Tools Examples

### Create Connection

```json
{
  "name": "create_connection",
  "arguments": {
    "server": "localhost",
    "database": "master",
    "authentication": "windows",
    "connection_timeout": 30,
    "pool_size": 5
  }
}
```

**Response:**
```json
{
  "connection_id": "123e4567-e89b-12d3-a456-426614174000",
  "status": "connected",
  "message": "Connection established successfully",
  "active_connections": 1,
  "connection_time_ms": 150
}
```

### Execute Query

```json
{
  "name": "execute_query",
  "arguments": {
    "connection_id": "123e4567-e89b-12d3-a456-426614174000",
    "query": "SELECT name, type_desc FROM sys.objects WHERE type = 'U'",
    "database": "master",
    "output_format": "json"
  }
}
```

**Response:**
```json
{
  "query_id": "456e7890-e89b-12d3-a456-426614174001",
  "status": "success",
  "rows_affected": 0,
  "data": [
    {"name": "Users", "type_desc": "USER_TABLE"},
    {"name": "Orders", "type_desc": "USER_TABLE"}
  ],
  "columns": ["name", "type_desc"],
  "message": "Query executed successfully",
  "execution_time_ms": 25
}
```

### Get Schema

```json
{
  "name": "get_schema",
  "arguments": {
    "connection_id": "123e4567-e89b-12d3-a456-426614174000",
    "database": "master",
    "table_name": "sys.objects",
    "include_columns": true,
    "include_indexes": true,
    "include_relationships": true
  }
}
```

**Response:**
```json
{
  "schema_id": "789e0123-e89b-12d3-a456-426614174002",
  "status": "success",
  "database_name": "master",
  "tables": [
    {
      "name": "sys.objects",
      "columns": [
        {
          "name": "name",
          "data_type": "nvarchar",
          "max_length": 128,
          "is_nullable": false,
          "is_primary_key": false
        }
      ],
      "indexes": [
        {
          "name": "PK__objects__3213E83F",
          "type": "CLUSTERED",
          "columns": ["object_id"]
        }
      ],
      "relationships": []
    }
  ],
  "message": "Schema retrieved successfully",
  "retrieval_time_ms": 45
}
```

### Get Table Data

```json
{
  "name": "get_table_data",
  "arguments": {
    "connection_id": "123e4567-e89b-12d3-a456-426614174000",
    "database": "master",
    "table_name": "sys.tables",
    "limit": 10,
    "output_format": "json"
  }
}
```

**Response:**
```json
{
  "data_id": "012e3456-e89b-12d3-a456-426614174003",
  "status": "success",
  "database_name": "master",
  "table_name": "sys.tables",
  "total_rows": 5,
  "returned_rows": 5,
  "data": [
    {"name": "Users", "object_id": 1},
    {"name": "Orders", "object_id": 2}
  ],
  "columns": ["name", "object_id"],
  "message": "Data retrieved successfully",
  "retrieval_time_ms": 30
}
```

### List Databases

```json
{
  "name": "list_databases",
  "arguments": {
    "connection_id": "123e4567-e89b-12d3-a456-426614174000",
    "include_system_databases": false,
    "include_metadata": true
  }
}
```

**Response:**
```json
{
  "status": "success",
  "databases": [
    {
      "name": "master",
      "size_mb": 10.5,
      "created_date": "2023-01-01T00:00:00Z"
    },
    {
      "name": "tempdb",
      "size_mb": 5.2,
      "created_date": "2023-01-01T00:00:00Z"
    }
  ],
  "message": "Databases listed successfully"
}
```

## CLI Examples

### Connection Management

```bash
# Connect to database
python -m src.cli connection connect \
  --server "localhost" \
  --database "master" \
  --trusted-connection

# List active connections
python -m src.cli connection list

# Check connection status
python -m src.cli connection status \
  --connection-id "123e4567-e89b-12d3-a456-426614174000"

# Close connection
python -m src.cli connection close \
  "123e4567-e89b-12d3-a456-426614174000"
```

### Query Execution

```bash
# Execute simple query
python -m src.cli query execute \
  "123e4567-e89b-12d3-a456-426614174000" \
  "SELECT COUNT(*) FROM sys.tables"

# Execute query with parameters
python -m src.cli query execute \
  "123e4567-e89b-12d3-a456-426614174000" \
  "SELECT * FROM sys.objects WHERE type = ?" \
  --parameters "U"

# Execute query with output format
python -m src.cli query execute \
  "123e4567-e89b-12d3-a456-426614174000" \
  "SELECT * FROM sys.tables" \
  --output json

# Get sample data
python -m src.cli query sample \
  "123e4567-e89b-12d3-a456-426614174000" \
  "master" \
  --table "sys.tables" \
  --limit 10
```

### Schema Inspection

```bash
# List all tables in database
python -m src.cli schema tables \
  "123e4567-e89b-12d3-a456-426614174000" \
  "master"

# Get table columns
python -m src.cli schema columns \
  "123e4567-e89b-12d3-a456-426614174000" \
  "master" \
  "sys.tables"

# Get table indexes
python -m src.cli schema indexes \
  "123e4567-e89b-12d3-a456-426614174000" \
  "master" \
  "sys.tables"

# Get table relationships
python -m src.cli schema relationships \
  "123e4567-e89b-12d3-a456-426614174000" \
  "master" \
  "sys.tables"

# Full schema inspection
python -m src.cli schema inspect \
  "123e4567-e89b-12d3-a456-426614174000" \
  "master" \
  --include-indexes \
  --include-relationships
```

### Configuration Management

```bash
# Show current configuration
python -m src.cli config show

# Set configuration value
python -m src.cli config set log_level DEBUG

# Get configuration value
python -m src.cli config get log_level

# Reset to defaults
python -m src.cli config reset

# Import configuration
python -m src.cli config import-config config.json

# Export configuration
python -m src.cli config export-config my-config.json
```

## Python Library Examples

### Basic Usage

```python
from src.services.connection_manager import ConnectionManager
from src.services.query_executor import QueryExecutor

# Create connection
conn_manager = ConnectionManager()
connection_id = conn_manager.create_connection({
    "server": "localhost",
    "database": "master",
    "authentication": "windows"
})

# Execute query
query_executor = QueryExecutor(conn_manager)
result = query_executor.execute_query(
    connection_id=connection_id,
    query="SELECT * FROM sys.tables",
    output_format="json"
)

print(result.data)
```

### Advanced Usage

```python
from src.services.schema_service import SchemaService
from src.services.data_service import DataService

# Get schema information
schema_service = SchemaService(conn_manager)
schema = schema_service.get_schema(
    connection_id=connection_id,
    database="master",
    include_columns=True,
    include_indexes=True
)

# Get table data
data_service = DataService(conn_manager)
data = data_service.get_table_data(
    connection_id=connection_id,
    database="master",
    table_name="sys.tables",
    limit=100,
    output_format="json"
)

print(f"Found {len(schema.tables)} tables")
print(f"Retrieved {len(data.data)} rows")
```

### Error Handling

```python
from src.lib.exceptions import ConnectionError, QueryError

try:
    connection_id = conn_manager.create_connection({
        "server": "invalid-server",
        "database": "master"
    })
except ConnectionError as e:
    print(f"Connection failed: {e.message}")

try:
    result = query_executor.execute_query(
        connection_id=connection_id,
        query="INVALID SQL QUERY"
    )
except QueryError as e:
    print(f"Query failed: {e.message}")
```

## Configuration Examples

### Environment Variables

```bash
# Logging configuration
export SQLSERVER_MCP_LOG_LEVEL=DEBUG
export SQLSERVER_MCP_LOG_FORMAT=json

# Server configuration
export SQLSERVER_MCP_SERVER_HOST=0.0.0.0
export SQLSERVER_MCP_SERVER_PORT=8000

# Database defaults
export SQLSERVER_MCP_DEFAULT_TIMEOUT=60
export SQLSERVER_MCP_DEFAULT_POOL_SIZE=20
export SQLSERVER_MCP_DEFAULT_ENCRYPT=true
```

### Configuration File

```json
{
  "log_level": "INFO",
  "log_format": "json",
  "default_timeout": 30,
  "default_pool_size": 10,
  "default_encrypt": true,
  "default_trusted_connection": true,
  "output_format": "table",
  "max_rows": 1000,
  "page_size": 100,
  "server": {
    "host": "127.0.0.1",
    "port": 8000,
    "max_connections": 100
  },
  "database": {
    "connection_timeout": 30,
    "command_timeout": 30,
    "pool_size": 10
  }
}
```

## Common Use Cases

### Database Migration

```python
# Get source schema
source_schema = schema_service.get_schema(
    connection_id=source_connection,
    database="source_db",
    include_columns=True,
    include_indexes=True
)

# Get target schema
target_schema = schema_service.get_schema(
    connection_id=target_connection,
    database="target_db",
    include_columns=True,
    include_indexes=True
)

# Compare schemas
# Generate migration scripts
```

### Data Analysis

```python
# Get table statistics
tables = schema_service.get_schema(
    connection_id=connection_id,
    database="analytics_db",
    include_row_counts=True,
    include_data_sizes=True
)

# Analyze large tables
large_tables = [t for t in tables.tables if t.row_count > 1000000]

# Get sample data from large tables
for table in large_tables:
    sample = data_service.get_table_data(
        connection_id=connection_id,
        database="analytics_db",
        table_name=table.name,
        limit=1000
    )
    # Analyze sample data
```

### Monitoring

```python
# Check connection health
status = conn_manager.get_connection_status(connection_id)
if status.status != "connected":
    # Handle connection issues
    pass

# Monitor query performance
result = query_executor.execute_query(
    connection_id=connection_id,
    query="SELECT * FROM large_table",
    timeout=300
)

if result.execution_time_ms > 10000:
    # Log slow query
    pass
```
