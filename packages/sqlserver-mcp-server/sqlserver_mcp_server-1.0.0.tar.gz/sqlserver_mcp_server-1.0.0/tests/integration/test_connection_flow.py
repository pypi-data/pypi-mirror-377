"""
Integration tests for connection management flow.

These tests verify the complete connection lifecycle from creation to closure.
"""

import pytest
import asyncio
from uuid import uuid4
from unittest.mock import AsyncMock, MagicMock, patch

from src.models.connection import ConnectionConfig, ConnectionStatus
from src.services.connection_manager import ConnectionManager
from src.mcp_tools.create_connection_tool import CreateConnectionTool


class TestConnectionFlow:
    """Test complete connection management flow."""

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
        mock_conn.cursor.return_value = MagicMock()
        return mock_conn

    @pytest.mark.asyncio
    async def test_connection_creation_success(self, connection_params, mock_connection):
        """Test successful connection creation."""
        with patch('pyodbc.connect', return_value=mock_connection):
            # Create connection
            status = await ConnectionManager.create_connection(connection_params)
            
            # Verify connection status
            assert status.status == "connected"
            assert status.message == "Connection established successfully."
            assert status.active_connections > 0
            assert status.connection_time_ms is not None

    @pytest.mark.asyncio
    async def test_connection_creation_failure(self, connection_params):
        """Test connection creation failure."""
        with patch('pyodbc.connect', side_effect=Exception("Connection failed")):
            # Attempt to create connection
            status = await ConnectionManager.create_connection(connection_params)
            
            # Verify error status
            assert status.status == "error"
            assert "Connection failed" in status.message
            assert status.active_connections == 0

    @pytest.mark.asyncio
    async def test_connection_retrieval(self, connection_params, mock_connection):
        """Test connection retrieval by ID."""
        with patch('pyodbc.connect', return_value=mock_connection):
            # Create connection
            status = await ConnectionManager.create_connection(connection_params)
            connection_id = status.connection_id
            
            # Retrieve connection
            retrieved_conn = await ConnectionManager.get_connection(connection_id)
            
            # Verify connection was retrieved
            assert retrieved_conn is not None
            assert retrieved_conn == mock_connection

    @pytest.mark.asyncio
    async def test_connection_closure(self, connection_params, mock_connection):
        """Test connection closure."""
        with patch('pyodbc.connect', return_value=mock_connection):
            # Create connection
            status = await ConnectionManager.create_connection(connection_params)
            connection_id = status.connection_id
            
            # Close connection
            close_status = await ConnectionManager.close_connection(connection_id)
            
            # Verify connection was closed
            assert close_status.status == "disconnected"
            assert close_status.message == "Connection closed successfully."
            mock_connection.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_connection_status_tracking(self, connection_params, mock_connection):
        """Test connection status tracking."""
        with patch('pyodbc.connect', return_value=mock_connection):
            # Create connection
            status = await ConnectionManager.create_connection(connection_params)
            connection_id = status.connection_id
            
            # Get connection status
            retrieved_status = await ConnectionManager.get_connection_status(connection_id)
            
            # Verify status tracking
            assert retrieved_status is not None
            assert retrieved_status.connection_id == connection_id
            assert retrieved_status.status == "connected"

    @pytest.mark.asyncio
    async def test_multiple_connections(self, mock_connection):
        """Test managing multiple connections."""
        with patch('pyodbc.connect', return_value=mock_connection):
            # Create multiple connections
            params1 = ConnectionConfig(server="server1", trusted_connection=True)
            params2 = ConnectionConfig(server="server2", trusted_connection=True)
            
            status1 = await ConnectionManager.create_connection(params1)
            status2 = await ConnectionManager.create_connection(params2)
            
            # Verify both connections exist
            assert status1.connection_id != status2.connection_id
            assert status1.active_connections == 2
            assert status2.active_connections == 2
            
            # List all connections
            all_connections = await ConnectionManager.list_all_connections()
            assert len(all_connections) == 2

    @pytest.mark.asyncio
    async def test_mcp_tool_integration(self, connection_params, mock_connection):
        """Test MCP tool integration with connection manager."""
        with patch('pyodbc.connect', return_value=mock_connection):
            # Create MCP tool
            tool = CreateConnectionTool()
            
            # Execute tool
            result = await tool.run(
                server=connection_params.server,
                database=connection_params.database,
                username=connection_params.username,
                password=connection_params.password,
                authentication=connection_params.authentication,
                connection_timeout=connection_params.connection_timeout,
                pool_size=connection_params.pool_size
            )
            
            # Verify tool result
            assert result["status"] == "connected"
            assert "connection_id" in result
            assert result["active_connections"] > 0

    @pytest.mark.asyncio
    async def test_connection_pool_management(self, mock_connection):
        """Test connection pool management."""
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
    async def test_connection_timeout_handling(self, connection_params):
        """Test connection timeout handling."""
        with patch('pyodbc.connect', side_effect=Exception("Connection timeout")):
            # Attempt connection with timeout
            status = await ConnectionManager.create_connection(connection_params)
            
            # Verify timeout is handled
            assert status.status == "error"
            assert "timeout" in status.message.lower() or "failed" in status.message.lower()

    @pytest.mark.asyncio
    async def test_connection_cleanup_on_error(self, connection_params, mock_connection):
        """Test connection cleanup when errors occur."""
        with patch('pyodbc.connect', return_value=mock_connection):
            # Create connection
            status = await ConnectionManager.create_connection(connection_params)
            connection_id = status.connection_id
            
            # Simulate connection error
            mock_connection.cursor.side_effect = Exception("Database error")
            
            # Attempt to use connection
            retrieved_conn = await ConnectionManager.get_connection(connection_id)
            assert retrieved_conn is not None
            
            # Close connection to cleanup
            close_status = await ConnectionManager.close_connection(connection_id)
            assert close_status.status == "disconnected"
