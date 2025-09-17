"""
Unit tests for SchemaService.

These tests verify the individual functionality of the SchemaService class.
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

from src.models import SchemaRequest, SchemaResult, Table, Column, Index, Relationship
from src.services.schema_service import SchemaService


class TestSchemaService:
    """Test SchemaService functionality."""

    @pytest.fixture
    def mock_connection(self):
        """Create a mock database connection."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        return mock_conn, mock_cursor

    @pytest.fixture
    def schema_request(self):
        """Create test schema request."""
        return SchemaRequest(
            connection_id=uuid4(),
            database="test-db",
            include_columns=True,
            include_indexes=False,
            include_relationships=False
        )

    @pytest.mark.asyncio
    async def test_get_schema_success(self, schema_request, mock_connection):
        """Test successful schema retrieval."""
        mock_conn, mock_cursor = mock_connection
        
        # Mock table information
        mock_cursor.fetchall.side_effect = [
            [("dbo", "users")],  # Tables query
            [("id", "int", "NO", None, None, None), ("name", "varchar", "YES", 255, None, None)],  # Columns
        ]
        
        with patch('src.services.connection_manager.ConnectionManager.get_connection', return_value=mock_conn):
            result = await SchemaService.get_schema(schema_request)
            
            assert result.status == "success"
            assert result.database_name == "test-db"
            assert len(result.tables) == 1
            assert result.tables[0].name == "users"
            assert result.tables[0].schema == "dbo"
            assert len(result.tables[0].columns) == 2

    @pytest.mark.asyncio
    async def test_get_schema_connection_not_found(self, schema_request):
        """Test schema retrieval when connection is not found."""
        with patch('src.services.connection_manager.ConnectionManager.get_connection', return_value=None):
            result = await SchemaService.get_schema(schema_request)
            
            assert result.status == "error"
            assert "Connection not found" in result.message
            assert result.tables == []

    @pytest.mark.asyncio
    async def test_get_schema_database_error(self, schema_request, mock_connection):
        """Test schema retrieval when database error occurs."""
        mock_conn, mock_cursor = mock_connection
        
        # Mock database error
        mock_cursor.execute.side_effect = Exception("Database error")
        
        with patch('src.services.connection_manager.ConnectionManager.get_connection', return_value=mock_conn):
            result = await SchemaService.get_schema(schema_request)
            
            assert result.status == "error"
            assert "Database error" in result.message
            assert result.tables == []

    @pytest.mark.asyncio
    async def test_get_schema_specific_table(self, mock_connection):
        """Test schema retrieval for a specific table."""
        mock_conn, mock_cursor = mock_connection
        
        # Mock table information for specific table
        mock_cursor.fetchall.side_effect = [
            [("dbo", "users")],  # Tables query
            [("id", "int", "NO", None, None, None)],  # Columns
        ]
        
        request = SchemaRequest(
            connection_id=uuid4(),
            database="test-db",
            table_name="users",
            include_columns=True
        )
        
        with patch('src.services.connection_manager.ConnectionManager.get_connection', return_value=mock_conn):
            result = await SchemaService.get_schema(request)
            
            assert result.status == "success"
            assert len(result.tables) == 1
            assert result.tables[0].name == "users"

    @pytest.mark.asyncio
    async def test_get_schema_with_indexes(self, mock_connection):
        """Test schema retrieval including indexes."""
        mock_conn, mock_cursor = mock_connection
        
        # Mock table and index information
        mock_cursor.fetchall.side_effect = [
            [("dbo", "users")],  # Tables query
            [("id", "int", "NO", None, None, None)],  # Columns
            [("PK_users", "id", True, True)],  # Indexes
        ]
        
        request = SchemaRequest(
            connection_id=uuid4(),
            database="test-db",
            table_name="users",
            include_columns=True,
            include_indexes=True
        )
        
        with patch('src.services.connection_manager.ConnectionManager.get_connection', return_value=mock_conn):
            result = await SchemaService.get_schema(request)
            
            assert result.status == "success"
            table = result.tables[0]
            assert len(table.indexes) == 1
            assert table.indexes[0].name == "PK_users"
            assert table.indexes[0].is_unique
            assert table.indexes[0].is_clustered

    @pytest.mark.asyncio
    async def test_get_schema_with_relationships(self, mock_connection):
        """Test schema retrieval including relationships."""
        mock_conn, mock_cursor = mock_connection
        
        # Mock table and relationship information
        mock_cursor.fetchall.side_effect = [
            [("dbo", "orders")],  # Tables query
            [("id", "int", "NO", None, None, None), ("user_id", "int", "NO", None, None, None)],  # Columns
            [("FK_orders_users", "orders", "user_id", "users", "id", "CASCADE", "NO ACTION")],  # Relationships
        ]
        
        request = SchemaRequest(
            connection_id=uuid4(),
            database="test-db",
            table_name="orders",
            include_columns=True,
            include_relationships=True
        )
        
        with patch('src.services.connection_manager.ConnectionManager.get_connection', return_value=mock_conn):
            result = await SchemaService.get_schema(request)
            
            assert result.status == "success"
            table = result.tables[0]
            assert len(table.relationships) == 1
            rel = table.relationships[0]
            assert rel.name == "FK_orders_users"
            assert rel.from_table == "orders"
            assert rel.to_table == "users"
            assert rel.on_delete == "CASCADE"

    @pytest.mark.asyncio
    async def test_get_schema_with_row_counts(self, mock_connection):
        """Test schema retrieval including row counts."""
        mock_conn, mock_cursor = mock_connection
        
        # Mock table and row count information
        mock_cursor.fetchall.side_effect = [
            [("dbo", "users")],  # Tables query
            [("id", "int", "NO", None, None, None)],  # Columns
            [(1000,)],  # Row count
        ]
        
        request = SchemaRequest(
            connection_id=uuid4(),
            database="test-db",
            table_name="users",
            include_columns=True,
            include_row_counts=True
        )
        
        with patch('src.services.connection_manager.ConnectionManager.get_connection', return_value=mock_conn):
            result = await SchemaService.get_schema(request)
            
            assert result.status == "success"
            table = result.tables[0]
            assert table.row_count == 1000

    @pytest.mark.asyncio
    async def test_get_schema_with_data_sizes(self, mock_connection):
        """Test schema retrieval including data sizes."""
        mock_conn, mock_cursor = mock_connection
        
        # Mock table and data size information
        mock_cursor.fetchall.side_effect = [
            [("dbo", "users")],  # Tables query
            [("id", "int", "NO", None, None, None)],  # Columns
            [(1024,)],  # Data size in KB
        ]
        
        request = SchemaRequest(
            connection_id=uuid4(),
            database="test-db",
            table_name="users",
            include_columns=True,
            include_data_sizes=True
        )
        
        with patch('src.services.connection_manager.ConnectionManager.get_connection', return_value=mock_conn):
            result = await SchemaService.get_schema(request)
            
            assert result.status == "success"
            table = result.tables[0]
            assert table.data_size_kb == 1024

    @pytest.mark.asyncio
    async def test_get_schema_empty_database(self, mock_connection):
        """Test schema retrieval for empty database."""
        mock_conn, mock_cursor = mock_connection
        
        # Mock empty database
        mock_cursor.fetchall.return_value = []
        
        request = SchemaRequest(
            connection_id=uuid4(),
            database="test-db",
            include_columns=True
        )
        
        with patch('src.services.connection_manager.ConnectionManager.get_connection', return_value=mock_conn):
            result = await SchemaService.get_schema(request)
            
            assert result.status == "success"
            assert len(result.tables) == 0

    @pytest.mark.asyncio
    async def test_get_schema_unexpected_error(self, schema_request, mock_connection):
        """Test schema retrieval with unexpected error."""
        mock_conn, mock_cursor = mock_connection
        
        # Mock unexpected error
        mock_cursor.execute.side_effect = Exception("Unexpected error")
        
        with patch('src.services.connection_manager.ConnectionManager.get_connection', return_value=mock_conn):
            result = await SchemaService.get_schema(schema_request)
            
            assert result.status == "error"
            assert "unexpected error" in result.message.lower()

    @pytest.mark.asyncio
    async def test_get_columns_static_method(self, mock_connection):
        """Test the static _get_columns method."""
        mock_conn, mock_cursor = mock_connection
        
        # Mock column information
        mock_cursor.fetchall.side_effect = [
            [("id", "int", "NO", None, None, None), ("name", "varchar", "YES", 255, None, None)],  # Columns
            [("id",)],  # Primary keys
            [("user_id",)],  # Foreign keys
        ]
        
        columns = await SchemaService._get_columns(mock_cursor, "test-db", "dbo", "users")
        
        assert len(columns) == 2
        assert columns[0].name == "id"
        assert columns[0].data_type == "int"
        assert not columns[0].is_nullable
        assert columns[0].is_primary_key
        assert not columns[0].is_foreign_key
        
        assert columns[1].name == "name"
        assert columns[1].data_type == "varchar"
        assert columns[1].is_nullable
        assert not columns[1].is_primary_key
        assert not columns[1].is_foreign_key

    @pytest.mark.asyncio
    async def test_get_indexes_static_method(self, mock_connection):
        """Test the static _get_indexes method."""
        mock_conn, mock_cursor = mock_connection
        
        # Mock index information
        mock_cursor.fetchall.return_value = [
            ("PK_users", "id", True, True),
            ("IX_users_name", "name", False, False),
        ]
        
        indexes = await SchemaService._get_indexes(mock_cursor, "test-db", "dbo", "users")
        
        assert len(indexes) == 2
        assert indexes[0].name == "PK_users"
        assert indexes[0].columns == ["id"]
        assert indexes[0].is_unique
        assert indexes[0].is_clustered
        
        assert indexes[1].name == "IX_users_name"
        assert indexes[1].columns == ["name"]
        assert not indexes[1].is_unique
        assert not indexes[1].is_clustered

    @pytest.mark.asyncio
    async def test_get_relationships_static_method(self, mock_connection):
        """Test the static _get_relationships method."""
        mock_conn, mock_cursor = mock_connection
        
        # Mock relationship information
        mock_cursor.fetchall.return_value = [
            ("FK_orders_users", "orders", "user_id", "users", "id", "CASCADE", "NO ACTION"),
        ]
        
        relationships = await SchemaService._get_relationships(mock_cursor, "test-db", "dbo", "orders")
        
        assert len(relationships) == 1
        rel = relationships[0]
        assert rel.name == "FK_orders_users"
        assert rel.from_table == "orders"
        assert rel.from_column == "user_id"
        assert rel.to_table == "users"
        assert rel.to_column == "id"
        assert rel.on_delete == "CASCADE"
        assert rel.on_update == "NO ACTION"

    @pytest.mark.asyncio
    async def test_get_row_count_static_method(self, mock_connection):
        """Test the static _get_row_count method."""
        mock_conn, mock_cursor = mock_connection
        
        # Mock row count
        mock_cursor.fetchone.return_value = (1000,)
        
        row_count = await SchemaService._get_row_count(mock_cursor, "test-db", "dbo", "users")
        
        assert row_count == 1000

    @pytest.mark.asyncio
    async def test_get_data_size_static_method(self, mock_connection):
        """Test the static _get_data_size method."""
        mock_conn, mock_cursor = mock_connection
        
        # Mock data size
        mock_cursor.fetchone.return_value = (2048,)
        
        data_size = await SchemaService._get_data_size(mock_cursor, "test-db", "dbo", "users")
        
        assert data_size == 2048

    @pytest.mark.asyncio
    async def test_list_databases_success(self, mock_connection):
        """Test successful database listing."""
        mock_conn, mock_cursor = mock_connection
        
        # Mock database information
        mock_cursor.fetchall.return_value = [
            ("master", 1, None, 150, "SQL_Latin1_General_CP1_CI_AS", "2020-01-01"),
            ("test-db", 5, None, 150, "SQL_Latin1_General_CP1_CI_AS", "2020-01-01"),
        ]
        
        with patch('src.services.connection_manager.ConnectionManager.get_connection', return_value=mock_conn):
            databases = await SchemaService.list_databases(uuid4(), include_system_databases=True)
            
            assert len(databases) == 2
            assert databases[0].name == "master"
            assert databases[0].is_system_database
            assert databases[1].name == "test-db"
            assert not databases[1].is_system_database

    @pytest.mark.asyncio
    async def test_list_databases_connection_not_found(self):
        """Test database listing when connection is not found."""
        with patch('src.services.connection_manager.ConnectionManager.get_connection', return_value=None):
            databases = await SchemaService.list_databases(uuid4())
            
            assert len(databases) == 0

    @pytest.mark.asyncio
    async def test_list_databases_with_metadata(self, mock_connection):
        """Test database listing with metadata."""
        mock_conn, mock_cursor = mock_connection
        
        # Mock database information
        mock_cursor.fetchall.return_value = [
            ("test-db", 5, None, 150, "SQL_Latin1_General_CP1_CI_AS", "2020-01-01"),
        ]
        
        # Mock size query
        mock_cursor.fetchone.return_value = (1024.5,)
        
        with patch('src.services.connection_manager.ConnectionManager.get_connection', return_value=mock_conn):
            databases = await SchemaService.list_databases(uuid4(), include_metadata=True)
            
            assert len(databases) == 1
            assert databases[0].name == "test-db"
            assert databases[0].size_mb == 1024.5

    @pytest.mark.asyncio
    async def test_list_databases_error_handling(self, mock_connection):
        """Test database listing error handling."""
        mock_conn, mock_cursor = mock_connection
        
        # Mock database error
        mock_cursor.execute.side_effect = Exception("Database error")
        
        with patch('src.services.connection_manager.ConnectionManager.get_connection', return_value=mock_conn):
            databases = await SchemaService.list_databases(uuid4())
            
            assert len(databases) == 0
