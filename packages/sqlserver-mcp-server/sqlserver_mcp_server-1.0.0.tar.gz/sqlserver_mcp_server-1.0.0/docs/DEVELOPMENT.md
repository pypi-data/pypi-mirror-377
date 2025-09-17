# Development Guide

## Project Structure

```
sqlserver-mcp-server/
├── src/
│   ├── cli/                 # CLI implementation
│   │   ├── connection_commands.py
│   │   ├── query_commands.py
│   │   ├── schema_commands.py
│   │   ├── config_commands.py
│   │   └── main.py
│   ├── lib/                 # Shared utilities
│   │   ├── config.py
│   │   ├── logging.py
│   │   └── exceptions.py
│   ├── mcp_tools/          # MCP tools and server
│   │   ├── execute_query_tool.py
│   │   ├── get_schema_tool.py
│   │   ├── list_databases_tool.py
│   │   ├── get_table_data_tool.py
│   │   ├── create_connection_tool.py
│   │   ├── resources.py
│   │   └── mcp_server.py
│   ├── models/             # Data models
│   │   ├── connection.py
│   │   ├── query.py
│   │   └── schema.py
│   └── services/           # Business logic services
│       ├── connection_manager.py
│       ├── query_executor.py
│       ├── schema_service.py
│       └── data_service.py
├── tests/
│   ├── contract/           # Contract tests
│   ├── integration/        # Integration tests
│   └── unit/              # Unit tests
├── docs/                   # Documentation
├── pyproject.toml         # Project configuration
├── requirements.txt       # Dependencies
└── README.md             # Main documentation
```

## Development Setup

### Prerequisites

- Python 3.8+
- Git
- SQL Server instance (for testing)

### Setup

1. Clone the repository:
```bash
git clone https://github.com/your-org/sqlserver-mcp-server.git
cd sqlserver-mcp-server
```

2. Install dependencies:
```bash
pip install -e .
pip install -e ".[dev]"
```

3. Install pre-commit hooks:
```bash
pre-commit install
```

## Testing

### Test Structure

- **Contract Tests**: Define expected behavior and interfaces
- **Integration Tests**: Test component interactions
- **Unit Tests**: Test individual components

### Running Tests

```bash
# All tests
pytest

# Specific test types
pytest tests/contract/
pytest tests/integration/
pytest tests/unit/

# With coverage
pytest --cov=src --cov-report=html

# Specific test file
pytest tests/unit/test_connection_manager.py -v
```

### Test Database Setup

For integration tests, you'll need a SQL Server instance:

```bash
# Set environment variables
export SQLSERVER_TEST_SERVER=localhost
export SQLSERVER_TEST_DATABASE=test_db
export SQLSERVER_TEST_USERNAME=test_user
export SQLSERVER_TEST_PASSWORD=test_password
```

## Code Quality

### Formatting

```bash
# Format code with black
black src/ tests/

# Sort imports with isort
isort src/ tests/
```

### Linting

```bash
# Run flake8
flake8 src/ tests/

# Run mypy for type checking
mypy src/
```

### Pre-commit Hooks

The project uses pre-commit hooks for code quality:

```bash
# Install hooks
pre-commit install

# Run manually
pre-commit run --all-files
```

## Architecture

### MCP Tools

MCP tools are the main interface for external clients. Each tool:

1. Validates input parameters
2. Calls appropriate service methods
3. Formats and returns results
4. Handles errors gracefully

### Services

Services contain the business logic:

- **ConnectionManager**: Manages database connections
- **QueryExecutor**: Executes SQL queries
- **SchemaService**: Retrieves schema information
- **DataService**: Retrieves table data

### Models

Pydantic models for data validation and serialization:

- **ConnectionParams**: Connection configuration
- **QueryRequest/Result**: Query execution
- **SchemaRequest/Result**: Schema information

### CLI

Command-line interface for interactive use:

- Connection management commands
- Query execution commands
- Schema inspection commands
- Configuration management

## Adding New Features

### 1. Define Contract

Start with contract tests in `tests/contract/`:

```python
def test_new_feature():
    # Define expected behavior
    assert new_feature() == expected_result
```

### 2. Create Models

Add Pydantic models in `src/models/`:

```python
class NewFeatureRequest(BaseModel):
    param1: str
    param2: Optional[int] = None
```

### 3. Implement Service

Add business logic in `src/services/`:

```python
class NewFeatureService:
    def process(self, request: NewFeatureRequest) -> NewFeatureResult:
        # Implementation
        pass
```

### 4. Create MCP Tool

Add MCP tool in `src/mcp_tools/`:

```python
class NewFeatureTool:
    def execute(self, **kwargs) -> dict:
        # Validate input
        # Call service
        # Return result
        pass
```

### 5. Add CLI Command

Add CLI command in `src/cli/`:

```python
@click.command()
@click.option('--param1', required=True)
def new_feature(param1):
    # CLI implementation
    pass
```

### 6. Write Tests

Add comprehensive tests:

- Unit tests for services
- Integration tests for workflows
- Contract tests for interfaces

## Debugging

### Logging

The project uses structured logging:

```python
import structlog

logger = structlog.get_logger()
logger.info("Operation completed", result=result)
```

### Environment Variables

Set debug logging:

```bash
export SQLSERVER_MCP_LOG_LEVEL=DEBUG
export SQLSERVER_MCP_LOG_FORMAT=json
```

### Common Issues

1. **Connection Issues**: Check SQL Server connectivity and credentials
2. **Import Errors**: Ensure all dependencies are installed
3. **Test Failures**: Verify test database setup

## Performance

### Connection Pooling

The project uses connection pooling for efficiency:

```python
# Configure pool size
connection_params.pool_size = 10
```

### Query Optimization

- Use parameterized queries
- Set appropriate timeouts
- Limit result sets when possible

### Monitoring

Monitor key metrics:

- Connection pool usage
- Query execution times
- Error rates
- Memory usage

## Deployment

### Production Configuration

```bash
# Set production environment
export SQLSERVER_MCP_ENV=production
export SQLSERVER_MCP_LOG_LEVEL=INFO
export SQLSERVER_MCP_LOG_FORMAT=json
```

### Docker

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY src/ src/
COPY pyproject.toml .

CMD ["python", "-m", "src.mcp_tools"]
```

### Health Checks

The server provides health check endpoints:

- `/health`: Basic health status
- `/status`: Detailed status information

## Contributing

### Pull Request Process

1. Fork the repository
2. Create a feature branch
3. Make changes with tests
4. Ensure all tests pass
5. Submit pull request

### Code Review

- All code must be reviewed
- Tests must pass
- Documentation must be updated
- Code quality checks must pass

### Release Process

1. Update version in `pyproject.toml`
2. Update changelog
3. Create release tag
4. Build and publish package
