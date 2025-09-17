"""
Unit tests for QueryExecutor service.

These tests verify the individual functionality of the QueryExecutor class.
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

from src.models.query import QueryRequest, QueryResult
from src.services.query_executor import QueryExecutor


class TestQueryExecutor:
    """Test QueryExecutor service functionality."""

    @pytest.fixture
    def mock_connection(self):
        """Create a mock database connection."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        return mock_conn, mock_cursor

    @pytest.fixture
    def query_request(self):
        """Create test query request."""
        return QueryRequest(
            connection_id=uuid4(),
            query="SELECT id, name FROM users",
            database="test-db"
        )

    @pytest.mark.asyncio
    async def test_execute_select_query(self, query_request, mock_connection):
        """Test executing a SELECT query."""
        mock_conn, mock_cursor = mock_connection
        
        # Mock query result
        mock_cursor.description = [("id",), ("name",)]
        mock_cursor.fetchall.return_value = [
            (1, "John Doe"),
            (2, "Jane Smith")
        ]
        mock_cursor.rowcount = 2
        
        with patch('src.services.connection_manager.ConnectionManager.get_connection', return_value=mock_conn):
            result = await QueryExecutor.execute_query(query_request)
            
            assert result.status == "success"
            assert result.rows_affected == 2
            assert result.columns == ["id", "name"]
            assert len(result.data) == 2
            assert result.data[0]["id"] == 1
            assert result.data[0]["name"] == "John Doe"
            assert result.execution_time_ms is not None

    @pytest.mark.asyncio
    async def test_execute_insert_query(self, mock_connection):
        """Test executing an INSERT query."""
        mock_conn, mock_cursor = mock_connection
        
        # Mock insert result
        mock_cursor.description = None  # No result set for INSERT
        mock_cursor.rowcount = 1
        
        request = QueryRequest(
            connection_id=uuid4(),
            query="INSERT INTO users (name) VALUES (?)",
            database="test-db",
            parameters=["New User"]
        )
        
        with patch('src.services.connection_manager.ConnectionManager.get_connection', return_value=mock_conn):
            result = await QueryExecutor.execute_query(request)
            
            assert result.status == "success"
            assert result.rows_affected == 1
            assert result.data is None
            assert result.columns is None
            mock_cursor.execute.assert_called_once_with(request.query, request.parameters)

    @pytest.mark.asyncio
    async def test_execute_update_query(self, mock_connection):
        """Test executing an UPDATE query."""
        mock_conn, mock_cursor = mock_connection
        
        # Mock update result
        mock_cursor.description = None
        mock_cursor.rowcount = 3
        
        request = QueryRequest(
            connection_id=uuid4(),
            query="UPDATE users SET active = ? WHERE status = ?",
            database="test-db",
            parameters=[True, "inactive"]
        )
        
        with patch('src.services.connection_manager.ConnectionManager.get_connection', return_value=mock_conn):
            result = await QueryExecutor.execute_query(request)
            
            assert result.status == "success"
            assert result.rows_affected == 3
            assert result.data is None
            assert result.columns is None

    @pytest.mark.asyncio
    async def test_execute_delete_query(self, mock_connection):
        """Test executing a DELETE query."""
        mock_conn, mock_cursor = mock_connection
        
        # Mock delete result
        mock_cursor.description = None
        mock_cursor.rowcount = 5
        
        request = QueryRequest(
            connection_id=uuid4(),
            query="DELETE FROM users WHERE created_date < ?",
            database="test-db",
            parameters=["2020-01-01"]
        )
        
        with patch('src.services.connection_manager.ConnectionManager.get_connection', return_value=mock_conn):
            result = await QueryExecutor.execute_query(request)
            
            assert result.status == "success"
            assert result.rows_affected == 5
            assert result.data is None
            assert result.columns is None

    @pytest.mark.asyncio
    async def test_execute_query_with_parameters(self, mock_connection):
        """Test executing a query with parameters."""
        mock_conn, mock_cursor = mock_connection
        
        # Mock query result
        mock_cursor.description = [("id",), ("name",)]
        mock_cursor.fetchall.return_value = [(1, "John Doe")]
        mock_cursor.rowcount = 1
        
        request = QueryRequest(
            connection_id=uuid4(),
            query="SELECT id, name FROM users WHERE id = ? AND active = ?",
            database="test-db",
            parameters=[1, True]
        )
        
        with patch('src.services.connection_manager.ConnectionManager.get_connection', return_value=mock_conn):
            result = await QueryExecutor.execute_query(request)
            
            assert result.status == "success"
            mock_cursor.execute.assert_called_once_with(request.query, request.parameters)

    @pytest.mark.asyncio
    async def test_execute_query_no_parameters(self, mock_connection):
        """Test executing a query without parameters."""
        mock_conn, mock_cursor = mock_connection
        
        # Mock query result
        mock_cursor.description = [("count",)]
        mock_cursor.fetchall.return_value = [(42,)]
        mock_cursor.rowcount = 1
        
        request = QueryRequest(
            connection_id=uuid4(),
            query="SELECT COUNT(*) FROM users",
            database="test-db"
        )
        
        with patch('src.services.connection_manager.ConnectionManager.get_connection', return_value=mock_conn):
            result = await QueryExecutor.execute_query(request)
            
            assert result.status == "success"
            mock_cursor.execute.assert_called_once_with(request.query, [])

    @pytest.mark.asyncio
    async def test_execute_query_connection_not_found(self, query_request):
        """Test executing a query when connection is not found."""
        with patch('src.services.connection_manager.ConnectionManager.get_connection', return_value=None):
            result = await QueryExecutor.execute_query(query_request)
            
            assert result.status == "error"
            assert "Connection not found" in result.message

    @pytest.mark.asyncio
    async def test_execute_query_database_error(self, query_request, mock_connection):
        """Test executing a query when database error occurs."""
        mock_conn, mock_cursor = mock_connection
        
        # Mock database error
        mock_cursor.execute.side_effect = Exception("Database error")
        
        with patch('src.services.connection_manager.ConnectionManager.get_connection', return_value=mock_conn):
            result = await QueryExecutor.execute_query(query_request)
            
            assert result.status == "error"
            assert "Database error" in result.message
            assert result.execution_time_ms is not None

    @pytest.mark.asyncio
    async def test_execute_query_syntax_error(self, query_request, mock_connection):
        """Test executing a query with syntax error."""
        mock_conn, mock_cursor = mock_connection
        
        # Mock syntax error
        mock_cursor.execute.side_effect = Exception("Invalid syntax near 'SELCT'")
        
        with patch('src.services.connection_manager.ConnectionManager.get_connection', return_value=mock_conn):
            result = await QueryExecutor.execute_query(query_request)
            
            assert result.status == "error"
            assert "syntax" in result.message.lower() or "failed" in result.message.lower()

    @pytest.mark.asyncio
    async def test_execute_query_permission_error(self, query_request, mock_connection):
        """Test executing a query with permission error."""
        mock_conn, mock_cursor = mock_connection
        
        # Mock permission error
        mock_cursor.execute.side_effect = Exception("Permission denied")
        
        with patch('src.services.connection_manager.ConnectionManager.get_connection', return_value=mock_conn):
            result = await QueryExecutor.execute_query(query_request)
            
            assert result.status == "error"
            assert "permission" in result.message.lower() or "failed" in result.message.lower()

    @pytest.mark.asyncio
    async def test_execute_query_timeout_error(self, query_request, mock_connection):
        """Test executing a query with timeout error."""
        mock_conn, mock_cursor = mock_connection
        
        # Mock timeout error
        mock_cursor.execute.side_effect = Exception("Query timeout")
        
        with patch('src.services.connection_manager.ConnectionManager.get_connection', return_value=mock_conn):
            result = await QueryExecutor.execute_query(query_request)
            
            assert result.status == "error"
            assert "timeout" in result.message.lower() or "failed" in result.message.lower()

    @pytest.mark.asyncio
    async def test_execute_query_unexpected_error(self, query_request, mock_connection):
        """Test executing a query with unexpected error."""
        mock_conn, mock_cursor = mock_connection
        
        # Mock unexpected error
        mock_cursor.execute.side_effect = Exception("Unexpected error")
        
        with patch('src.services.connection_manager.ConnectionManager.get_connection', return_value=mock_conn):
            result = await QueryExecutor.execute_query(query_request)
            
            assert result.status == "error"
            assert "unexpected error" in result.message.lower()

    @pytest.mark.asyncio
    async def test_format_results_json(self, mock_connection):
        """Test formatting results as JSON."""
        mock_conn, mock_cursor = mock_connection
        
        # Mock query result
        mock_cursor.description = [("id",), ("name",)]
        mock_cursor.fetchall.return_value = [
            (1, "John Doe"),
            (2, "Jane Smith")
        ]
        mock_cursor.rowcount = 2
        
        request = QueryRequest(
            connection_id=uuid4(),
            query="SELECT id, name FROM users",
            database="test-db",
            output_format="json"
        )
        
        with patch('src.services.connection_manager.ConnectionManager.get_connection', return_value=mock_conn):
            result = await QueryExecutor.execute_query(request)
            
            assert result.status == "success"
            assert result.data[0]["id"] == 1
            assert result.data[0]["name"] == "John Doe"
            assert result.data[1]["id"] == 2
            assert result.data[1]["name"] == "Jane Smith"

    @pytest.mark.asyncio
    async def test_format_results_csv(self, mock_connection):
        """Test formatting results as CSV."""
        mock_conn, mock_cursor = mock_connection
        
        # Mock query result
        mock_cursor.description = [("id",), ("name",)]
        mock_cursor.fetchall.return_value = [
            (1, "John Doe"),
            (2, "Jane Smith")
        ]
        mock_cursor.rowcount = 2
        
        request = QueryRequest(
            connection_id=uuid4(),
            query="SELECT id, name FROM users",
            database="test-db",
            output_format="csv"
        )
        
        with patch('src.services.connection_manager.ConnectionManager.get_connection', return_value=mock_conn):
            result = await QueryExecutor.execute_query(request)
            
            assert result.status == "success"
            assert "csv" in result.data[0]
            csv_content = result.data[0]["csv"]
            assert "id,name" in csv_content
            assert "1,John Doe" in csv_content
            assert "2,Jane Smith" in csv_content

    @pytest.mark.asyncio
    async def test_format_results_list(self, mock_connection):
        """Test formatting results as list."""
        mock_conn, mock_cursor = mock_connection
        
        # Mock query result
        mock_cursor.description = [("id",), ("name",)]
        mock_cursor.fetchall.return_value = [
            (1, "John Doe"),
            (2, "Jane Smith")
        ]
        mock_cursor.rowcount = 2
        
        request = QueryRequest(
            connection_id=uuid4(),
            query="SELECT id, name FROM users",
            database="test-db",
            output_format="list"
        )
        
        with patch('src.services.connection_manager.ConnectionManager.get_connection', return_value=mock_conn):
            result = await QueryExecutor.execute_query(request)
            
            assert result.status == "success"
            assert result.data[0] == [1, "John Doe"]
            assert result.data[1] == [2, "Jane Smith"]

    @pytest.mark.asyncio
    async def test_execute_query_empty_result(self, mock_connection):
        """Test executing a query that returns empty result."""
        mock_conn, mock_cursor = mock_connection
        
        # Mock empty result
        mock_cursor.description = [("id",), ("name",)]
        mock_cursor.fetchall.return_value = []
        mock_cursor.rowcount = 0
        
        request = QueryRequest(
            connection_id=uuid4(),
            query="SELECT id, name FROM users WHERE 1=0",
            database="test-db"
        )
        
        with patch('src.services.connection_manager.ConnectionManager.get_connection', return_value=mock_conn):
            result = await QueryExecutor.execute_query(request)
            
            assert result.status == "success"
            assert result.data is None
            assert result.rows_affected == 0

    @pytest.mark.asyncio
    async def test_execute_query_large_result_set(self, mock_connection):
        """Test executing a query with large result set."""
        mock_conn, mock_cursor = mock_connection
        
        # Mock large result set
        large_data = [(i, f"User {i}") for i in range(1000)]
        mock_cursor.description = [("id",), ("name",)]
        mock_cursor.fetchall.return_value = large_data
        mock_cursor.rowcount = 1000
        
        request = QueryRequest(
            connection_id=uuid4(),
            query="SELECT id, name FROM users",
            database="test-db"
        )
        
        with patch('src.services.connection_manager.ConnectionManager.get_connection', return_value=mock_conn):
            result = await QueryExecutor.execute_query(request)
            
            assert result.status == "success"
            assert len(result.data) == 1000
            assert result.rows_affected == 1000

    def test_format_results_static_method(self):
        """Test the static _format_results method."""
        rows = [(1, "John"), (2, "Jane")]
        columns = ["id", "name"]
        
        # Test JSON format
        result = QueryExecutor._format_results(rows, columns, "json")
        assert result[0]["id"] == 1
        assert result[0]["name"] == "John"
        
        # Test CSV format
        result = QueryExecutor._format_results(rows, columns, "csv")
        assert "csv" in result[0]
        csv_content = result[0]["csv"]
        assert "id,name" in csv_content
        assert "1,John" in csv_content
        
        # Test list format
        result = QueryExecutor._format_results(rows, columns, "list")
        assert result[0] == [1, "John"]
        assert result[1] == [2, "Jane"]

    def test_format_results_empty_data(self):
        """Test formatting empty data."""
        result = QueryExecutor._format_results([], ["id", "name"], "json")
        assert result is None
