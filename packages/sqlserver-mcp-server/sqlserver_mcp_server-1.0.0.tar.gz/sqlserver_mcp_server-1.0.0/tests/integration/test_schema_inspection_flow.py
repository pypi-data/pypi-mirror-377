"""
Integration tests for schema inspection flow.

These tests verify the complete schema inspection lifecycle from request to result.
"""

import pytest
import asyncio
from uuid import uuid4
from unittest.mock import AsyncMock, MagicMock, patch

from src.models.connection import ConnectionConfig, ConnectionStatus
from src.models import SchemaRequest, SchemaResult, Table, Column, Index, Relationship
from src.services.connection_manager import ConnectionManager
from src.services.schema_service import SchemaService
from src.mcp_tools.get_schema_tool import GetSchemaTool


class TestSchemaInspectionFlow:
    """Test complete schema inspection flow."""

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
    async def test_database_schema_retrieval(self, established_connection):
        """Test retrieving schema for entire database."""
        connection_id, mock_conn, mock_cursor = established_connection
        
        # Mock table information
        mock_cursor.fetchall.side_effect = [
            [("dbo", "users"), ("dbo", "orders")],  # Tables query
            [("id", "int", "NO", None, None, None), ("name", "varchar", "YES", 255, None, None)],  # Users columns
            [("id", "int", "NO", None, None, None), ("user_id", "int", "NO", None, None, None)],  # Orders columns
        ]
        
        # Create schema request
        request = SchemaRequest(
            connection_id=connection_id,
            database="test-db",
            include_columns=True,
            include_indexes=False,
            include_relationships=False
        )
        
        # Execute schema retrieval
        result = await SchemaService.get_schema(request)
        
        # Verify result
        assert result.status == "success"
        assert result.database_name == "test-db"
        assert len(result.tables) == 2
        
        # Verify table structure
        users_table = next(t for t in result.tables if t.name == "users")
        assert users_table.schema == "dbo"
        assert len(users_table.columns) == 2
        assert users_table.columns[0].name == "id"
        assert users_table.columns[0].data_type == "int"
        assert not users_table.columns[0].is_nullable

    @pytest.mark.asyncio
    async def test_single_table_schema_retrieval(self, established_connection):
        """Test retrieving schema for a single table."""
        connection_id, mock_conn, mock_cursor = established_connection
        
        # Mock table information for single table
        mock_cursor.fetchall.side_effect = [
            [("dbo", "users")],  # Tables query
            [("id", "int", "NO", None, None, None), ("name", "varchar", "YES", 255, None, None)],  # Columns
        ]
        
        # Create schema request for specific table
        request = SchemaRequest(
            connection_id=connection_id,
            database="test-db",
            table_name="users",
            include_columns=True
        )
        
        # Execute schema retrieval
        result = await SchemaService.get_schema(request)
        
        # Verify result
        assert result.status == "success"
        assert len(result.tables) == 1
        assert result.tables[0].name == "users"

    @pytest.mark.asyncio
    async def test_schema_with_indexes(self, established_connection):
        """Test schema retrieval including indexes."""
        connection_id, mock_conn, mock_cursor = established_connection
        
        # Mock table and index information
        mock_cursor.fetchall.side_effect = [
            [("dbo", "users")],  # Tables query
            [("id", "int", "NO", None, None, None)],  # Columns
            [("PK_users", "id", True, True)],  # Indexes
        ]
        
        # Create schema request with indexes
        request = SchemaRequest(
            connection_id=connection_id,
            database="test-db",
            table_name="users",
            include_columns=True,
            include_indexes=True
        )
        
        # Execute schema retrieval
        result = await SchemaService.get_schema(request)
        
        # Verify result includes indexes
        assert result.status == "success"
        table = result.tables[0]
        assert len(table.indexes) == 1
        assert table.indexes[0].name == "PK_users"
        assert table.indexes[0].is_unique
        assert table.indexes[0].is_clustered

    @pytest.mark.asyncio
    async def test_schema_with_relationships(self, established_connection):
        """Test schema retrieval including relationships."""
        connection_id, mock_conn, mock_cursor = established_connection
        
        # Mock table and relationship information
        mock_cursor.fetchall.side_effect = [
            [("dbo", "orders")],  # Tables query
            [("id", "int", "NO", None, None, None), ("user_id", "int", "NO", None, None, None)],  # Columns
            [("FK_orders_users", "orders", "user_id", "users", "id", "CASCADE", "NO ACTION")],  # Relationships
        ]
        
        # Create schema request with relationships
        request = SchemaRequest(
            connection_id=connection_id,
            database="test-db",
            table_name="orders",
            include_columns=True,
            include_relationships=True
        )
        
        # Execute schema retrieval
        result = await SchemaService.get_schema(request)
        
        # Verify result includes relationships
        assert result.status == "success"
        table = result.tables[0]
        assert len(table.relationships) == 1
        rel = table.relationships[0]
        assert rel.name == "FK_orders_users"
        assert rel.from_table == "orders"
        assert rel.to_table == "users"
        assert rel.on_delete == "CASCADE"

    @pytest.mark.asyncio
    async def test_schema_with_row_counts(self, established_connection):
        """Test schema retrieval including row counts."""
        connection_id, mock_conn, mock_cursor = established_connection
        
        # Mock table and row count information
        mock_cursor.fetchall.side_effect = [
            [("dbo", "users")],  # Tables query
            [("id", "int", "NO", None, None, None)],  # Columns
            [(1000,)],  # Row count
        ]
        
        # Create schema request with row counts
        request = SchemaRequest(
            connection_id=connection_id,
            database="test-db",
            table_name="users",
            include_columns=True,
            include_row_counts=True
        )
        
        # Execute schema retrieval
        result = await SchemaService.get_schema(request)
        
        # Verify result includes row count
        assert result.status == "success"
        table = result.tables[0]
        assert table.row_count == 1000

    @pytest.mark.asyncio
    async def test_schema_error_handling(self, established_connection):
        """Test schema retrieval error handling."""
        connection_id, mock_conn, mock_cursor = established_connection
        
        # Mock database error
        mock_cursor.execute.side_effect = Exception("Database access denied")
        
        # Create schema request
        request = SchemaRequest(
            connection_id=connection_id,
            database="test-db",
            include_columns=True
        )
        
        # Execute schema retrieval
        result = await SchemaService.get_schema(request)
        
        # Verify error handling
        assert result.status == "error"
        assert "access denied" in result.message.lower() or "failed" in result.message.lower()

    @pytest.mark.asyncio
    async def test_schema_validation(self, established_connection):
        """Test schema request validation."""
        connection_id, mock_conn, mock_cursor = established_connection
        
        # Test invalid database name
        with pytest.raises(ValueError, match="Database name must start with a letter"):
            request = SchemaRequest(
                connection_id=connection_id,
                database="123invalid",
                include_columns=True
            )
        
        # Test invalid table name
        with pytest.raises(ValueError, match="Table name must start with a letter"):
            request = SchemaRequest(
                connection_id=connection_id,
                database="test-db",
                table_name="123invalid",
                include_columns=True
            )

    @pytest.mark.asyncio
    async def test_mcp_tool_integration(self, established_connection):
        """Test MCP tool integration with schema service."""
        connection_id, mock_conn, mock_cursor = established_connection
        
        # Mock table information
        mock_cursor.fetchall.side_effect = [
            [("dbo", "users")],  # Tables query
            [("id", "int", "NO", None, None, None)],  # Columns
        ]
        
        # Create MCP tool
        tool = GetSchemaTool()
        
        # Execute tool
        result = await tool.run(
            connection_id=str(connection_id),
            database="test-db",
            table_name="users",
            include_columns=True
        )
        
        # Verify tool result
        assert result["status"] == "success"
        assert result["database_name"] == "test-db"
        assert len(result["tables"]) == 1
        assert result["tables"][0]["name"] == "users"

    @pytest.mark.asyncio
    async def test_schema_performance_tracking(self, established_connection):
        """Test schema retrieval performance tracking."""
        connection_id, mock_conn, mock_cursor = established_connection
        
        # Mock table information
        mock_cursor.fetchall.side_effect = [
            [("dbo", "users")],  # Tables query
            [("id", "int", "NO", None, None, None)],  # Columns
        ]
        
        # Create schema request
        request = SchemaRequest(
            connection_id=connection_id,
            database="test-db",
            table_name="users",
            include_columns=True
        )
        
        # Execute schema retrieval
        result = await SchemaService.get_schema(request)
        
        # Verify performance tracking
        assert result.status == "success"
        assert result.retrieval_time_ms is not None
        assert result.retrieval_time_ms >= 0

    @pytest.mark.asyncio
    async def test_empty_database_schema(self, established_connection):
        """Test schema retrieval for empty database."""
        connection_id, mock_conn, mock_cursor = established_connection
        
        # Mock empty database
        mock_cursor.fetchall.return_value = []
        
        # Create schema request
        request = SchemaRequest(
            connection_id=connection_id,
            database="test-db",
            include_columns=True
        )
        
        # Execute schema retrieval
        result = await SchemaService.get_schema(request)
        
        # Verify empty database handling
        assert result.status == "success"
        assert len(result.tables) == 0
        assert result.database_name == "test-db"
