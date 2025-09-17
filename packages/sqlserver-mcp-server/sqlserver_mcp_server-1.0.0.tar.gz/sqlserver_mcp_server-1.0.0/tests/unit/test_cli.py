"""
Unit tests for CLI Commands.

These tests verify the individual functionality of all CLI commands.
"""

import pytest
from unittest.mock import MagicMock, patch
from click.testing import CliRunner
from uuid import uuid4

from src.cli.main import main
from src.cli.connection_commands import connect, disconnect, status
from src.cli.query_commands import query, execute
from src.cli.schema_commands import list_databases, list_tables, describe_table, get_schema
from src.cli.data_commands import select
from src.cli.config_commands import config_set, config_get, config_list, config_reset


class TestConnectionCommands:
    """Test connection CLI commands."""

    @pytest.fixture
    def runner(self):
        """Create CLI runner."""
        return CliRunner()

    @pytest.fixture
    def mock_connection_manager(self):
        """Create mock connection manager."""
        with patch('src.cli.connection_commands.ConnectionManager') as mock:
            yield mock.return_value

    def test_connect_command_success(self, runner, mock_connection_manager):
        """Test successful connection command."""
        mock_connection_manager.create_connection.return_value = "conn_123"
        
        result = runner.invoke(connect, [
            "--server", "localhost",
            "--database", "test_db",
            "--trusted-connection"
        ])
        
        assert result.exit_code == 0
        assert "Connection created successfully" in result.output
        assert "conn_123" in result.output

    def test_connect_command_error(self, runner, mock_connection_manager):
        """Test connection command with error."""
        mock_connection_manager.create_connection.side_effect = Exception("Connection failed")
        
        result = runner.invoke(connect, [
            "--server", "invalid_server",
            "--database", "test_db"
        ])
        
        assert result.exit_code == 1
        assert "Error creating connection" in result.output

    def test_disconnect_command_success(self, runner, mock_connection_manager):
        """Test successful disconnect command."""
        mock_connection_manager.close_connection.return_value = None
        
        result = runner.invoke(disconnect, ["conn_123"])
        
        assert result.exit_code == 0
        assert "Connection closed successfully" in result.output

    def test_status_command_success(self, runner, mock_connection_manager):
        """Test successful status command."""
        mock_status = MagicMock()
        mock_status.connection_id = "conn_123"
        mock_status.connected = True
        mock_status.server = "localhost"
        mock_status.database = "test_db"
        mock_connection_manager.get_connection_status.return_value = mock_status
        
        result = runner.invoke(status, ["conn_123"])
        
        assert result.exit_code == 0
        assert "conn_123" in result.output
        assert "localhost" in result.output


class TestQueryCommands:
    """Test query CLI commands."""

    @pytest.fixture
    def runner(self):
        """Create CLI runner."""
        return CliRunner()

    @pytest.fixture
    def mock_query_executor(self):
        """Create mock query executor."""
        with patch('src.cli.query_commands.QueryExecutor') as mock:
            yield mock.return_value

    def test_query_command_success(self, runner, mock_query_executor):
        """Test successful query command."""
        mock_result = MagicMock()
        mock_result.success = True
        mock_result.data = [{"id": 1, "name": "test"}]
        mock_result.row_count = 1
        mock_result.execution_time_ms = 15.5
        mock_query_executor.execute_query.return_value = mock_result
        
        result = runner.invoke(query, [
            "--connection-id", "conn_123",
            "--query", "SELECT * FROM users"
        ])
        
        assert result.exit_code == 0
        assert "Query executed successfully" in result.output

    def test_query_command_error(self, runner, mock_query_executor):
        """Test query command with error."""
        mock_query_executor.execute_query.side_effect = Exception("Query failed")
        
        result = runner.invoke(query, [
            "--connection-id", "conn_123",
            "--query", "INVALID SQL"
        ])
        
        assert result.exit_code == 1
        assert "Error executing query" in result.output

    def test_execute_command_success(self, runner, mock_query_executor):
        """Test successful execute command."""
        mock_result = MagicMock()
        mock_result.success = True
        mock_result.data = []
        mock_result.row_count = 0
        mock_result.execution_time_ms = 5.0
        mock_query_executor.execute_query.return_value = mock_result
        
        # Create a temporary SQL file
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.sql', delete=False) as f:
            f.write("SELECT 1")
            temp_file = f.name
        
        try:
            result = runner.invoke(execute, [
                "--connection-id", "conn_123",
                "--file", temp_file
            ])
            
            assert result.exit_code == 0
            assert "Query executed successfully" in result.output
        finally:
            import os
            os.unlink(temp_file)


