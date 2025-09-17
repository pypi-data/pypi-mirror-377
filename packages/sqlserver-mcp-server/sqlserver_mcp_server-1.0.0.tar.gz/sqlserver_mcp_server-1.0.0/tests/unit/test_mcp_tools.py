"""
Unit tests for MCP Tools.

These tests verify the individual functionality of all MCP tools.
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

from src.mcp_tools.execute_query_tool import ExecuteQueryTool
from src.mcp_tools.get_schema_tool import GetSchemaTool
from src.mcp_tools.list_databases_tool import ListDatabasesTool
from src.mcp_tools.get_table_data_tool import GetTableDataTool
from src.mcp_tools.create_connection_tool import CreateConnectionTool
from src.models.connection import ConnectionConfig
from src.models.query import QueryRequest
from src.models.data import GetTableDataRequest


class TestExecuteQueryTool:
    """Test ExecuteQueryTool functionality."""

    @pytest.fixture
    def mock_connection_manager(self):
        """Create a mock connection manager."""
        return AsyncMock()

    @pytest.fixture
    def mock_query_executor(self):
        """Create a mock query executor."""
        return AsyncMock()

    @pytest.fixture
    def execute_query_tool(self, mock_connection_manager, mock_query_executor):
        """Create ExecuteQueryTool instance."""
        return ExecuteQueryTool(mock_connection_manager, mock_query_executor)

    def test_tool_definition(self, execute_query_tool):
        """Test tool definition structure."""
        tool_def = execute_query_tool.get_tool_definition()
        
        assert tool_def.name == "execute_query"
        assert "description" in tool_def.description
        assert "inputSchema" in tool_def.__dict__

    @pytest.mark.asyncio
    async def test_execute_success(self, execute_query_tool, mock_query_executor):
        """Test successful query execution."""
        # Mock successful query result
        mock_result = MagicMock()
        mock_result.success = True
        mock_result.data = [{"id": 1, "name": "test"}]
        mock_result.columns = [MagicMock(name="id"), MagicMock(name="name")]
        mock_result.row_count = 1
        mock_result.execution_time_ms = 15.5
        mock_result.query_id = "query_123"
        
        mock_query_executor.execute_query.return_value = mock_result
        
        # Test arguments
        arguments = {
            "query": "SELECT * FROM users",
            "database": "test_db",
            "timeout": 30
        }
        
        result = await execute_query_tool.execute(arguments, "conn_123")
        
        assert len(result) == 1
        assert "Query executed successfully" in result[0].text
        mock_query_executor.execute_query.assert_called_once()

    @pytest.mark.asyncio
    async def test_execute_error(self, execute_query_tool, mock_query_executor):
        """Test query execution with error."""
        # Mock query executor to raise exception
        mock_query_executor.execute_query.side_effect = Exception("Query failed")
        
        arguments = {"query": "INVALID SQL"}
        
        result = await execute_query_tool.execute(arguments, "conn_123")
        
        assert len(result) == 1
        assert "Error executing query" in result[0].text

    def test_parse_arguments(self, execute_query_tool):
        """Test argument parsing."""
        arguments = {
            "query": "SELECT * FROM users",
            "database": "test_db",
            "timeout": 30,
            "parameters": [
                {"name": "user_id", "value": 123, "type": "int"}
            ]
        }
        
        request = execute_query_tool._parse_arguments(arguments)
        
        assert request.query == "SELECT * FROM users"
        assert request.database == "test_db"
        assert request.timeout == 30
        assert len(request.parameters) == 1
        assert request.parameters[0].name == "user_id"

    def test_parse_arguments_minimal(self, execute_query_tool):
        """Test minimal argument parsing."""
        arguments = {"query": "SELECT 1"}
        
        request = execute_query_tool._parse_arguments(arguments)
        
        assert request.query == "SELECT 1"
        assert request.database is None
        assert request.timeout == 30
        assert request.parameters is None


class TestGetSchemaTool:
    """Test GetSchemaTool functionality."""

    @pytest.fixture
    def mock_connection_manager(self):
        """Create a mock connection manager."""
        return AsyncMock()

    @pytest.fixture
    def mock_schema_service(self):
        """Create a mock schema service."""
        return AsyncMock()

    @pytest.fixture
    def get_schema_tool(self, mock_connection_manager, mock_schema_service):
        """Create GetSchemaTool instance."""
        return GetSchemaTool(mock_connection_manager, mock_schema_service)

    def test_tool_definition(self, get_schema_tool):
        """Test tool definition structure."""
        tool_def = get_schema_tool.get_tool_definition()
        
        assert tool_def.name == "get_schema"
        assert "description" in tool_def.description
        assert "inputSchema" in tool_def.__dict__

    @pytest.mark.asyncio
    async def test_execute_success(self, get_schema_tool, mock_schema_service):
        """Test successful schema retrieval."""
        # Mock successful schema result
        mock_result = MagicMock()
        mock_result.success = True
        mock_result.tables = [MagicMock(name="users")]
        mock_result.execution_time_ms = 10.5
        
        mock_schema_service.get_schema.return_value = mock_result
        
        arguments = {
            "database": "test_db",
            "table_name": "users",
            "include_relationships": True
        }
        
        result = await get_schema_tool.execute(arguments, "conn_123")
        
        assert len(result) == 1
        assert "Schema retrieved successfully" in result[0].text
        mock_schema_service.get_schema.assert_called_once()


class TestListDatabasesTool:
    """Test ListDatabasesTool functionality."""

    @pytest.fixture
    def mock_connection_manager(self):
        """Create a mock connection manager."""
        return AsyncMock()

    @pytest.fixture
    def list_databases_tool(self, mock_connection_manager):
        """Create ListDatabasesTool instance."""
        return ListDatabasesTool(mock_connection_manager)

    def test_tool_definition(self, list_databases_tool):
        """Test tool definition structure."""
        tool_def = list_databases_tool.get_tool_definition()
        
        assert tool_def.name == "list_databases"
        assert "description" in tool_def.description
        assert "inputSchema" in tool_def.__dict__

    @pytest.mark.asyncio
    async def test_execute_success(self, list_databases_tool, mock_connection_manager):
        """Test successful database listing."""
        # Mock connection and cursor
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchall.return_value = [
            ("master", "System database"),
            ("test_db", "Test database")
        ]
        
        mock_connection_manager.get_connection.return_value = mock_conn
        
        arguments = {"include_system": False}
        
        result = await list_databases_tool.execute(arguments, "conn_123")
        
        assert len(result) == 1
        assert "Databases retrieved successfully" in result[0].text


class TestGetTableDataTool:
    """Test GetTableDataTool functionality."""

    @pytest.fixture
    def mock_connection_manager(self):
        """Create a mock connection manager."""
        return AsyncMock()

    @pytest.fixture
    def mock_data_service(self):
        """Create a mock data service."""
        return AsyncMock()

    @pytest.fixture
    def get_table_data_tool(self, mock_connection_manager, mock_data_service):
        """Create GetTableDataTool instance."""
        return GetTableDataTool(mock_connection_manager, mock_data_service)

    def test_tool_definition(self, get_table_data_tool):
        """Test tool definition structure."""
        tool_def = get_table_data_tool.get_tool_definition()
        
        assert tool_def.name == "get_table_data"
        assert "description" in tool_def.description
        assert "inputSchema" in tool_def.__dict__

    @pytest.mark.asyncio
    async def test_execute_success(self, get_table_data_tool, mock_data_service):
        """Test successful table data retrieval."""
        # Mock successful data result
        mock_result = MagicMock()
        mock_result.success = True
        mock_result.data = [{"id": 1, "name": "test"}]
        mock_result.total_rows = 1
        mock_result.returned_rows = 1
        mock_result.execution_time_ms = 5.5
        
        mock_data_service.get_table_data.return_value = mock_result
        
        arguments = {
            "table_name": "users",
            "limit": 100,
            "offset": 0
        }
        
        result = await get_table_data_tool.execute(arguments, "conn_123")
        
        assert len(result) == 1
        assert "Table data retrieved successfully" in result[0].text
        mock_data_service.get_table_data.assert_called_once()


class TestCreateConnectionTool:
    """Test CreateConnectionTool functionality."""

    @pytest.fixture
    def mock_connection_manager(self):
        """Create a mock connection manager."""
        return AsyncMock()

    @pytest.fixture
    def create_connection_tool(self, mock_connection_manager):
        """Create CreateConnectionTool instance."""
        return CreateConnectionTool(mock_connection_manager)

    def test_tool_definition(self, create_connection_tool):
        """Test tool definition structure."""
        tool_def = create_connection_tool.get_tool_definition()
        
        assert tool_def.name == "create_connection"
        assert "description" in tool_def.description
        assert "inputSchema" in tool_def.__dict__

    @pytest.mark.asyncio
    async def test_execute_success(self, create_connection_tool, mock_connection_manager):
        """Test successful connection creation."""
        # Mock successful connection creation
        mock_connection_manager.create_connection.return_value = "conn_123"
        
        arguments = {
            "server": "localhost",
            "database": "test_db",
            "trusted_connection": True
        }
        
        result = await create_connection_tool.execute(arguments)
        
        assert len(result) == 1
        assert "Connection created successfully" in result[0].text
        assert "conn_123" in result[0].text
        mock_connection_manager.create_connection.assert_called_once()

    @pytest.mark.asyncio
    async def test_execute_error(self, create_connection_tool, mock_connection_manager):
        """Test connection creation with error."""
        # Mock connection manager to raise exception
        mock_connection_manager.create_connection.side_effect = Exception("Connection failed")
        
        arguments = {
            "server": "invalid_server",
            "database": "test_db"
        }
        
        result = await create_connection_tool.execute(arguments)
        
        assert len(result) == 1
        assert "Error creating connection" in result[0].text
