# Contributing to SQL Server MCP Server

Thank you for your interest in contributing to the SQL Server MCP Server! This document provides guidelines and information for contributors.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Process](#development-process)
- [Code Standards](#code-standards)
- [Testing Guidelines](#testing-guidelines)
- [Pull Request Process](#pull-request-process)
- [Issue Reporting](#issue-reporting)
- [Documentation](#documentation)

## Code of Conduct

This project follows the [Contributor Covenant Code of Conduct](CODE_OF_CONDUCT.md). By participating, you agree to uphold this code.

## Getting Started

### Prerequisites

- Python 3.8 or higher
- SQL Server instance (local or remote)
- Git
- Basic understanding of MCP (Model Context Protocol)

### Development Setup

1. **Fork and Clone**
   ```bash
   git clone https://github.com/your-username/sqlserver-mcp-server.git
   cd sqlserver-mcp-server
   ```

2. **Create Virtual Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -e ".[dev]"
   ```

4. **Install Pre-commit Hooks**
   ```bash
   pre-commit install
   ```

5. **Verify Installation**
   ```bash
   pytest tests/unit/ -v
   ```

## Development Process

### Branch Strategy

- **main**: Production-ready code
- **develop**: Integration branch for features
- **feature/***: Feature development branches
- **bugfix/***: Bug fix branches
- **hotfix/***: Critical production fixes

### Workflow

1. **Create Feature Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make Changes**
   - Follow code standards
   - Write tests
   - Update documentation

3. **Test Changes**
   ```bash
   pytest tests/ -v
   black src/ tests/
   isort src/ tests/
   flake8 src/ tests/
   mypy src/
   ```

4. **Commit Changes**
   ```bash
   git add .
   git commit -m "feat: add new feature description"
   ```

5. **Push and Create PR**
   ```bash
   git push origin feature/your-feature-name
   ```

## Code Standards

### Python Style Guide

We follow [PEP 8](https://pep8.org/) with some modifications:

- **Line Length**: 88 characters (Black default)
- **Indentation**: 4 spaces
- **String Quotes**: Double quotes preferred
- **Import Order**: isort configuration

### Code Formatting

**Black** is used for code formatting:
```bash
black src/ tests/
```

**isort** is used for import sorting:
```bash
isort src/ tests/
```

### Type Hints

All functions must have type hints:
```python
def execute_query(
    self, 
    connection_id: str, 
    query: str,
    timeout: int = 30
) -> QueryResult:
    """Execute a SQL query."""
    pass
```

### Documentation

**Docstrings** are required for all public functions:
```python
def create_connection(self, config: ConnectionConfig) -> str:
    """
    Create a new database connection.
    
    Args:
        config: Connection configuration parameters
        
    Returns:
        Connection ID for the created connection
        
    Raises:
        ConnectionError: If connection creation fails
    """
    pass
```

### Error Handling

Use custom exceptions from `src/lib/exceptions.py`:
```python
from ..lib.exceptions import ConnectionError, QueryError

try:
    result = execute_query(query)
except pyodbc.Error as e:
    raise QueryError(f"Query execution failed: {e}") from e
```

## Testing Guidelines

### Test Categories

1. **Unit Tests** (`tests/unit/`)
   - Test individual functions and classes
   - Mock external dependencies
   - Fast execution (< 1 second per test)

2. **Integration Tests** (`tests/integration/`)
   - Test component interactions
   - Use real SQL Server instances
   - May be slower (> 1 second per test)

3. **Contract Tests** (`tests/contract/`)
   - Test MCP protocol compliance
   - Validate input/output schemas
   - Ensure API contract stability

### Test Structure

```python
import pytest
from unittest.mock import Mock, patch

class TestConnectionManager:
    """Test cases for ConnectionManager."""
    
    @pytest.fixture
    def connection_manager(self):
        """Create ConnectionManager instance for testing."""
        return ConnectionManager()
    
    @pytest.fixture
    def mock_config(self):
        """Create mock connection configuration."""
        return ConnectionConfig(
            server="localhost",
            database="test_db"
        )
    
    async def test_create_connection_success(self, connection_manager, mock_config):
        """Test successful connection creation."""
        with patch('pyodbc.connect') as mock_connect:
            mock_connect.return_value = Mock()
            
            connection_id = await connection_manager.create_connection(mock_config)
            
            assert connection_id is not None
            assert connection_id.startswith("conn_")
    
    async def test_create_connection_failure(self, connection_manager, mock_config):
        """Test connection creation failure."""
        with patch('pyodbc.connect') as mock_connect:
            mock_connect.side_effect = pyodbc.Error("Connection failed")
            
            with pytest.raises(ConnectionError):
                await connection_manager.create_connection(mock_config)
```

### Test Markers

Use pytest markers for test categorization:
```python
@pytest.mark.unit
def test_unit_function():
    pass

@pytest.mark.integration
@pytest.mark.requires_db
def test_integration_with_db():
    pass

@pytest.mark.contract
def test_mcp_contract():
    pass

@pytest.mark.slow
def test_performance():
    pass
```

### Running Tests

```bash
# Run all tests
pytest

# Run specific test categories
pytest -m unit
pytest -m integration
pytest -m contract

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/unit/test_connection_manager.py -v
```

## Pull Request Process

### Before Submitting

1. **Ensure Tests Pass**
   ```bash
   pytest tests/ -v
   ```

2. **Check Code Quality**
   ```bash
   black src/ tests/
   isort src/ tests/
   flake8 src/ tests/
   mypy src/
   ```

3. **Update Documentation**
   - Update docstrings
   - Update API documentation if needed
   - Update examples if applicable

### PR Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Unit tests added/updated
- [ ] Integration tests added/updated
- [ ] All tests pass locally

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No breaking changes (or documented)
```

### Review Process

1. **Automated Checks**
   - CI/CD pipeline runs tests
   - Code quality checks
   - Security scans

2. **Manual Review**
   - Code quality and style
   - Test coverage
   - Documentation completeness
   - Performance implications

3. **Approval**
   - At least one maintainer approval required
   - All CI checks must pass
   - No merge conflicts

## Issue Reporting

### Bug Reports

Use the bug report template:

```markdown
**Describe the bug**
A clear description of what the bug is.

**To Reproduce**
Steps to reproduce the behavior:
1. Go to '...'
2. Click on '....'
3. See error

**Expected behavior**
What you expected to happen.

**Environment:**
- OS: [e.g. Windows 10, Ubuntu 20.04]
- Python version: [e.g. 3.9.7]
- SQL Server version: [e.g. 2019]
- Package version: [e.g. 1.0.0]

**Additional context**
Any other context about the problem.
```

### Feature Requests

Use the feature request template:

```markdown
**Is your feature request related to a problem?**
A clear description of what the problem is.

**Describe the solution you'd like**
A clear description of what you want to happen.

**Describe alternatives you've considered**
Alternative solutions or features you've considered.

**Additional context**
Any other context or screenshots about the feature request.
```

## Documentation

### Code Documentation

- **Docstrings**: All public functions and classes
- **Type Hints**: All function parameters and return values
- **Comments**: Complex logic and business rules

### API Documentation

- **API Reference**: Complete tool and resource documentation
- **Examples**: Usage examples for all features
- **Error Codes**: Comprehensive error documentation

### User Documentation

- **README**: Quick start and basic usage
- **Architecture**: System design and components
- **Deployment**: Production deployment guide

## Performance Guidelines

### Code Performance

- Use async/await for I/O operations
- Implement connection pooling
- Cache frequently accessed data
- Optimize database queries

### Test Performance

- Keep unit tests fast (< 1 second)
- Use mocks for external dependencies
- Parallel test execution where possible
- Separate slow tests with markers

## Security Guidelines

### Code Security

- Use parameterized queries (prevent SQL injection)
- Validate all input parameters
- Handle credentials securely
- Log security-relevant events

### Testing Security

- Test input validation
- Test authentication and authorization
- Test error handling
- Test credential management

## Release Process

### Version Numbering

We use [Semantic Versioning](https://semver.org/):
- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes (backward compatible)

### Release Checklist

- [ ] All tests pass
- [ ] Documentation updated
- [ ] Version bumped
- [ ] CHANGELOG updated
- [ ] Release notes prepared
- [ ] Tag created

## Getting Help

### Communication Channels

- **GitHub Issues**: Bug reports and feature requests
- **GitHub Discussions**: General questions and discussions
- **Documentation**: Comprehensive guides and references

### Resources

- [MCP Protocol Documentation](https://modelcontextprotocol.io/)
- [SQL Server Documentation](https://docs.microsoft.com/en-us/sql/)
- [Python Async/Await Guide](https://docs.python.org/3/library/asyncio.html)

---

Thank you for contributing to SQL Server MCP Server! Your contributions help make this project better for everyone.

*Contributing Guide Version: 1.0.0 | Last Updated: 2025-01-27*