class TestSchemaCommands:
    """Test schema CLI commands."""

    @pytest.fixture
    def runner(self):
        """Create CLI runner."""
        return CliRunner()

    @pytest.fixture
    def mock_schema_service(self):
        """Create mock schema service."""
        with patch('src.cli.schema_commands.SchemaService') as mock:
            yield mock.return_value

    def test_list_databases_command_success(self, runner, mock_schema_service):
        """Test successful list databases command."""
        mock_databases = [
            MagicMock(name="master", description="System database"),
            MagicMock(name="test_db", description="Test database")
        ]
        mock_schema_service.list_databases.return_value = mock_databases
        
        result = runner.invoke(list_databases, ["--connection-id", "conn_123"])
        
        assert result.exit_code == 0
        assert "master" in result.output
        assert "test_db" in result.output

    def test_list_tables_command_success(self, runner, mock_schema_service):
        """Test successful list tables command."""
        mock_tables = [
            MagicMock(name="users", schema_name="dbo"),
            MagicMock(name="orders", schema_name="dbo")
        ]
        mock_schema_service.list_tables.return_value = mock_tables
        
        result = runner.invoke(list_tables, [
            "--connection-id", "conn_123",
            "--database", "test_db"
        ])
        
        assert result.exit_code == 0
        assert "users" in result.output
        assert "orders" in result.output

    def test_describe_table_command_success(self, runner, mock_schema_service):
        """Test successful describe table command."""
        mock_table = MagicMock()
        mock_table.name = "users"
        mock_table.schema_name = "dbo"
        mock_table.columns = [
            MagicMock(name="id", data_type="int", nullable=False),
            MagicMock(name="name", data_type="varchar", nullable=True)
        ]
        mock_schema_service.get_table_info.return_value = mock_table
        
        result = runner.invoke(describe_table, [
            "--connection-id", "conn_123",
            "--table", "users",
            "--database", "test_db"
        ])
        
        assert result.exit_code == 0
        assert "users" in result.output
        assert "id" in result.output
        assert "name" in result.output

    def test_get_schema_command_success(self, runner, mock_schema_service):
        """Test successful get schema command."""
        mock_schema = MagicMock()
        mock_schema.success = True
        mock_schema.tables = [MagicMock(name="users")]
        mock_schema.execution_time_ms = 10.5
        mock_schema_service.get_schema.return_value = mock_schema
        
        result = runner.invoke(get_schema, [
            "--connection-id", "conn_123",
            "--database", "test_db",
            "--include-relationships"
        ])
        
        assert result.exit_code == 0
        assert "Schema retrieved successfully" in result.output


class TestDataCommands:
    """Test data CLI commands."""

    @pytest.fixture
    def runner(self):
        """Create CLI runner."""
        return CliRunner()

    @pytest.fixture
    def mock_data_service(self):
        """Create mock data service."""
        with patch('src.cli.data_commands.DataService') as mock:
            yield mock.return_value

    def test_select_command_success(self, runner, mock_data_service):
        """Test successful select command."""
        mock_result = MagicMock()
        mock_result.success = True
        mock_result.data = [{"id": 1, "name": "test"}]
        mock_result.total_rows = 1
        mock_result.returned_rows = 1
        mock_result.execution_time_ms = 5.5
        mock_data_service.get_table_data.return_value = mock_result
        
        result = runner.invoke(select, [
            "--connection-id", "conn_123",
            "--table", "users",
            "--limit", "100"
        ])
        
        assert result.exit_code == 0
        assert "Table data retrieved successfully" in result.output

    def test_select_command_with_filters(self, runner, mock_data_service):
        """Test select command with filters."""
        mock_result = MagicMock()
        mock_result.success = True
        mock_result.data = []
        mock_result.total_rows = 0
        mock_result.returned_rows = 0
        mock_result.execution_time_ms = 3.0
        mock_data_service.get_table_data.return_value = mock_result
        
        result = runner.invoke(select, [
            "--connection-id", "conn_123",
            "--table", "users",
            "--where", "id > 100",
            "--order-by", "name ASC",
            "--columns", "id,name"
        ])
        
        assert result.exit_code == 0
        assert "Table data retrieved successfully" in result.output


class TestConfigCommands:
    """Test config CLI commands."""

    @pytest.fixture
    def runner(self):
        """Create CLI runner."""
        return CliRunner()

    def test_config_set_command_success(self, runner):
        """Test successful config set command."""
        with patch('src.cli.config_commands.set_config') as mock_set:
            mock_set.return_value = None
            
            result = runner.invoke(config_set, [
                "default_server", "localhost"
            ])
            
            assert result.exit_code == 0
            assert "Configuration updated" in result.output

    def test_config_get_command_success(self, runner):
        """Test successful config get command."""
        with patch('src.cli.config_commands.get_config') as mock_get:
            mock_get.return_value = "localhost"
            
            result = runner.invoke(config_get, ["default_server"])
            
            assert result.exit_code == 0
            assert "localhost" in result.output

    def test_config_list_command_success(self, runner):
        """Test successful config list command."""
        with patch('src.cli.config_commands.list_config') as mock_list:
            mock_list.return_value = {"default_server": "localhost", "default_database": "test_db"}
            
            result = runner.invoke(config_list)
            
            assert result.exit_code == 0
            assert "default_server" in result.output
            assert "default_database" in result.output

    def test_config_reset_command_success(self, runner):
        """Test successful config reset command."""
        with patch('src.cli.config_commands.reset_config') as mock_reset:
            mock_reset.return_value = None
            
            result = runner.invoke(config_reset, ["--confirm"])
            
            assert result.exit_code == 0
            assert "Configuration reset" in result.output


class TestMainCLI:
    """Test main CLI functionality."""

    @pytest.fixture
    def runner(self):
        """Create CLI runner."""
        return CliRunner()

    def test_main_help(self, runner):
        """Test main CLI help."""
        result = runner.invoke(main, ["--help"])
        
        assert result.exit_code == 0
        assert "SQL Server MCP Server CLI" in result.output

    def test_main_version(self, runner):
        """Test main CLI version."""
        result = runner.invoke(main, ["--version"])
        
        assert result.exit_code == 0
        assert "1.0.0" in result.output

    def test_main_verbose(self, runner):
        """Test main CLI verbose mode."""
        result = runner.invoke(main, ["--verbose", "connect", "--help"])
        
        assert result.exit_code == 0
        assert "connect" in result.output
