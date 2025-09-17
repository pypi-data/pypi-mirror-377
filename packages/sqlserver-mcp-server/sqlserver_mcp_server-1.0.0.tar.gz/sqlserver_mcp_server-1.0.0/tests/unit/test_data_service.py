"""
Unit tests for DataService.

These tests verify the individual functionality of the DataService class.
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

from src.services.data_service import DataService
from src.models.data import GetTableDataRequest, GetTableDataResult


class TestDataService:
    """Test DataService functionality."""

    @pytest.fixture
    def mock_connection(self):
        """Create a mock database connection."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        return mock_conn, mock_cursor

    @pytest.fixture
    def table_data_request(self):
        """Create test table data request."""
        return GetTableDataRequest(
            connection_id=uuid4(),
            database="test-db",
            table_name="users",
            limit=100,
            offset=0
        )

    @pytest.mark.asyncio
    async def test_get_table_data_success(self, table_data_request, mock_connection):
        """Test successful table data retrieval."""
        mock_conn, mock_cursor = mock_connection
        
        # Mock query result
        mock_cursor.description = [("id",), ("name",), ("email",)]
        mock_cursor.fetchall.return_value = [
            (1, "John Doe", "john@example.com"),
            (2, "Jane Smith", "jane@example.com")
        ]
        
        # Mock count query
        mock_cursor.fetchone.return_value = (2,)
        
        with patch('src.services.connection_manager.ConnectionManager.get_connection', return_value=mock_conn):
            result = await DataService.get_table_data(table_data_request)
            
            assert result.status == "success"
            assert result.database_name == "test-db"
            assert result.table_name == "users"
            assert result.returned_rows == 2
            assert result.total_rows == 2
            assert len(result.data) == 2
            assert result.columns == ["id", "name", "email"]
            assert result.data[0]["id"] == 1
            assert result.data[0]["name"] == "John Doe"

    @pytest.mark.asyncio
    async def test_get_table_data_connection_not_found(self, table_data_request):
        """Test table data retrieval when connection is not found."""
        with patch('src.services.connection_manager.ConnectionManager.get_connection', return_value=None):
            result = await DataService.get_table_data(table_data_request)
            
            assert result.status == "error"
            assert "Connection not found" in result.message
            assert result.returned_rows == 0

    @pytest.mark.asyncio
    async def test_get_table_data_with_columns(self, mock_connection):
        """Test table data retrieval with specific columns."""
        mock_conn, mock_cursor = mock_connection
        
        # Mock query result
        mock_cursor.description = [("id",), ("name",)]
        mock_cursor.fetchall.return_value = [
            (1, "John Doe"),
            (2, "Jane Smith")
        ]
        
        # Mock count query
        mock_cursor.fetchone.return_value = (2,)
        
        request = GetTableDataRequest(
            connection_id=uuid4(),
            database="test-db",
            table_name="users",
            columns=["id", "name"],
            limit=100,
            offset=0
        )
        
        with patch('src.services.connection_manager.ConnectionManager.get_connection', return_value=mock_conn):
            result = await DataService.get_table_data(request)
            
            assert result.status == "success"
            assert len(result.data) == 2
            assert result.columns == ["id", "name"]
            assert "email" not in result.data[0]

    @pytest.mark.asyncio
    async def test_get_table_data_with_where_clause(self, mock_connection):
        """Test table data retrieval with WHERE clause."""
        mock_conn, mock_cursor = mock_connection
        
        # Mock query result
        mock_cursor.description = [("id",), ("name",)]
        mock_cursor.fetchall.return_value = [(1, "John Doe")]
        
        # Mock count query
        mock_cursor.fetchone.return_value = (1,)
        
        request = GetTableDataRequest(
            connection_id=uuid4(),
            database="test-db",
            table_name="users",
            where_clause="id = 1",
            limit=100,
            offset=0
        )
        
        with patch('src.services.connection_manager.ConnectionManager.get_connection', return_value=mock_conn):
            result = await DataService.get_table_data(request)
            
            assert result.status == "success"
            assert len(result.data) == 1
            assert result.data[0]["id"] == 1

    @pytest.mark.asyncio
    async def test_get_table_data_with_order_by(self, mock_connection):
        """Test table data retrieval with ORDER BY clause."""
        mock_conn, mock_cursor = mock_connection
        
        # Mock query result
        mock_cursor.description = [("id",), ("name",)]
        mock_cursor.fetchall.return_value = [
            (2, "Jane Smith"),
            (1, "John Doe")
        ]
        
        # Mock count query
        mock_cursor.fetchone.return_value = (2,)
        
        request = GetTableDataRequest(
            connection_id=uuid4(),
            database="test-db",
            table_name="users",
            order_by="name DESC",
            limit=100,
            offset=0
        )
        
        with patch('src.services.connection_manager.ConnectionManager.get_connection', return_value=mock_conn):
            result = await DataService.get_table_data(request)
            
            assert result.status == "success"
            assert len(result.data) == 2
            assert result.data[0]["name"] == "Jane Smith"

    @pytest.mark.asyncio
    async def test_get_table_data_with_pagination(self, mock_connection):
        """Test table data retrieval with pagination."""
        mock_conn, mock_cursor = mock_connection
        
        # Mock query result
        mock_cursor.description = [("id",), ("name",)]
        mock_cursor.fetchall.return_value = [(3, "Bob Johnson")]
        
        # Mock count query
        mock_cursor.fetchone.return_value = (3,)
        
        request = GetTableDataRequest(
            connection_id=uuid4(),
            database="test-db",
            table_name="users",
            limit=1,
            offset=2
        )
        
        with patch('src.services.connection_manager.ConnectionManager.get_connection', return_value=mock_conn):
            result = await DataService.get_table_data(request)
            
            assert result.status == "success"
            assert len(result.data) == 1
            assert result.data[0]["id"] == 3
            assert result.total_rows == 3

    @pytest.mark.asyncio
    async def test_get_table_data_database_error(self, table_data_request, mock_connection):
        """Test table data retrieval when database error occurs."""
        mock_conn, mock_cursor = mock_connection
        
        # Mock database error
        mock_cursor.execute.side_effect = Exception("Database error")
        
        with patch('src.services.connection_manager.ConnectionManager.get_connection', return_value=mock_conn):
            result = await DataService.get_table_data(table_data_request)
            
            assert result.status == "error"
            assert "Database error" in result.message
            assert result.returned_rows == 0

    @pytest.mark.asyncio
    async def test_get_table_data_permission_error(self, table_data_request, mock_connection):
        """Test table data retrieval with permission error."""
        mock_conn, mock_cursor = mock_connection
        
        # Mock permission error
        mock_cursor.execute.side_effect = Exception("Permission denied")
        
        with patch('src.services.connection_manager.ConnectionManager.get_connection', return_value=mock_conn):
            result = await DataService.get_table_data(table_data_request)
            
            assert result.status == "error"
            assert "permission" in result.message.lower() or "failed" in result.message.lower()

    @pytest.mark.asyncio
    async def test_get_table_data_unexpected_error(self, table_data_request, mock_connection):
        """Test table data retrieval with unexpected error."""
        mock_conn, mock_cursor = mock_connection
        
        # Mock unexpected error
        mock_cursor.execute.side_effect = Exception("Unexpected error")
        
        with patch('src.services.connection_manager.ConnectionManager.get_connection', return_value=mock_conn):
            result = await DataService.get_table_data(table_data_request)
            
            assert result.status == "error"
            assert "unexpected error" in result.message.lower()

    @pytest.mark.asyncio
    async def test_get_table_data_empty_result(self, mock_connection):
        """Test table data retrieval with empty result."""
        mock_conn, mock_cursor = mock_connection
        
        # Mock empty result
        mock_cursor.description = [("id",), ("name",)]
        mock_cursor.fetchall.return_value = []
        
        # Mock count query
        mock_cursor.fetchone.return_value = (0,)
        
        request = GetTableDataRequest(
            connection_id=uuid4(),
            database="test-db",
            table_name="users",
            limit=100,
            offset=0
        )
        
        with patch('src.services.connection_manager.ConnectionManager.get_connection', return_value=mock_conn):
            result = await DataService.get_table_data(request)
            
            assert result.status == "success"
            assert result.data is None
            assert result.returned_rows == 0
            assert result.total_rows == 0

    @pytest.mark.asyncio
    async def test_get_table_data_count_error(self, mock_connection):
        """Test table data retrieval when count query fails."""
        mock_conn, mock_cursor = mock_connection
        
        # Mock query result
        mock_cursor.description = [("id",), ("name",)]
        mock_cursor.fetchall.return_value = [(1, "John Doe")]
        
        # Mock count query error
        mock_cursor.fetchone.side_effect = Exception("Count query failed")
        
        request = GetTableDataRequest(
            connection_id=uuid4(),
            database="test-db",
            table_name="users",
            limit=100,
            offset=0
        )
        
        with patch('src.services.connection_manager.ConnectionManager.get_connection', return_value=mock_conn):
            result = await DataService.get_table_data(request)
            
            # Should still succeed even if count fails
            assert result.status == "success"
            assert len(result.data) == 1
            assert result.total_rows is None

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
        
        # Mock count query
        mock_cursor.fetchone.return_value = (2,)
        
        request = GetTableDataRequest(
            connection_id=uuid4(),
            database="test-db",
            table_name="users",
            output_format="json",
            limit=100,
            offset=0
        )
        
        with patch('src.services.connection_manager.ConnectionManager.get_connection', return_value=mock_conn):
            result = await DataService.get_table_data(request)
            
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
        
        # Mock count query
        mock_cursor.fetchone.return_value = (2,)
        
        request = GetTableDataRequest(
            connection_id=uuid4(),
            database="test-db",
            table_name="users",
            output_format="csv",
            limit=100,
            offset=0
        )
        
        with patch('src.services.connection_manager.ConnectionManager.get_connection', return_value=mock_conn):
            result = await DataService.get_table_data(request)
            
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
        
        # Mock count query
        mock_cursor.fetchone.return_value = (2,)
        
        request = GetTableDataRequest(
            connection_id=uuid4(),
            database="test-db",
            table_name="users",
            output_format="list",
            limit=100,
            offset=0
        )
        
        with patch('src.services.connection_manager.ConnectionManager.get_connection', return_value=mock_conn):
            result = await DataService.get_table_data(request)
            
            assert result.status == "success"
            assert result.data[0] == [1, "John Doe"]
            assert result.data[1] == [2, "Jane Smith"]

    def test_format_results_static_method(self):
        """Test the static _format_results method."""
        rows = [(1, "John"), (2, "Jane")]
        columns = ["id", "name"]
        
        # Test JSON format
        result = DataService._format_results(rows, columns, "json")
        assert result[0]["id"] == 1
        assert result[0]["name"] == "John"
        
        # Test CSV format
        result = DataService._format_results(rows, columns, "csv")
        assert "csv" in result[0]
        csv_content = result[0]["csv"]
        assert "id,name" in csv_content
        assert "1,John" in csv_content
        
        # Test list format
        result = DataService._format_results(rows, columns, "list")
        assert result[0] == [1, "John"]
        assert result[1] == [2, "Jane"]

    def test_format_results_empty_data(self):
        """Test formatting empty data."""
        result = DataService._format_results([], ["id", "name"], "json")
        assert result is None

    def test_get_table_data_request_validation(self):
        """Test GetTableDataRequest validation."""
        # Test valid request
        request = GetTableDataRequest(
            connection_id=uuid4(),
            database="test-db",
            table_name="users",
            limit=100,
            offset=0
        )
        assert request.database == "test-db"
        assert request.table_name == "users"
        
        # Test invalid database name
        with pytest.raises(ValueError, match="Database name must start with a letter"):
            GetTableDataRequest(
                connection_id=uuid4(),
                database="123invalid",
                table_name="users",
                limit=100,
                offset=0
            )
        
        # Test invalid table name
        with pytest.raises(ValueError, match="Table name must start with a letter"):
            GetTableDataRequest(
                connection_id=uuid4(),
                database="test-db",
                table_name="123invalid",
                limit=100,
                offset=0
            )
