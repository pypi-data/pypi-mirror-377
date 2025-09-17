"""
Unit tests for ConnectionManager service.

These tests verify the individual functionality of the ConnectionManager class.
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

from src.models.connection import ConnectionConfig, ConnectionStatus
from src.services.connection_manager import ConnectionManager


class TestConnectionManager:
    """Test ConnectionManager service functionality."""

    @pytest.fixture
    def connection_params(self):
        """Create test connection parameters."""
        return ConnectionConfig(
            server="test-server",
            database="test-db",
            username="test-user",
            password="test-pass",
            trusted_connection=False,
            connection_timeout=30,
            pool_size=5
        )

    @pytest.fixture
    def mock_connection(self):
        """Create a mock database connection."""
        mock_conn = MagicMock()
        mock_conn.cursor.return_value = MagicMock()
        return mock_conn

    def test_connection_string_building_sql_auth(self, connection_params):
        """Test connection string building for SQL authentication."""
        conn_str = ConnectionManager._build_connection_string(connection_params)
        
        assert "DRIVER={ODBC Driver 17 for SQL Server}" in conn_str
        assert "SERVER=test-server" in conn_str
        assert "DATABASE=test-db" in conn_str
        assert "UID=test-user" in conn_str
        assert "PWD=test-pass" in conn_str
        assert "Connection Timeout=30" in conn_str

    def test_connection_string_building_windows_auth(self):
        """Test connection string building for Windows authentication."""
        params = ConnectionConfig(
            server="test-server",
            database="test-db",
            trusted_connection=True,
            connection_timeout=30
        )
        
        conn_str = ConnectionManager._build_connection_string(params)
        
        assert "DRIVER={ODBC Driver 17 for SQL Server}" in conn_str
        assert "SERVER=test-server" in conn_str
        assert "DATABASE=test-db" in conn_str
        assert "Trusted_Connection=yes" in conn_str
        assert "Connection Timeout=30" in conn_str

    def test_connection_string_building_no_database(self):
        """Test connection string building without database."""
        params = ConnectionConfig(
            server="test-server",
            trusted_connection=True
        )
        
        conn_str = ConnectionManager._build_connection_string(params)
        
        assert "DRIVER={ODBC Driver 17 for SQL Server}" in conn_str
        assert "SERVER=test-server" in conn_str
        assert "DATABASE=" not in conn_str
        assert "Trusted_Connection=yes" in conn_str

    @pytest.mark.asyncio
    async def test_create_connection_success(self, connection_params, mock_connection):
        """Test successful connection creation."""
        with patch('pyodbc.connect', return_value=mock_connection):
            status = await ConnectionManager.create_connection(connection_params)
            
            assert status.status == "connected"
            assert status.message == "Connection established successfully."
            assert status.active_connections > 0
            assert status.connection_time_ms is not None
            assert status.connection_time_ms >= 0

    @pytest.mark.asyncio
    async def test_create_connection_failure(self, connection_params):
        """Test connection creation failure."""
        with patch('pyodbc.connect', side_effect=Exception("Connection failed")):
            status = await ConnectionManager.create_connection(connection_params)
            
            assert status.status == "error"
            assert "Connection failed" in status.message
            assert status.active_connections == 0
            assert status.connection_time_ms is not None

    @pytest.mark.asyncio
    async def test_get_connection_existing(self, connection_params, mock_connection):
        """Test retrieving an existing connection."""
        with patch('pyodbc.connect', return_value=mock_connection):
            # Create connection
            status = await ConnectionManager.create_connection(connection_params)
            connection_id = status.connection_id
            
            # Retrieve connection
            retrieved_conn = await ConnectionManager.get_connection(connection_id)
            
            assert retrieved_conn is not None
            assert retrieved_conn == mock_connection

    @pytest.mark.asyncio
    async def test_get_connection_nonexistent(self):
        """Test retrieving a non-existent connection."""
        connection_id = uuid4()
        retrieved_conn = await ConnectionManager.get_connection(connection_id)
        
        assert retrieved_conn is None

    @pytest.mark.asyncio
    async def test_close_connection_existing(self, connection_params, mock_connection):
        """Test closing an existing connection."""
        with patch('pyodbc.connect', return_value=mock_connection):
            # Create connection
            status = await ConnectionManager.create_connection(connection_params)
            connection_id = status.connection_id
            
            # Close connection
            close_status = await ConnectionManager.close_connection(connection_id)
            
            assert close_status.status == "disconnected"
            assert close_status.message == "Connection closed successfully."
            mock_connection.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_close_connection_nonexistent(self):
        """Test closing a non-existent connection."""
        connection_id = uuid4()
        close_status = await ConnectionManager.close_connection(connection_id)
        
        assert close_status.status == "error"
        assert close_status.message == "Connection not found."

    @pytest.mark.asyncio
    async def test_get_connection_status_existing(self, connection_params, mock_connection):
        """Test getting status of an existing connection."""
        with patch('pyodbc.connect', return_value=mock_connection):
            # Create connection
            status = await ConnectionManager.create_connection(connection_params)
            connection_id = status.connection_id
            
            # Get status
            retrieved_status = await ConnectionManager.get_connection_status(connection_id)
            
            assert retrieved_status is not None
            assert retrieved_status.connection_id == connection_id
            assert retrieved_status.status == "connected"

    @pytest.mark.asyncio
    async def test_get_connection_status_nonexistent(self):
        """Test getting status of a non-existent connection."""
        connection_id = uuid4()
        status = await ConnectionManager.get_connection_status(connection_id)
        
        assert status is None

    @pytest.mark.asyncio
    async def test_list_all_connections(self, mock_connection):
        """Test listing all connections."""
        with patch('pyodbc.connect', return_value=mock_connection):
            # Create multiple connections
            params1 = ConnectionConfig(server="server1", trusted_connection=True)
            params2 = ConnectionConfig(server="server2", trusted_connection=True)
            
            status1 = await ConnectionManager.create_connection(params1)
            status2 = await ConnectionManager.create_connection(params2)
            
            # List all connections
            all_connections = await ConnectionManager.list_all_connections()
            
            assert len(all_connections) == 2
            assert status1.connection_id in all_connections
            assert status2.connection_id in all_connections

    @pytest.mark.asyncio
    async def test_list_all_connections_empty(self):
        """Test listing connections when none exist."""
        all_connections = await ConnectionManager.list_all_connections()
        assert len(all_connections) == 0

    @pytest.mark.asyncio
    async def test_connection_pool_tracking(self, mock_connection):
        """Test connection pool size tracking."""
        with patch('pyodbc.connect', return_value=mock_connection):
            # Create connection with specific pool size
            params = ConnectionConfig(
                server="test-server",
                pool_size=3,
                trusted_connection=True
            )
            
            status = await ConnectionManager.create_connection(params)
            
            # Verify pool size is tracked
            assert status.active_connections <= params.pool_size

    @pytest.mark.asyncio
    async def test_concurrent_connection_creation(self, mock_connection):
        """Test concurrent connection creation."""
        with patch('pyodbc.connect', return_value=mock_connection):
            # Create multiple connections concurrently
            params_list = [
                ConnectionConfig(server=f"server{i}", trusted_connection=True)
                for i in range(5)
            ]
            
            tasks = [
                ConnectionManager.create_connection(params)
                for params in params_list
            ]
            
            results = await asyncio.gather(*tasks)
            
            # Verify all connections were created
            assert len(results) == 5
            for result in results:
                assert result.status == "connected"
            
            # Verify all connections are tracked
            all_connections = await ConnectionManager.list_all_connections()
            assert len(all_connections) == 5

    @pytest.mark.asyncio
    async def test_connection_cleanup_on_error(self, connection_params, mock_connection):
        """Test connection cleanup when errors occur."""
        with patch('pyodbc.connect', return_value=mock_connection):
            # Create connection
            status = await ConnectionManager.create_connection(connection_params)
            connection_id = status.connection_id
            
            # Simulate connection error
            mock_connection.cursor.side_effect = Exception("Database error")
            
            # Connection should still exist in manager
            retrieved_conn = await ConnectionManager.get_connection(connection_id)
            assert retrieved_conn is not None
            
            # Close connection to cleanup
            close_status = await ConnectionManager.close_connection(connection_id)
            assert close_status.status == "disconnected"

    def test_connection_string_validation(self):
        """Test connection string validation."""
        # Test with valid parameters
        params = ConnectionConfig(
            server="valid-server",
            database="valid-db",
            trusted_connection=True
        )
        
        conn_str = ConnectionManager._build_connection_string(params)
        assert conn_str is not None
        assert len(conn_str) > 0

    def test_connection_string_sql_auth_validation(self):
        """Test connection string validation for SQL authentication."""
        # Test with missing username/password for SQL auth
        params = ConnectionConfig(
            server="test-server",
            authentication="sql"
        )
        
        with pytest.raises(ValueError, match="Username and password are required"):
            ConnectionManager._build_connection_string(params)
