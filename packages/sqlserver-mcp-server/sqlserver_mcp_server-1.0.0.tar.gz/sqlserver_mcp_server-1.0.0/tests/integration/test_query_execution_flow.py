"""
Integration tests for query execution flow.

These tests verify the complete query execution lifecycle from request to result.
"""

import pytest
import asyncio
from uuid import uuid4
from unittest.mock import AsyncMock, MagicMock, patch

from src.models.connection import ConnectionConfig, ConnectionStatus
from src.models.query import QueryRequest, QueryResult
from src.services.connection_manager import ConnectionManager
from src.services.query_executor import QueryExecutor
from src.mcp_tools.execute_query_tool import ExecuteQueryTool


class TestQueryExecutionFlow:
    """Test complete query execution flow."""

    @pytest.fixture
    def connection_params(self):
        """Create test connection parameters."""
        return ConnectionConfig(
            server="test-server",
            database="test-db",
            username="test-user",
            password="test-pass",
            authentication="sql",
            connection_timeout=30,
            pool_size=5
        )

    @pytest.fixture
    def mock_connection(self):
        """Create a mock database connection."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        return mock_conn, mock_cursor

    @pytest.fixture
    async def established_connection(self, connection_params, mock_connection):
        """Create an established connection for testing."""
        mock_conn, mock_cursor = mock_connection
        with patch('pyodbc.connect', return_value=mock_conn):
            status = await ConnectionManager.create_connection(connection_params)
            return status.connection_id, mock_conn, mock_cursor

    @pytest.mark.asyncio
    async def test_select_query_execution(self, established_connection):
        """Test SELECT query execution."""
        connection_id, mock_conn, mock_cursor = established_connection
        
        # Mock query result
        mock_cursor.description = [("id",), ("name",), ("email",)]
        mock_cursor.fetchall.return_value = [
            (1, "John Doe", "john@example.com"),
            (2, "Jane Smith", "jane@example.com")
        ]
        mock_cursor.rowcount = 2
        
        # Create query request
        request = QueryRequest(
            connection_id=connection_id,
            query="SELECT id, name, email FROM users",
            database="test-db"
        )
        
        # Execute query
        result = await QueryExecutor.execute_query(request)
        
        # Verify result
        assert result.status == "success"
        assert result.rows_affected == 2
        assert result.columns == ["id", "name", "email"]
        assert len(result.data) == 2
        assert result.data[0]["id"] == 1
        assert result.data[0]["name"] == "John Doe"
        assert result.execution_time_ms is not None

    @pytest.mark.asyncio
    async def test_insert_query_execution(self, established_connection):
        """Test INSERT query execution."""
        connection_id, mock_conn, mock_cursor = established_connection
        
        # Mock insert result
        mock_cursor.description = None  # No result set for INSERT
        mock_cursor.rowcount = 1
        
        # Create query request
        request = QueryRequest(
            connection_id=connection_id,
            query="INSERT INTO users (name, email) VALUES (?, ?)",
            database="test-db",
            parameters=["New User", "newuser@example.com"]
        )
        
        # Execute query
        result = await QueryExecutor.execute_query(request)
        
        # Verify result
        assert result.status == "success"
        assert result.rows_affected == 1
        assert result.data is None
        assert result.columns is None
        mock_cursor.execute.assert_called_once_with(
            request.query, request.parameters
        )

    @pytest.mark.asyncio
    async def test_query_with_parameters(self, established_connection):
        """Test query execution with parameters."""
        connection_id, mock_conn, mock_cursor = established_connection
        
        # Mock query result
        mock_cursor.description = [("id",), ("name",)]
        mock_cursor.fetchall.return_value = [(1, "John Doe")]
        mock_cursor.rowcount = 1
        
        # Create query request with parameters
        request = QueryRequest(
            connection_id=connection_id,
            query="SELECT id, name FROM users WHERE id = ? AND active = ?",
            database="test-db",
            parameters=[1, True]
        )
        
        # Execute query
        result = await QueryExecutor.execute_query(request)
        
        # Verify parameters were passed correctly
        mock_cursor.execute.assert_called_once_with(
            request.query, request.parameters
        )
        assert result.status == "success"

    @pytest.mark.asyncio
    async def test_query_timeout_handling(self, established_connection):
        """Test query timeout handling."""
        connection_id, mock_conn, mock_cursor = established_connection
        
        # Mock timeout error
        mock_cursor.execute.side_effect = Exception("Query timeout")
        
        # Create query request with short timeout
        request = QueryRequest(
            connection_id=connection_id,
            query="SELECT * FROM large_table",
            database="test-db",
            timeout=1
        )
        
        # Execute query
        result = await QueryExecutor.execute_query(request)
        
        # Verify timeout handling
        assert result.status == "error"
        assert "timeout" in result.message.lower() or "failed" in result.message.lower()

    @pytest.mark.asyncio
    async def test_query_syntax_error(self, established_connection):
        """Test query syntax error handling."""
        connection_id, mock_conn, mock_cursor = established_connection
        
        # Mock syntax error
        mock_cursor.execute.side_effect = Exception("Invalid syntax near 'SELCT'")
        
        # Create query request with syntax error
        request = QueryRequest(
            connection_id=connection_id,
            query="SELCT * FROM users",  # Typo in SELECT
            database="test-db"
        )
        
        # Execute query
        result = await QueryExecutor.execute_query(request)
        
        # Verify error handling
        assert result.status == "error"
        assert "syntax" in result.message.lower() or "failed" in result.message.lower()

    @pytest.mark.asyncio
    async def test_query_permission_error(self, established_connection):
        """Test query permission error handling."""
        connection_id, mock_conn, mock_cursor = established_connection
        
        # Mock permission error
        mock_cursor.execute.side_effect = Exception("Permission denied")
        
        # Create query request
        request = QueryRequest(
            connection_id=connection_id,
            query="DROP TABLE users",
            database="test-db"
        )
        
        # Execute query
        result = await QueryExecutor.execute_query(request)
        
        # Verify error handling
        assert result.status == "error"
        assert "permission" in result.message.lower() or "failed" in result.message.lower()

    @pytest.mark.asyncio
    async def test_query_output_formats(self, established_connection):
        """Test different query output formats."""
        connection_id, mock_conn, mock_cursor = established_connection
        
        # Mock query result
        mock_cursor.description = [("id",), ("name",)]
        mock_cursor.fetchall.return_value = [(1, "John"), (2, "Jane")]
        mock_cursor.rowcount = 2
        
        # Test JSON format
        request = QueryRequest(
            connection_id=connection_id,
            query="SELECT id, name FROM users",
            database="test-db",
            output_format="json"
        )
        
        result = await QueryExecutor.execute_query(request)
        assert result.status == "success"
        assert result.data[0]["id"] == 1
        assert result.data[0]["name"] == "John"
        
        # Test CSV format
        request.output_format = "csv"
        result = await QueryExecutor.execute_query(request)
        assert result.status == "success"
        assert "csv" in result.data[0]
        
        # Test list format
        request.output_format = "list"
        result = await QueryExecutor.execute_query(request)
        assert result.status == "success"
        assert result.data[0] == [1, "John"]

    @pytest.mark.asyncio
    async def test_mcp_tool_integration(self, established_connection):
        """Test MCP tool integration with query executor."""
        connection_id, mock_conn, mock_cursor = established_connection
        
        # Mock query result
        mock_cursor.description = [("count",)]
        mock_cursor.fetchall.return_value = [(42,)]
        mock_cursor.rowcount = 1
        
        # Create MCP tool
        tool = ExecuteQueryTool()
        
        # Execute tool
        result = await tool.run(
            connection_id=str(connection_id),
            query="SELECT COUNT(*) FROM users",
            database="test-db"
        )
        
        # Verify tool result
        assert result["status"] == "success"
        assert result["data"][0]["count"] == 42

    @pytest.mark.asyncio
    async def test_large_result_set_handling(self, established_connection):
        """Test handling of large result sets."""
        connection_id, mock_conn, mock_cursor = established_connection
        
        # Mock large result set
        large_data = [(i, f"User {i}") for i in range(1000)]
        mock_cursor.description = [("id",), ("name",)]
        mock_cursor.fetchall.return_value = large_data
        mock_cursor.rowcount = 1000
        
        # Create query request
        request = QueryRequest(
            connection_id=connection_id,
            query="SELECT id, name FROM users",
            database="test-db"
        )
        
        # Execute query
        result = await QueryExecutor.execute_query(request)
        
        # Verify large result handling
        assert result.status == "success"
        assert len(result.data) == 1000
        assert result.rows_affected == 1000

    @pytest.mark.asyncio
    async def test_empty_result_set(self, established_connection):
        """Test handling of empty result sets."""
        connection_id, mock_conn, mock_cursor = established_connection
        
        # Mock empty result
        mock_cursor.description = [("id",), ("name",)]
        mock_cursor.fetchall.return_value = []
        mock_cursor.rowcount = 0
        
        # Create query request
        request = QueryRequest(
            connection_id=connection_id,
            query="SELECT id, name FROM users WHERE 1=0",
            database="test-db"
        )
        
        # Execute query
        result = await QueryExecutor.execute_query(request)
        
        # Verify empty result handling
        assert result.status == "success"
        assert result.data is None
        assert result.rows_affected == 0
