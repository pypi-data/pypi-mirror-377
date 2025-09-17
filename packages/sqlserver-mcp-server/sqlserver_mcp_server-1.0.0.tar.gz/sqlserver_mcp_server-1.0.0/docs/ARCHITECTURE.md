# SQL Server MCP Server - Architecture Documentation

## Overview

The SQL Server MCP Server is a comprehensive Model Context Protocol (MCP) server that provides secure, efficient access to SQL Server databases through standardized MCP tools and resources. This document describes the system architecture, design decisions, and implementation patterns.

## System Architecture

### High-Level Architecture

```
┌─────────────────┐    JSON-RPC 2.0    ┌─────────────────┐
│   MCP Client    │ ←────────────────→ │   MCP Server    │
│  (AI Assistant) │                    │ (SQL Server)    │
└─────────────────┘                    └─────────────────┘
                                              │
                                              │ SQL Operations
                                              ▼
                                       ┌─────────────────┐
                                       │   SQL Server    │
                                       │   Database      │
                                       └─────────────────┘
```

### Component Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    MCP Server Layer                        │
├─────────────────────────────────────────────────────────────┤
│  Tools: execute_query, get_schema, list_databases, etc.    │
│  Resources: connection_status, query_history               │
└─────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────┐
│                    Service Layer                           │
├─────────────────────────────────────────────────────────────┤
│  ConnectionManager │ QueryExecutor │ SchemaService │ DataService │
└─────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────┐
│                    Model Layer                             │
├─────────────────────────────────────────────────────────────┤
│  Connection │ Query │ Schema │ Data Models                 │
└─────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────┐
│                    Infrastructure Layer                    │
├─────────────────────────────────────────────────────────────┤
│  pyodbc │ pydantic │ structlog │ asyncio │ rich │ click    │
└─────────────────────────────────────────────────────────────┘
```

## Core Components

### 1. MCP Server (`src/mcp_tools/mcp_server.py`)

**Purpose**: Main entry point for MCP protocol communication
**Responsibilities**:
- Register MCP tools and resources
- Handle JSON-RPC 2.0 requests
- Route requests to appropriate tools
- Manage server lifecycle

**Key Features**:
- Async/await support for concurrent operations
- Structured logging with context
- Error handling and response formatting
- Tool and resource registration

### 2. Connection Manager (`src/services/connection_manager.py`)

**Purpose**: Manages database connections and connection pooling
**Responsibilities**:
- Create and maintain connection pools
- Health monitoring and connection validation
- Connection lifecycle management
- Pool statistics and metrics

**Key Features**:
- Async connection pooling with pyodbc
- Automatic connection validation
- Health checks and error tracking
- Configurable pool sizes and timeouts

### 3. Query Executor (`src/services/query_executor.py`)

**Purpose**: Executes SQL queries safely and efficiently
**Responsibilities**:
- Parameterized query execution
- Query timeout management
- Result formatting and pagination
- Query history and performance tracking

**Key Features**:
- SQL injection prevention through parameterization
- Configurable timeouts and limits
- Result streaming for large datasets
- Performance metrics collection

### 4. Schema Service (`src/services/schema_service.py`)

**Purpose**: Retrieves and caches database schema information
**Responsibilities**:
- Table, column, and index metadata
- Relationship and constraint information
- Schema caching for performance
- Metadata formatting for MCP responses

**Key Features**:
- Comprehensive metadata queries
- Intelligent caching strategies
- Relationship discovery
- Performance optimization

### 5. Data Service (`src/services/data_service.py`)

**Purpose**: Retrieves and formats table data
**Responsibilities**:
- Paginated data retrieval
- Column selection and filtering
- Data formatting for different output types
- Performance optimization for large datasets

**Key Features**:
- Efficient pagination
- Column filtering and selection
- Multiple output formats (JSON, CSV, table)
- Memory-efficient streaming

## Data Flow

### 1. Connection Establishment

```
Client Request → MCP Server → create_connection_tool → ConnectionManager → pyodbc → SQL Server
```

### 2. Query Execution

```
Client Request → MCP Server → execute_query_tool → QueryExecutor → ConnectionManager → pyodbc → SQL Server
```

### 3. Schema Retrieval

```
Client Request → MCP Server → get_schema_tool → SchemaService → ConnectionManager → pyodbc → SQL Server
```

## Design Patterns

### 1. Service Layer Pattern

Each major functionality is encapsulated in a dedicated service:
- **ConnectionManager**: Connection lifecycle
- **QueryExecutor**: Query execution
- **SchemaService**: Schema operations
- **DataService**: Data retrieval

### 2. Repository Pattern

Data models act as repositories for structured data:
- **Connection Models**: Connection configuration and status
- **Query Models**: Query requests and results
- **Schema Models**: Database metadata

### 3. Factory Pattern

Tool initialization uses factory methods:
```python
def initialize_execute_query_tool(connection_manager, query_executor):
    global _execute_query_tool
    _execute_query_tool = ExecuteQueryTool(connection_manager, query_executor)
