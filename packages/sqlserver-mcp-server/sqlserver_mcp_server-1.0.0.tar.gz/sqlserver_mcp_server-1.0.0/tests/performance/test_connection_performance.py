"""
Performance tests for connection management.

These tests measure connection creation, pooling, and management performance.
"""

import pytest
import asyncio
import time
from unittest.mock import Mock, patch
from concurrent.futures import ThreadPoolExecutor

from src.services.connection_manager import ConnectionManager, ConnectionPool
from src.models.connection import ConnectionConfig
from src.lib.performance import get_performance_monitor


class TestConnectionPerformance:
    """Test connection management performance."""
    
    @pytest.fixture
    def connection_config(self):
        """Create test connection configuration."""
        return ConnectionConfig(
            server="localhost",
            database="test_db",
            trusted_connection=True,
            pool_size=10
        )
    
    @pytest.fixture
    def connection_manager(self):
        """Create connection manager for testing."""
        return ConnectionManager()
    
    @pytest.mark.performance
    @pytest.mark.benchmark
    async def test_connection_creation_performance(self, connection_manager, connection_config):
        """Test connection creation performance."""
        with patch('pyodbc.connect') as mock_connect:
            mock_connect.return_value = Mock()
            
            # Measure connection creation time
            start_time = time.time()
            connection_id = await connection_manager.create_connection(connection_config)
            creation_time = time.time() - start_time
            
            # Should create connection in less than 1 second
            assert creation_time < 1.0
            assert connection_id is not None
    
    @pytest.mark.performance
    @pytest.mark.benchmark
    async def test_connection_pool_performance(self, connection_manager, connection_config):
        """Test connection pool performance under load."""
        with patch('pyodbc.connect') as mock_connect:
            mock_connect.return_value = Mock()
            
            # Create connection
            connection_id = await connection_manager.create_connection(connection_config)
            
            # Test concurrent connection requests
            async def get_connection():
                return await connection_manager.get_connection(connection_id)
            
            # Measure time for 100 concurrent requests
            start_time = time.time()
            tasks = [get_connection() for _ in range(100)]
            connections = await asyncio.gather(*tasks)
            total_time = time.time() - start_time
            
            # Should handle 100 requests in less than 5 seconds
            assert total_time < 5.0
            assert len(connections) == 100
    
    @pytest.mark.performance
    @pytest.mark.benchmark
    async def test_connection_pool_scaling(self, connection_config):
        """Test connection pool scaling performance."""
        with patch('pyodbc.connect') as mock_connect:
            mock_connect.return_value = Mock()
            
            # Test different pool sizes
            pool_sizes = [5, 10, 20, 50]
            results = {}
            
            for pool_size in pool_sizes:
                config = ConnectionConfig(
                    server="localhost",
                    database="test_db",
                    trusted_connection=True,
                    pool_size=pool_size
                )
                
                pool = ConnectionPool(config, pool_size)
                await pool.initialize()
                
                # Measure time to get all connections
                start_time = time.time()
                connections = []
                for _ in range(pool_size):
                    conn = await pool.get_connection()
                    connections.append(conn)
                total_time = time.time() - start_time
                
                results[pool_size] = total_time
                
                # Cleanup
                await pool.close_all()
            
            # Larger pools should not be significantly slower
            assert results[50] < results[5] * 3
    
    @pytest.mark.performance
    @pytest.mark.benchmark
    async def test_connection_health_check_performance(self, connection_manager, connection_config):
        """Test connection health check performance."""
        with patch('pyodbc.connect') as mock_connect:
            mock_conn = Mock()
            mock_cursor = Mock()
            mock_conn.cursor.return_value = mock_cursor
            mock_connect.return_value = mock_conn
            
            # Create connection
            connection_id = await connection_manager.create_connection(connection_config)
            
            # Measure health check time
            start_time = time.time()
            is_healthy = await connection_manager.health_check(connection_id)
            health_check_time = time.time() - start_time
            
            # Health check should complete in less than 500ms
            assert health_check_time < 0.5
            assert is_healthy is True
    
    @pytest.mark.performance
    @pytest.mark.benchmark
    async def test_concurrent_connection_creation(self, connection_config):
        """Test concurrent connection creation performance."""
        with patch('pyodbc.connect') as mock_connect:
            mock_connect.return_value = Mock()
            
            async def create_connection():
                manager = ConnectionManager()
                return await manager.create_connection(connection_config)
            
            # Create 10 connections concurrently
            start_time = time.time()
            tasks = [create_connection() for _ in range(10)]
            connection_ids = await asyncio.gather(*tasks)
            total_time = time.time() - start_time
            
            # Should create 10 connections in less than 3 seconds
            assert total_time < 3.0
            assert len(connection_ids) == 10
            assert all(cid is not None for cid in connection_ids)
    
    @pytest.mark.performance
    @pytest.mark.benchmark
    async def test_connection_cleanup_performance(self, connection_manager, connection_config):
        """Test connection cleanup performance."""
        with patch('pyodbc.connect') as mock_connect:
            mock_conn = Mock()
            mock_connect.return_value = mock_conn
            
            # Create multiple connections
            connection_ids = []
            for _ in range(10):
                conn_id = await connection_manager.create_connection(connection_config)
                connection_ids.append(conn_id)
            
            # Measure cleanup time
            start_time = time.time()
            for conn_id in connection_ids:
                await connection_manager.close_connection(conn_id)
            cleanup_time = time.time() - start_time
            
            # Should cleanup 10 connections in less than 2 seconds
            assert cleanup_time < 2.0
    
    @pytest.mark.performance
    @pytest.mark.benchmark
    async def test_connection_pool_memory_usage(self, connection_config):
        """Test connection pool memory usage."""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        with patch('pyodbc.connect') as mock_connect:
            mock_connect.return_value = Mock()
            
            # Create large pool
            config = ConnectionConfig(
                server="localhost",
                database="test_db",
                trusted_connection=True,
                pool_size=100
            )
            
            pool = ConnectionPool(config, 100)
            await pool.initialize()
            
            # Check memory usage
            current_memory = process.memory_info().rss / 1024 / 1024  # MB
            memory_increase = current_memory - initial_memory
            
            # Memory increase should be reasonable (less than 50MB for 100 connections)
            assert memory_increase < 50.0
            
            # Cleanup
            await pool.close_all()
    
    @pytest.mark.performance
    @pytest.mark.benchmark
    async def test_connection_pool_stress(self, connection_config):
        """Test connection pool under stress conditions."""
        with patch('pyodbc.connect') as mock_connect:
            mock_connect.return_value = Mock()
            
            config = ConnectionConfig(
                server="localhost",
                database="test_db",
                trusted_connection=True,
                pool_size=20
            )
            
            pool = ConnectionPool(config, 20)
            await pool.initialize()
            
            # Stress test: rapid get/return cycles
            async def stress_cycle():
                conn = await pool.get_connection()
                await asyncio.sleep(0.001)  # Simulate work
                await pool.return_connection(conn)
            
            start_time = time.time()
            tasks = [stress_cycle() for _ in range(1000)]
            await asyncio.gather(*tasks)
            total_time = time.time() - start_time
            
            # Should handle 1000 cycles in less than 10 seconds
            assert total_time < 10.0
            
            # Cleanup
            await pool.close_all()
    
    @pytest.mark.performance
    @pytest.mark.benchmark
    async def test_performance_monitoring_overhead(self, connection_manager, connection_config):
        """Test that performance monitoring doesn't add significant overhead."""
        with patch('pyodbc.connect') as mock_connect:
            mock_connect.return_value = Mock()
            
            # Test without monitoring
            start_time = time.time()
            connection_id = await connection_manager.create_connection(connection_config)
            time_without_monitoring = time.time() - start_time
            
            # Test with monitoring (already enabled)
            start_time = time.time()
            connection_id2 = await connection_manager.create_connection(connection_config)
            time_with_monitoring = time.time() - start_time
            
            # Monitoring overhead should be less than 10%
            overhead_ratio = time_with_monitoring / time_without_monitoring
            assert overhead_ratio < 1.1
