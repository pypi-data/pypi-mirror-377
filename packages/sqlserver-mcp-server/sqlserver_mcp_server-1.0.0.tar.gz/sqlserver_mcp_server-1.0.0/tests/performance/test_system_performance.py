"""
System-wide performance tests.

These tests measure overall system performance, resource utilization,
and end-to-end performance under various load conditions.
"""

import pytest
import asyncio
import time
import psutil
import os
from unittest.mock import Mock, patch

from src.mcp_tools.mcp_server import SQLServerMCPServer
from src.services.connection_manager import ConnectionManager
from src.services.query_executor import QueryExecutor
from src.services.schema_service import SchemaService
from src.services.data_service import DataService
from src.models.connection import ConnectionConfig
from src.lib.performance import get_performance_monitor, get_resource_manager


class TestSystemPerformance:
    """Test overall system performance."""
    
    @pytest.fixture
    def system_components(self):
        """Create system components for testing."""
        connection_manager = ConnectionManager()
        query_executor = QueryExecutor(connection_manager)
        schema_service = SchemaService(connection_manager)
        data_service = DataService(connection_manager, query_executor)
        
        return {
            'connection_manager': connection_manager,
            'query_executor': query_executor,
            'schema_service': schema_service,
            'data_service': data_service
        }
    
    @pytest.fixture
    def mock_connection(self):
        """Create mock database connection."""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_conn.cursor.return_value = mock_cursor
        return mock_conn, mock_cursor
    
    @pytest.mark.performance
    @pytest.mark.benchmark
    async def test_system_startup_performance(self):
        """Test system startup performance."""
        # Measure MCP server startup time
        start_time = time.time()
        
        with patch('pyodbc.connect') as mock_connect:
            mock_connect.return_value = Mock()
            
            server = SQLServerMCPServer()
            startup_time = time.time() - start_time
            
            # System should start in less than 2 seconds
            assert startup_time < 2.0
    
    @pytest.mark.performance
    @pytest.mark.benchmark
    async def test_system_memory_usage(self, system_components):
        """Test system memory usage under load."""
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        connection_manager = system_components['connection_manager']
        
        with patch('pyodbc.connect') as mock_connect:
            mock_connect.return_value = Mock()
            
            # Create multiple connections
            config = ConnectionConfig(
                server="localhost",
                database="test_db",
                trusted_connection=True,
                pool_size=10
            )
            
            connection_ids = []
            for _ in range(20):
                conn_id = await connection_manager.create_connection(config)
                connection_ids.append(conn_id)
            
            # Check memory usage
            current_memory = process.memory_info().rss / 1024 / 1024  # MB
            memory_increase = current_memory - initial_memory
            
            # Memory increase should be reasonable (less than 200MB for 20 connections)
            assert memory_increase < 200.0
            
            # Cleanup
            for conn_id in connection_ids:
                await connection_manager.close_connection(conn_id)
    
    @pytest.mark.performance
    @pytest.mark.benchmark
    async def test_concurrent_operations_performance(self, system_components, mock_connection):
        """Test performance under concurrent operations."""
        mock_conn, mock_cursor = mock_connection
        
        # Mock query results
        mock_cursor.fetchall.return_value = [("test", 1)]
        mock_cursor.description = [("name",), ("id",)]
        
        connection_manager = system_components['connection_manager']
        query_executor = system_components['query_executor']
        
        with patch('pyodbc.connect') as mock_connect:
            mock_connect.return_value = mock_conn
            
            # Create connection
            config = ConnectionConfig(
                server="localhost",
                database="test_db",
                trusted_connection=True,
                pool_size=20
            )
            connection_id = await connection_manager.create_connection(config)
            
            async def mixed_operation():
                """Perform mixed operations."""
                # Get connection
                conn = await connection_manager.get_connection(connection_id)
                
                # Execute query
                from src.models.query import QueryRequest
                query_request = QueryRequest(
                    query="SELECT name, id FROM test_table",
                    timeout=30
                )
                result = await query_executor.execute_query(connection_id, query_request)
                
                # Return connection
                await connection_manager.return_connection(connection_id, conn)
                
                return result
            
            # Execute 100 mixed operations concurrently
            start_time = time.time()
            tasks = [mixed_operation() for _ in range(100)]
            results = await asyncio.gather(*tasks)
            total_time = time.time() - start_time
            
            # Should handle 100 operations in less than 5 seconds
            assert total_time < 5.0
            assert len(results) == 100
            assert all(r.success for r in results)
    
    @pytest.mark.performance
    @pytest.mark.benchmark
    async def test_system_throughput(self, system_components, mock_connection):
        """Test system throughput under sustained load."""
        mock_conn, mock_cursor = mock_connection
        
        # Mock query results
        mock_cursor.fetchall.return_value = [("throughput", 1)]
        mock_cursor.description = [("name",), ("id",)]
        
        connection_manager = system_components['connection_manager']
        query_executor = system_components['query_executor']
        
        with patch('pyodbc.connect') as mock_connect:
            mock_connect.return_value = mock_conn
            
            # Create connection
            config = ConnectionConfig(
                server="localhost",
                database="test_db",
                trusted_connection=True,
                pool_size=50
            )
            connection_id = await connection_manager.create_connection(config)
            
            async def throughput_operation():
                """Simple throughput operation."""
                from src.models.query import QueryRequest
                query_request = QueryRequest(
                    query="SELECT name, id FROM test_table",
                    timeout=30
                )
                return await query_executor.execute_query(connection_id, query_request)
            
            # Measure throughput over 10 seconds
            start_time = time.time()
            operations_completed = 0
            
            while time.time() - start_time < 10.0:
                # Execute batch of operations
                tasks = [throughput_operation() for _ in range(10)]
                results = await asyncio.gather(*tasks)
                operations_completed += len(results)
            
            total_time = time.time() - start_time
            throughput = operations_completed / total_time
            
            # Should achieve at least 10 operations per second
            assert throughput >= 10.0
    
    @pytest.mark.performance
    @pytest.mark.benchmark
    async def test_system_latency(self, system_components, mock_connection):
        """Test system latency under various conditions."""
        mock_conn, mock_cursor = mock_connection
        
        # Mock query results
        mock_cursor.fetchall.return_value = [("latency", 1)]
        mock_cursor.description = [("name",), ("id",)]
        
        connection_manager = system_components['connection_manager']
        query_executor = system_components['query_executor']
        
        with patch('pyodbc.connect') as mock_connect:
            mock_connect.return_value = mock_conn
            
            # Create connection
            config = ConnectionConfig(
                server="localhost",
                database="test_db",
                trusted_connection=True,
                pool_size=10
            )
            connection_id = await connection_manager.create_connection(config)
            
            from src.models.query import QueryRequest
            query_request = QueryRequest(
                query="SELECT name, id FROM test_table",
                timeout=30
            )
            
            # Measure latency for 100 operations
            latencies = []
            for _ in range(100):
                start_time = time.time()
                result = await query_executor.execute_query(connection_id, query_request)
                latency = time.time() - start_time
                latencies.append(latency)
            
            # Calculate latency statistics
            avg_latency = sum(latencies) / len(latencies)
            p95_latency = sorted(latencies)[int(len(latencies) * 0.95)]
            p99_latency = sorted(latencies)[int(len(latencies) * 0.99)]
            
            # Latency requirements
            assert avg_latency < 0.1  # Average < 100ms
            assert p95_latency < 0.2  # 95th percentile < 200ms
            assert p99_latency < 0.5  # 99th percentile < 500ms
    
    @pytest.mark.performance
    @pytest.mark.benchmark
    async def test_system_resource_utilization(self, system_components):
        """Test system resource utilization under load."""
        process = psutil.Process(os.getpid())
        
        # Get initial resource usage
        initial_cpu = process.cpu_percent()
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        connection_manager = system_components['connection_manager']
        
        with patch('pyodbc.connect') as mock_connect:
            mock_connect.return_value = Mock()
            
            # Create load
            config = ConnectionConfig(
                server="localhost",
                database="test_db",
                trusted_connection=True,
                pool_size=20
            )
            
            async def resource_intensive_operation():
                """Resource intensive operation."""
                conn_id = await connection_manager.create_connection(config)
                conn = await connection_manager.get_connection(conn_id)
                await asyncio.sleep(0.01)  # Simulate work
                await connection_manager.return_connection(conn_id, conn)
                await connection_manager.close_connection(conn_id)
            
            # Execute resource intensive operations
            start_time = time.time()
            tasks = [resource_intensive_operation() for _ in range(50)]
            await asyncio.gather(*tasks)
            total_time = time.time() - start_time
            
            # Check resource usage
            current_cpu = process.cpu_percent()
            current_memory = process.memory_info().rss / 1024 / 1024  # MB
            
            cpu_increase = current_cpu - initial_cpu
            memory_increase = current_memory - initial_memory
            
            # Resource usage should be reasonable
            assert cpu_increase < 50.0  # CPU increase < 50%
            assert memory_increase < 100.0  # Memory increase < 100MB
    
    @pytest.mark.performance
    @pytest.mark.benchmark
    async def test_system_stability_under_load(self, system_components, mock_connection):
        """Test system stability under sustained load."""
        mock_conn, mock_cursor = mock_connection
        
        # Mock query results
        mock_cursor.fetchall.return_value = [("stability", 1)]
        mock_cursor.description = [("name",), ("id",)]
        
        connection_manager = system_components['connection_manager']
        query_executor = system_components['query_executor']
        
        with patch('pyodbc.connect') as mock_connect:
            mock_connect.return_value = mock_conn
            
            # Create connection
            config = ConnectionConfig(
                server="localhost",
                database="test_db",
                trusted_connection=True,
                pool_size=30
            )
            connection_id = await connection_manager.create_connection(config)
            
            from src.models.query import QueryRequest
            query_request = QueryRequest(
                query="SELECT name, id FROM test_table",
                timeout=30
            )
            
            # Run sustained load for 30 seconds
            start_time = time.time()
            successful_operations = 0
            failed_operations = 0
            
            while time.time() - start_time < 30.0:
                try:
                    result = await query_executor.execute_query(connection_id, query_request)
                    if result.success:
                        successful_operations += 1
                    else:
                        failed_operations += 1
                except Exception:
                    failed_operations += 1
                
                # Small delay to prevent overwhelming
                await asyncio.sleep(0.01)
            
            total_operations = successful_operations + failed_operations
            success_rate = successful_operations / total_operations if total_operations > 0 else 0
            
            # System should maintain high stability
            assert success_rate >= 0.95  # 95% success rate
            assert total_operations >= 100  # At least 100 operations in 30 seconds
    
    @pytest.mark.performance
    @pytest.mark.benchmark
    async def test_performance_monitoring_impact(self, system_components):
        """Test impact of performance monitoring on system performance."""
        connection_manager = system_components['connection_manager']
        performance_monitor = get_performance_monitor()
        resource_manager = get_resource_manager()
        
        with patch('pyodbc.connect') as mock_connect:
            mock_connect.return_value = Mock()
            
            config = ConnectionConfig(
                server="localhost",
                database="test_db",
                trusted_connection=True,
                pool_size=10
            )
            
            # Test without monitoring (baseline)
            start_time = time.time()
            for _ in range(100):
                conn_id = await connection_manager.create_connection(config)
                await connection_manager.close_connection(conn_id)
            baseline_time = time.time() - start_time
            
            # Test with monitoring (already enabled)
            start_time = time.time()
            for _ in range(100):
                conn_id = await connection_manager.create_connection(config)
                await connection_manager.close_connection(conn_id)
            monitoring_time = time.time() - start_time
            
            # Get system health
            health = await resource_manager.get_system_health()
            
            # Monitoring overhead should be minimal
            overhead_ratio = monitoring_time / baseline_time
            assert overhead_ratio < 1.2  # Less than 20% overhead
            
            # System should report good health
            assert health['health_score'] >= 0.8  # Health score >= 80%