```

### 4. Observer Pattern

Health monitoring and status updates:
- Connection health tracking
- Performance metrics collection
- Error monitoring and reporting

## Security Architecture

### 1. Authentication

- **Windows Authentication**: Integrated security
- **SQL Server Authentication**: Username/password
- **Connection String Security**: Encrypted connections

### 2. Authorization

- Database-level permissions
- Connection-scoped access
- Query-level restrictions

### 3. Data Protection

- **SQL Injection Prevention**: Parameterized queries only
- **Connection Encryption**: TLS/SSL support
- **Credential Management**: Secure storage and handling

## Performance Architecture

### 1. Connection Pooling

- Pre-allocated connection pools
- Automatic pool scaling
- Connection reuse and recycling

### 2. Caching Strategy

- Schema metadata caching
- Query result caching (configurable)
- Connection status caching

### 3. Async Operations

- Non-blocking I/O operations
- Concurrent request handling
- Efficient resource utilization

## Error Handling

### 1. Error Hierarchy

```
BaseException
├── ConnectionError
│   ├── AuthenticationError
│   └── TimeoutError
├── QueryError
│   ├── SyntaxError
│   └── PermissionError
└── SchemaError
    └── MetadataError
```

### 2. Error Recovery

- Automatic connection retry
- Graceful degradation
- Error context preservation

## Monitoring and Observability

### 1. Structured Logging

- JSON-formatted logs
- Contextual information
- Performance metrics
- Error tracking

### 2. Health Monitoring

- Connection health checks
- Performance metrics
- Resource utilization
- Error rates

### 3. Metrics Collection

- Query execution times
- Connection pool statistics
- Error counts and types
- Throughput measurements

## Configuration Management

### 1. Environment Variables

- Database connection settings
- Logging configuration
- Performance tuning parameters

### 2. Configuration Files

- JSON-based configuration
- Validation with Pydantic
- Default value management

## Testing Architecture

### 1. Test Categories

- **Contract Tests**: MCP protocol compliance
- **Unit Tests**: Individual component testing
- **Integration Tests**: End-to-end functionality
- **Performance Tests**: Load and stress testing

### 2. Test Data Management

- Isolated test databases
- Test data fixtures
- Cleanup procedures

## Deployment Architecture

### 1. Container Support

- Docker containerization
- Multi-stage builds
- Health check endpoints

### 2. Scaling Considerations

- Horizontal scaling support
- Load balancing compatibility
- Resource isolation

## Future Enhancements

### 1. Planned Features

- Query result streaming
- Advanced caching strategies
- Multi-database support
- Query optimization hints

### 2. Performance Improvements

- Connection multiplexing
- Query plan caching
- Result set compression
- Batch operation support

---

*Architecture Version: 1.0.0 | Last Updated: 2025-01-27*
