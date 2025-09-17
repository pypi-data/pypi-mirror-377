"""
Integration tests for MCP server integration.

These tests verify the complete MCP server functionality including tools and resources.
"""

import pytest
import asyncio
from uuid import uuid4
from unittest.mock import AsyncMock, MagicMock, patch

from src.mcp_tools.mcp_server import SQLServerMCPServer
from src.mcp_tools.create_connection_tool import CreateConnectionTool
from src.mcp_tools.execute_query_tool import ExecuteQueryTool
from src.mcp_tools.get_schema_tool import GetSchemaTool
from src.mcp_tools.list_databases_tool import ListDatabasesTool
from src.mcp_tools.get_table_data_tool import GetTableDataTool
from src.mcp_tools.resources import StatusResource, HistoryResource


class TestMCPServerIntegration:
    """Test complete MCP server integration."""

    @pytest.fixture
    def mcp_server(self):
        """Create MCP server instance."""
        return SQLServerMCPServer(host="127.0.0.1", port=8001)

    @pytest.fixture
    def mock_connection(self):
        """Create a mock database connection."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        return mock_conn, mock_cursor

    @pytest.mark.asyncio
    async def test_server_initialization(self, mcp_server):
        """Test MCP server initialization."""
        # Verify server properties
        assert mcp_server._server_id is not None
        assert mcp_server._start_time is not None
        assert mcp_server._history_resource is not None
        assert mcp_server._status_resource is not None
        
        # Verify tools are registered
        tools = mcp_server.get_tools()
        tool_names = [tool.name for tool in tools]
        expected_tools = [
            "create_connection",
            "execute_query", 
            "get_schema",
            "get_table_data",
            "list_databases"
        ]
        for expected_tool in expected_tools:
            assert expected_tool in tool_names

    @pytest.mark.asyncio
    async def test_server_tool_registration(self, mcp_server):
        """Test that all tools are properly registered."""
        tools = mcp_server.get_tools()
        
        # Verify each tool type
        tool_types = {
            "create_connection": CreateConnectionTool,
            "execute_query": ExecuteQueryTool,
            "get_schema": GetSchemaTool,
            "get_table_data": GetTableDataTool,
            "list_databases": ListDatabasesTool
        }
        
        for tool_name, expected_type in tool_types.items():
            tool = next((t for t in tools if t.name == tool_name), None)
            assert tool is not None
            assert isinstance(tool, expected_type)

    @pytest.mark.asyncio
    async def test_server_resource_registration(self, mcp_server):
        """Test that all resources are properly registered."""
        resources = mcp_server.get_resources()
        
        # Verify resource types
        resource_names = [resource.name for resource in resources]
        assert "status" in resource_names
        assert "history" in resource_names
        
        # Verify resource instances
        status_resource = next((r for r in resources if r.name == "status"), None)
        history_resource = next((r for r in resources if r.name == "history"), None)
        
        assert isinstance(status_resource, StatusResource)
        assert isinstance(history_resource, HistoryResource)

    @pytest.mark.asyncio
    async def test_connection_tool_integration(self, mcp_server, mock_connection):
        """Test connection tool integration with server."""
        mock_conn, mock_cursor = mock_connection
        
        with patch('pyodbc.connect', return_value=mock_conn):
            # Get connection tool
            tools = mcp_server.get_tools()
            connection_tool = next(t for t in tools if t.name == "create_connection")
            
            # Execute connection tool
            result = await connection_tool.run(
                server="test-server",
                database="test-db",
                trusted_connection=True
            )
            
            # Verify result
            assert result["status"] == "connected"
            assert "connection_id" in result

    @pytest.mark.asyncio
    async def test_query_tool_integration(self, mcp_server, mock_connection):
        """Test query tool integration with server."""
        mock_conn, mock_cursor = mock_connection
        
        # Mock query result
        mock_cursor.description = [("count",)]
        mock_cursor.fetchall.return_value = [(42,)]
        mock_cursor.rowcount = 1
        
        with patch('pyodbc.connect', return_value=mock_conn):
            # Get query tool
            tools = mcp_server.get_tools()
            query_tool = next(t for t in tools if t.name == "execute_query")
            
            # Execute query tool
            result = await query_tool.run(
                connection_id=str(uuid4()),
                query="SELECT COUNT(*) FROM users"
            )
            
            # Verify result
            assert result["status"] == "success"
            assert result["data"][0]["count"] == 42

    @pytest.mark.asyncio
    async def test_schema_tool_integration(self, mcp_server, mock_connection):
        """Test schema tool integration with server."""
        mock_conn, mock_cursor = mock_connection
        
        # Mock schema result
        mock_cursor.fetchall.side_effect = [
            [("dbo", "users")],  # Tables query
            [("id", "int", "NO", None, None, None)],  # Columns
        ]
        
        with patch('pyodbc.connect', return_value=mock_conn):
            # Get schema tool
            tools = mcp_server.get_tools()
            schema_tool = next(t for t in tools if t.name == "get_schema")
            
            # Execute schema tool
            result = await schema_tool.run(
                connection_id=str(uuid4()),
                database="test-db",
                table_name="users",
                include_columns=True
            )
            
            # Verify result
            assert result["status"] == "success"
            assert result["database_name"] == "test-db"
            assert len(result["tables"]) == 1

    @pytest.mark.asyncio
    async def test_status_resource_integration(self, mcp_server):
        """Test status resource integration with server."""
        # Get status resource
        resources = mcp_server.get_resources()
        status_resource = next(r for r in resources if r.name == "status")
        
        # Get status
        status = await status_resource.get()
        
        # Verify status structure
        assert "server_id" in status
        assert "status" in status
        assert "timestamp" in status
        assert "uptime_seconds" in status
        assert "active_connections" in status
        assert "total_connections_made" in status

    @pytest.mark.asyncio
    async def test_history_resource_integration(self, mcp_server):
        """Test history resource integration with server."""
        # Get history resource
        resources = mcp_server.get_resources()
        history_resource = next(r for r in resources if r.name == "history")
        
        # Add history entry
        await history_resource.add_entry("test_event", {"key": "value"})
        
        # Get history
        history = await history_resource.get()
        
        # Verify history structure
        assert len(history) == 1
        assert history[0]["event_type"] == "test_event"
        assert history[0]["details"]["key"] == "value"

    @pytest.mark.asyncio
    async def test_server_error_handling(self, mcp_server):
        """Test server error handling."""
        # Test with invalid tool parameters
        tools = mcp_server.get_tools()
        connection_tool = next(t for t in tools if t.name == "create_connection")
        
        # Execute with invalid parameters
        result = await connection_tool.run(
            server="",  # Invalid server name
            authentication="sql",
            username="test",
            password="test"
        )
        
        # Verify error handling
        assert result["status"] == "error"
        assert "error" in result["message"].lower()

    @pytest.mark.asyncio
    async def test_server_concurrent_operations(self, mcp_server, mock_connection):
        """Test server handling of concurrent operations."""
        mock_conn, mock_cursor = mock_connection
        
        # Mock query results
        mock_cursor.description = [("id",)]
        mock_cursor.fetchall.return_value = [(1,), (2,), (3,)]
        mock_cursor.rowcount = 3
        
        with patch('pyodbc.connect', return_value=mock_conn):
            # Get tools
            tools = mcp_server.get_tools()
            connection_tool = next(t for t in tools if t.name == "create_connection")
            query_tool = next(t for t in tools if t.name == "execute_query")
            
            # Create connection
            conn_result = await connection_tool.run(
                server="test-server",
                trusted_connection=True
            )
            connection_id = conn_result["connection_id"]
            
            # Execute multiple concurrent queries
            tasks = []
            for i in range(5):
                task = query_tool.run(
                    connection_id=connection_id,
                    query=f"SELECT {i} as id"
                )
                tasks.append(task)
            
            # Wait for all queries to complete
            results = await asyncio.gather(*tasks)
            
            # Verify all queries succeeded
            for result in results:
                assert result["status"] == "success"

    @pytest.mark.asyncio
    async def test_server_resource_cleanup(self, mcp_server):
        """Test server resource cleanup."""
        # Get history resource
        resources = mcp_server.get_resources()
        history_resource = next(r for r in resources if r.name == "history")
        
        # Add many history entries
        for i in range(1500):  # More than the 1000 limit
            await history_resource.add_entry(f"event_{i}", {"index": i})
        
        # Get history
        history = await history_resource.get()
        
        # Verify history is limited to 1000 entries
        assert len(history) == 1000
        assert history[0]["event_type"] == "event_500"  # First entry should be from index 500

    @pytest.mark.asyncio
    async def test_server_metadata(self, mcp_server):
        """Test server metadata and information."""
        # Verify server metadata
        assert mcp_server.name == "SQL Server MCP Server"
        assert mcp_server.version == "1.0.0"
        assert "comprehensive MCP server" in mcp_server.description
        
        # Verify server ID format
        assert len(str(mcp_server._server_id)) == 36  # UUID length
        
        # Verify start time
        assert mcp_server._start_time > 0
