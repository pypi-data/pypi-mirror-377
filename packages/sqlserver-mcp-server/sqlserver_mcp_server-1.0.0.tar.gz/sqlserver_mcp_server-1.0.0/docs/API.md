# API Reference

This document provides comprehensive documentation for the SQL Server MCP Server API, including all MCP tools, resources, and data models.

## Table of Contents

- [MCP Tools](#mcp-tools)
  - [create_connection](#create_connection)
  - [execute_query](#execute_query)
  - [get_schema](#get_schema)
  - [get_table_data](#get_table_data)
  - [list_databases](#list_databases)
- [MCP Resources](#mcp-resources)
  - [connection_status](#connection_status)
  - [query_history](#query_history)
- [Data Models](#data-models)
- [Error Handling](#error-handling)
- [Examples](#examples)

## MCP Tools

### create_connection

Creates a new database connection with connection pooling support.

**Tool Name:** `create_connection`

**Description:** Establishes a secure connection to a SQL Server instance with configurable authentication and connection parameters.

**Parameters:**
- `server` (string, required): SQL Server instance name, IP address, or FQDN
- `database` (string, optional): Target database name (defaults to "master")
- `username` (string, optional): Username for SQL Server authentication
- `password` (string, optional): Password for SQL Server authentication
- `trusted_connection` (boolean, optional): Use Windows authentication (default: true)
- `connection_timeout` (integer, optional): Connection timeout in seconds (default: 30)
- `pool_size` (integer, optional): Connection pool size (default: 5)
- `encrypt` (boolean, optional): Enable encryption (default: true)
- `trust_server_certificate` (boolean, optional): Trust server certificate (default: false)

**Returns:**
- `connection_id` (string): Unique connection identifier for subsequent operations
- `status` (string): Connection status ("connected", "disconnected", "error")
- `message` (string, optional): Status message or error details
- `active_connections` (integer): Number of active connections in the pool
- `connection_time_ms` (integer, optional): Connection establishment time in milliseconds
- `server_info` (object, optional): Server information including version and capabilities

**Example:**
```json
{
  "server": "localhost",
  "database": "AdventureWorks",
  "trusted_connection": true,
  "connection_timeout": 30,
  "pool_size": 10
}
```

**Response:**
```json
{
  "connection_id": "conn_12345",
  "status": "connected",
  "message": "Connection established successfully",
  "active_connections": 1,
  "connection_time_ms": 45,
  "server_info": {
    "version": "15.0.2000.5",
    "edition": "Developer Edition"
  }
}
```

### execute_query

Executes a SQL query with support for parameterized queries and multiple output formats.

**Tool Name:** `execute_query`

**Description:** Executes SQL queries against the connected database with comprehensive error handling, parameter binding, and result formatting.

**Parameters:**
- `connection_id` (string, required): Connection identifier from create_connection
- `query` (string, required): SQL query to execute
- `database` (string, optional): Target database (overrides connection default)
- `parameters` (array, optional): Query parameters for parameterized queries
  - `name` (string): Parameter name (e.g., "@user_id")
  - `value` (any): Parameter value
  - `type` (string, optional): SQL data type ("int", "varchar", "datetime", etc.)
- `timeout` (integer, optional): Query timeout in seconds (default: 30)
- `output_format` (string, optional): Output format ("json", "csv", "table", "list", default: "json")
- `include_metadata` (boolean, optional): Include column metadata in results (default: true)

**Returns:**
- `query_id` (string): Unique query identifier for tracking
- `status` (string): Execution status ("success", "error", "timeout")
- `rows_affected` (integer, optional): Number of rows affected (for INSERT/UPDATE/DELETE)
- `data` (array, optional): Query result data
- `columns` (array, optional): Column information including name, type, and metadata
- `message` (string, optional): Status or error message
- `execution_time_ms` (integer, optional): Query execution time in milliseconds
- `query_plan` (object, optional): Query execution plan (if available)

**Example:**
```json
{
  "connection_id": "conn_12345",
  "query": "SELECT * FROM Person.Person WHERE BusinessEntityID = @id",
  "database": "AdventureWorks",
  "parameters": [
    {
      "name": "@id",
      "value": 1,
      "type": "int"
    }
  ],
  "timeout": 30,
  "output_format": "json"
}
```

**Response:**
```json
{
  "query_id": "query_67890",
  "status": "success",
  "rows_affected": 1,
  "data": [
    {
      "BusinessEntityID": 1,
      "PersonType": "EM",
      "NameStyle": false,
      "Title": null,
      "FirstName": "Ken",
      "MiddleName": "J",
      "LastName": "Sánchez"
    }
  ],
  "columns": [
    {
      "name": "BusinessEntityID",
      "type": "int",
      "nullable": false,
      "max_length": 4
    },
    {
      "name": "FirstName",
      "type": "nvarchar",
      "nullable": false,
      "max_length": 50
    }
  ],
  "message": "Query executed successfully",
  "execution_time_ms": 15
}
```

### get_schema

Retrieves database schema information.

**Parameters:**
- `connection_id` (string, required): Connection identifier
- `database` (string, required): Database name
- `table_name` (string, optional): Specific table name
- `include_columns` (boolean, optional): Include column details (default: true)
- `include_indexes` (boolean, optional): Include index details (default: false)
- `include_relationships` (boolean, optional): Include relationship details (default: false)
- `include_row_counts` (boolean, optional): Include row counts (default: false)
- `include_data_sizes` (boolean, optional): Include data sizes (default: false)

**Returns:**
- `schema_id` (string): Unique schema identifier
- `status` (string): Retrieval status ("success", "error")
- `database_name` (string): Database name
- `tables` (array): Table information
- `message` (string, optional): Status or error message
- `retrieval_time_ms` (integer, optional): Schema retrieval time

### get_table_data

Retrieves data from a specific table.

**Parameters:**
- `connection_id` (string, required): Connection identifier
- `database` (string, required): Database name
- `table_name` (string, required): Table name
- `columns` (array, optional): Specific columns to retrieve
- `where_clause` (string, optional): WHERE clause for filtering
- `order_by` (string, optional): ORDER BY clause for sorting
- `limit` (integer, optional): Maximum rows to return (default: 100)
- `offset` (integer, optional): Number of rows to skip (default: 0)
- `output_format` (string, optional): Output format ("json", "csv", "list", default: "json")

**Returns:**
- `data_id` (string): Unique data identifier
- `status` (string): Retrieval status ("success", "error")
- `database_name` (string): Database name
- `table_name` (string): Table name
- `total_rows` (integer, optional): Total rows in table
- `returned_rows` (integer): Number of rows returned
- `data` (array, optional): Table data
- `columns` (array, optional): Column names
- `message` (string, optional): Status or error message
- `retrieval_time_ms` (integer, optional): Data retrieval time

### list_databases

Lists available databases.

**Parameters:**
- `connection_id` (string, required): Connection identifier
- `include_system_databases` (boolean, optional): Include system databases (default: false)
- `include_metadata` (boolean, optional): Include database metadata (default: false)

**Returns:**
- `status` (string): Operation status ("success", "error")
- `databases` (array): List of databases
- `message` (string, optional): Status or error message

## MCP Resources

### status

Provides real-time server status information.

**Returns:**
- `server_id` (string): Server identifier
- `status` (string): Server status ("online", "offline", "degraded")
- `timestamp` (string): Status timestamp
- `uptime_seconds` (integer): Server uptime
- `active_connections` (integer): Active connections count
- `total_connections_made` (integer): Total connections made
- `message` (string, optional): Status message

### history

Provides operational history log.

**Returns:**
- Array of history entries with:
  - `timestamp` (string): Event timestamp
  - `event_type` (string): Event type
  - `details` (object): Event details

## Data Models

### ConnectionParams

```python
class ConnectionParams(BaseModel):
    server: str
    database: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
    authentication: str = "windows"
    connection_timeout: int = 30
    pool_size: int = 5
    encrypt: bool = True
    trusted_connection: bool = True
```

### QueryRequest

```python
class QueryRequest(BaseModel):
    connection_id: str
    query: str
    database: Optional[str] = None
    parameters: Optional[List[Any]] = None
    timeout: int = 30
    output_format: str = "json"
```

### SchemaRequest

```python
class SchemaRequest(BaseModel):
    connection_id: str
    database: str
    table_name: Optional[str] = None
    include_columns: bool = True
    include_indexes: bool = False
    include_relationships: bool = False
    include_row_counts: bool = False
    include_data_sizes: bool = False
```

## Error Handling

All MCP tools return standardized error responses:

```json
{
  "status": "error",
  "message": "Error description",
  "error_code": "ERROR_CODE",
  "details": {
    "additional": "error information"
  }
}
```

Common error codes:
- `CONNECTION_FAILED`: Database connection failed
- `INVALID_QUERY`: SQL query is invalid
- `PERMISSION_DENIED`: Insufficient permissions
- `TIMEOUT`: Operation timed out
- `INVALID_PARAMETERS`: Invalid input parameters
