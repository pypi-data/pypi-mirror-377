# SQL Server MCP Server

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: LGPL v3](https://img.shields.io/badge/License-LGPL%20v3-blue.svg)](https://www.gnu.org/licenses/lgpl-3.0)
[![MCP Protocol](https://img.shields.io/badge/MCP-Protocol-green.svg)](https://modelcontextprotocol.io/)

A comprehensive Model Context Protocol (MCP) server for interacting with SQL Server databases. This server provides AI assistants with secure, efficient access to SQL Server databases through standardized MCP tools and resources.

## ✨ Features

- **🔗 Database Connection Management**: Secure connection pooling with Windows and SQL Server authentication
- **📊 Query Execution**: Execute SQL queries with parameterized queries and multiple output formats
- **🔍 Schema Inspection**: Retrieve detailed database schema information including tables, columns, indexes, and relationships
- **📋 Data Retrieval**: Get table data with pagination, filtering, and sorting capabilities
- **🖥️ CLI Interface**: Full command-line interface for all MCP capabilities
- **🛡️ Security**: SQL injection prevention, secure authentication, and credential management
- **⚡ Performance**: Connection pooling, query optimization, and performance monitoring
- **📚 Full MCP Protocol Compliance**: Complete implementation of MCP protocol standards

## 🚀 Installation

### Prerequisites

- Python 3.8 or higher
- SQL Server instance (local or remote)
- ODBC Driver 17 for SQL Server

### Install from Source

```bash
git clone https://github.com/your-org/sqlserver-mcp-server.git
cd sqlserver-mcp-server
pip install -e .
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

## 🏃‍♂️ Quick Start

### Start MCP Server

```bash
# Start the MCP server
python -m src.mcp_tools

# Or use the CLI entry point
sqlserver-mcp server
```

### Use CLI Interface

```bash
# Connect to database
sqlserver-mcp connect --server "localhost" --database "master" --trusted-connection

# Execute query
sqlserver-mcp query --connection-id <connection-id> "SELECT * FROM sys.tables"

# List databases
sqlserver-mcp list-databases --connection-id <connection-id>

# Get table schema
sqlserver-mcp get-schema --connection-id <connection-id> --table "users"
```

## 🛠️ MCP Tools

The server provides the following MCP tools:

| Tool | Description | Parameters |
|------|-------------|------------|
| `create_connection` | Establish database connections | server, database, authentication |
| `execute_query` | Execute SQL queries | query, database, timeout, parameters |
| `get_schema` | Retrieve schema information | database, table_name, include_relationships |
| `get_table_data` | Get table data with pagination | table_name, limit, offset, where_clause |
| `list_databases` | List available databases | include_system, include_metadata |

## 📖 MCP Resources

The server provides the following MCP resources:

| Resource | Description | URI |
|----------|-------------|-----|
| `connection_status` | Real-time connection health and metrics | `mcp://sqlserver/connection_status` |
| `query_history` | Query execution history and statistics | `mcp://sqlserver/query_history` |

## ⚙️ Configuration

### Environment Variables

```bash
export SQLSERVER_MCP_LOG_LEVEL=INFO
export SQLSERVER_MCP_SERVER_HOST=127.0.0.1
export SQLSERVER_MCP_SERVER_PORT=8000
```

### Configuration File

Create a `config.json` file in your project directory:

```json
{
  "default_server": "localhost",
  "default_database": "master",
  "connection_timeout": 30,
  "pool_size": 10,
  "log_level": "INFO",
  "output_format": "table"
}
```

## 📚 Usage Examples

### MCP Client Integration

```python
import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def main():
    # Connect to SQL Server MCP Server
    server_params = StdioServerParameters(
        command="python",
        args=["-m", "src.mcp_tools"]
    )
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize the session
            await session.initialize()
            
            # Create a database connection
            result = await session.call_tool(
                "create_connection",
                {
                    "server": "localhost",
                    "database": "master",
                    "trusted_connection": True
                }
            )
            
            connection_id = result.content[0].text
            
            # Execute a query
            query_result = await session.call_tool(
                "execute_query",
                {
                    "query": "SELECT name FROM sys.databases",
                    "connection_id": connection_id
                }
            )
            
            print(query_result.content[0].text)

if __name__ == "__main__":
    asyncio.run(main())
```

### CLI Examples

```bash
# Connect to SQL Server
sqlserver-mcp connect --server "localhost" --database "AdventureWorks" --trusted-connection

# List all databases
sqlserver-mcp list-databases --connection-id conn_123

# Get table schema
sqlserver-mcp get-schema --connection-id conn_123 --table "Person.Person" --include-relationships

# Execute parameterized query
sqlserver-mcp query --connection-id conn_123 "SELECT * FROM Person.Person WHERE BusinessEntityID = @id" --params '{"id": 1}'

# Get table data with pagination
sqlserver-mcp select --connection-id conn_123 --table "Person.Person" --limit 10 --offset 0

# Export query results to CSV
sqlserver-mcp query --connection-id conn_123 "SELECT * FROM Person.Person" --output-format csv > results.csv
```

## 🧪 Testing

The project includes comprehensive test coverage:

- **Contract Tests**: Validate MCP protocol compliance
- **Integration Tests**: Test with real SQL Server instances
- **Unit Tests**: Test individual components
- **Performance Tests**: Benchmark query execution and connection management

### Running Tests

```bash
# Run all tests
pytest

# Run specific test categories
pytest tests/contract/     # Contract tests
pytest tests/integration/  # Integration tests  
pytest tests/unit/        # Unit tests
pytest tests/performance/ # Performance tests

# Run with coverage
pytest --cov=src --cov-report=html
```

## 🏗️ Architecture

The SQL Server MCP Server follows a modular architecture:

```
src/
├── mcp_tools/          # MCP protocol implementation
│   ├── execute_query_tool.py
│   ├── get_schema_tool.py
│   ├── list_databases_tool.py
│   ├── get_table_data_tool.py
│   ├── create_connection_tool.py
│   └── mcp_server.py
├── services/           # Business logic services
│   ├── connection_manager.py
│   ├── query_executor.py
│   ├── schema_service.py
│   └── data_service.py
├── models/             # Data models
│   ├── connection.py
│   ├── query.py
│   ├── schema.py
│   └── data.py
├── cli/                # Command-line interface
│   ├── connection_commands.py
│   ├── query_commands.py
│   ├── schema_commands.py
│   ├── data_commands.py
│   └── config_commands.py
└── lib/                # Shared utilities
    ├── config.py
    ├── logging.py
    ├── exceptions.py
    └── performance.py
```

## 🔧 Development

### Setup Development Environment

```bash
# Clone the repository
git clone https://github.com/your-org/sqlserver-mcp-server.git
cd sqlserver-mcp-server

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -e ".[dev]"
```

### Code Quality

```bash
# Format code
black src/ tests/
isort src/ tests/

# Lint code
flake8 src/ tests/
mypy src/

# Run all quality checks
make lint
```

### Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test categories
pytest tests/contract/     # Contract tests
pytest tests/integration/  # Integration tests
pytest tests/unit/        # Unit tests
pytest tests/performance/ # Performance tests
```

### Building

```bash
# Build package
python -m build

# Install from built package
pip install dist/sqlserver_mcp_server-*.whl
```

## 📋 Roadmap

- [ ] Support for additional database engines (PostgreSQL, MySQL)
- [ ] Advanced query optimization and caching
- [ ] Real-time database monitoring and alerts
- [ ] Enhanced security features (encryption, audit logging)
- [ ] Web-based administration interface
- [ ] Docker containerization and Kubernetes support

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](docs/CONTRIBUTING.md) for details.

### Development Workflow

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests for your changes
5. Run the test suite (`pytest`)
6. Commit your changes (`git commit -m 'Add amazing feature'`)
7. Push to the branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

## 📄 License

This project is licensed under the GNU Lesser General Public License v3.0 - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- 📖 **Documentation**: Check the [docs/](docs/) directory for detailed documentation
- 🐛 **Bug Reports**: Create a [GitHub issue](https://github.com/your-org/sqlserver-mcp-server/issues)
- 💡 **Feature Requests**: Create a [GitHub issue](https://github.com/your-org/sqlserver-mcp-server/issues)
- 💬 **Discussions**: Join our [GitHub Discussions](https://github.com/your-org/sqlserver-mcp-server/discussions)
- 📧 **Email**: Contact us at support@your-org.com

## 🙏 Acknowledgments

- [Model Context Protocol](https://modelcontextprotocol.io/) for the MCP specification
- [pyodbc](https://github.com/mkleehammer/pyodbc) for SQL Server connectivity
- [Pydantic](https://pydantic.dev/) for data validation
- [Click](https://click.palletsprojects.com/) for CLI framework
- [Rich](https://rich.readthedocs.io/) for beautiful terminal output

## 📊 Project Status

![GitHub last commit](https://img.shields.io/github/last-commit/your-org/sqlserver-mcp-server)
![GitHub issues](https://img.shields.io/github/issues/your-org/sqlserver-mcp-server)
![GitHub pull requests](https://img.shields.io/github/issues-pr/your-org/sqlserver-mcp-server)
![GitHub stars](https://img.shields.io/github/stars/your-org/sqlserver-mcp-server)