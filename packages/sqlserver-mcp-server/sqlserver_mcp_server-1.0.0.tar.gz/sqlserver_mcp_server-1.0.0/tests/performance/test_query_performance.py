"""
Performance tests for query execution.

These tests measure query execution performance, caching effectiveness,
and concurrent query handling.
"""

import pytest
import asyncio
import time
from unittest.mock import Mock, patch

from src.services.query_executor import QueryExecutor
from src.services.connection_manager import ConnectionManager
from src.models.query import QueryRequest
from src.lib.performance import get_performance_monitor, get_query_cache


class TestQueryPerformance:
    """Test query execution performance."""
    
    @pytest.fixture
    def connection_manager(self):
        """Create connection manager for testing."""
        return ConnectionManager()
    
    @pytest.fixture
    def query_executor(self, connection_manager):
        """Create query executor for testing."""
        return QueryExecutor(connection_manager)
    
    @pytest.fixture
    def mock_connection(self):
        """Create mock database connection."""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_conn.cursor.return_value = mock_cursor
        return mock_conn, mock_cursor
    
    @pytest.mark.performance
    @pytest.mark.benchmark
    async def test_simple_query_performance(self, query_executor, mock_connection):
        """Test simple query execution performance."""
        mock_conn, mock_cursor = mock_connection
        
        # Mock query result
        mock_cursor.fetchall.return_value = [("test", 1), ("test2", 2)]
        mock_cursor.description = [("name",), ("id",)]
        
        with patch.object(query_executor.connection_manager, 'get_connection', return_value=mock_conn):
            query_request = QueryRequest(
                query="SELECT name, id FROM test_table",
                timeout=30
            )
            
            # Measure query execution time
            start_time = time.time()
            result = await query_executor.execute_query("test_conn", query_request)
            execution_time = time.time() - start_time
            
            # Simple query should execute in less than 100ms
            assert execution_time < 0.1
            assert result.success is True
            assert len(result.data) == 2
    
    @pytest.mark.performance
    @pytest.mark.benchmark
    async def test_large_result_set_performance(self, query_executor, mock_connection):
        """Test performance with large result sets."""
        mock_conn, mock_cursor = mock_connection
        
        # Mock large result set (1000 rows)
        large_result = [(f"row_{i}", i) for i in range(1000)]
        mock_cursor.fetchall.return_value = large_result
        mock_cursor.description = [("name",), ("id",)]
        
        with patch.object(query_executor.connection_manager, 'get_connection', return_value=mock_conn):
            query_request = QueryRequest(
                query="SELECT name, id FROM large_table",
                timeout=30
            )
            
            # Measure query execution time
            start_time = time.time()
            result = await query_executor.execute_query("test_conn", query_request)
            execution_time = time.time() - start_time
            
            # Large result set should process in less than 1 second
            assert execution_time < 1.0
            assert result.success is True
            assert len(result.data) == 1000
    
    @pytest.mark.performance
    @pytest.mark.benchmark
    async def test_concurrent_query_execution(self, query_executor, mock_connection):
        """Test concurrent query execution performance."""
        mock_conn, mock_cursor = mock_connection
        
        # Mock query result
        mock_cursor.fetchall.return_value = [("test", 1)]
        mock_cursor.description = [("name",), ("id",)]
        
        with patch.object(query_executor.connection_manager, 'get_connection', return_value=mock_conn):
            async def execute_query():
                query_request = QueryRequest(
                    query="SELECT name, id FROM test_table",
                    timeout=30
                )
                return await query_executor.execute_query("test_conn", query_request)
            
            # Execute 50 queries concurrently
            start_time = time.time()
            tasks = [execute_query() for _ in range(50)]
            results = await asyncio.gather(*tasks)
            total_time = time.time() - start_time
            
            # Should handle 50 concurrent queries in less than 2 seconds
            assert total_time < 2.0
            assert len(results) == 50
            assert all(r.success for r in results)
    
    @pytest.mark.performance
    @pytest.mark.benchmark
    async def test_parameterized_query_performance(self, query_executor, mock_connection):
        """Test parameterized query performance."""
        mock_conn, mock_cursor = mock_connection
        
        # Mock query result
        mock_cursor.fetchall.return_value = [("test", 1)]
        mock_cursor.description = [("name",), ("id",)]
        
        with patch.object(query_executor.connection_manager, 'get_connection', return_value=mock_conn):
            query_request = QueryRequest(
                query="SELECT name, id FROM test_table WHERE id = ?",
                parameters=[("id", 1, "int")],
                timeout=30
            )
            
            # Measure parameterized query execution time
            start_time = time.time()
            result = await query_executor.execute_query("test_conn", query_request)
            execution_time = time.time() - start_time
            
            # Parameterized query should execute in less than 100ms
            assert execution_time < 0.1
            assert result.success is True
    
    @pytest.mark.performance
    @pytest.mark.benchmark
    async def test_query_cache_performance(self, query_executor, mock_connection):
        """Test query cache performance."""
        mock_conn, mock_cursor = mock_connection
        
        # Mock query result
        mock_cursor.fetchall.return_value = [("cached", 1)]
        mock_cursor.description = [("name",), ("id",)]
        
        with patch.object(query_executor.connection_manager, 'get_connection', return_value=mock_conn):
            query_request = QueryRequest(
                query="SELECT name, id FROM test_table",
                timeout=30
            )
            
            # First execution (cache miss)
            start_time = time.time()
            result1 = await query_executor.execute_query("test_conn", query_request)
            first_execution_time = time.time() - start_time
            
            # Second execution (cache hit)
            start_time = time.time()
            result2 = await query_executor.execute_query("test_conn", query_request)
            second_execution_time = time.time() - start_time
            
            # Cached query should be significantly faster
            assert second_execution_time < first_execution_time * 0.5
            assert result1.success is True
            assert result2.success is True
    
    @pytest.mark.performance
    @pytest.mark.benchmark
    async def test_query_timeout_performance(self, query_executor, mock_connection):
        """Test query timeout handling performance."""
        mock_conn, mock_cursor = mock_connection
        
        # Mock slow query
        async def slow_fetchall():
            await asyncio.sleep(2)  # Simulate slow query
            return [("slow", 1)]
        
        mock_cursor.fetchall.side_effect = slow_fetchall
        mock_cursor.description = [("name",), ("id",)]
        
        with patch.object(query_executor.connection_manager, 'get_connection', return_value=mock_conn):
            query_request = QueryRequest(
                query="SELECT name, id FROM slow_table",
                timeout=1  # 1 second timeout
            )
            
            # Measure timeout handling
            start_time = time.time()
            result = await query_executor.execute_query("test_conn", query_request)
            execution_time = time.time() - start_time
            
            # Should timeout in approximately 1 second
            assert 0.9 <= execution_time <= 1.5
            assert result.success is False
            assert "timeout" in result.error_message.lower()
    
    @pytest.mark.performance
    @pytest.mark.benchmark
    async def test_query_memory_usage(self, query_executor, mock_connection):
        """Test query execution memory usage."""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        mock_conn, mock_cursor = mock_connection
        
        # Mock large result set
        large_result = [(f"row_{i}", i, f"data_{i}" * 100) for i in range(10000)]
        mock_cursor.fetchall.return_value = large_result
        mock_cursor.description = [("name",), ("id",), ("data",)]
        
        with patch.object(query_executor.connection_manager, 'get_connection', return_value=mock_conn):
            query_request = QueryRequest(
                query="SELECT name, id, data FROM large_table",
                timeout=30
            )
            
            # Execute query
            result = await query_executor.execute_query("test_conn", query_request)
            
            # Check memory usage
            current_memory = process.memory_info().rss / 1024 / 1024  # MB
            memory_increase = current_memory - initial_memory
            
            # Memory increase should be reasonable (less than 100MB for 10k rows)
            assert memory_increase < 100.0
            assert result.success is True
    
    @pytest.mark.performance
    @pytest.mark.benchmark
    async def test_query_error_handling_performance(self, query_executor, mock_connection):
        """Test query error handling performance."""
        mock_conn, mock_cursor = mock_connection
        
        # Mock query error
        mock_cursor.execute.side_effect = Exception("SQL Error")
        
        with patch.object(query_executor.connection_manager, 'get_connection', return_value=mock_conn):
            query_request = QueryRequest(
                query="INVALID SQL QUERY",
                timeout=30
            )
            
            # Measure error handling time
            start_time = time.time()
            result = await query_executor.execute_query("test_conn", query_request)
            execution_time = time.time() - start_time
            
            # Error handling should be fast (less than 100ms)
            assert execution_time < 0.1
            assert result.success is False
            assert "error" in result.error_message.lower()
    
    @pytest.mark.performance
    @pytest.mark.benchmark
    async def test_query_batch_performance(self, query_executor, mock_connection):
        """Test batch query execution performance."""
        mock_conn, mock_cursor = mock_connection
        
        # Mock query results
        mock_cursor.fetchall.return_value = [("batch", 1)]
        mock_cursor.description = [("name",), ("id",)]
        
        with patch.object(query_executor.connection_manager, 'get_connection', return_value=mock_conn):
            queries = [
                QueryRequest(query="SELECT name, id FROM table1", timeout=30),
                QueryRequest(query="SELECT name, id FROM table2", timeout=30),
                QueryRequest(query="SELECT name, id FROM table3", timeout=30),
                QueryRequest(query="SELECT name, id FROM table4", timeout=30),
                QueryRequest(query="SELECT name, id FROM table5", timeout=30),
            ]
            
            # Execute batch of queries
            start_time = time.time()
            tasks = [
                query_executor.execute_query("test_conn", query)
                for query in queries
            ]
            results = await asyncio.gather(*tasks)
            total_time = time.time() - start_time
            
            # Batch execution should be efficient
            assert total_time < 1.0
            assert len(results) == 5
            assert all(r.success for r in results)
    
    @pytest.mark.performance
    @pytest.mark.benchmark
    async def test_performance_monitoring_overhead(self, query_executor, mock_connection):
        """Test that performance monitoring doesn't add significant overhead."""
        mock_conn, mock_cursor = mock_connection
        
        # Mock query result
        mock_cursor.fetchall.return_value = [("test", 1)]
        mock_cursor.description = [("name",), ("id",)]
        
        with patch.object(query_executor.connection_manager, 'get_connection', return_value=mock_conn):
            query_request = QueryRequest(
                query="SELECT name, id FROM test_table",
                timeout=30
            )
            
            # Execute query multiple times to get average
            times = []
            for _ in range(10):
                start_time = time.time()
                result = await query_executor.execute_query("test_conn", query_request)
                execution_time = time.time() - start_time
                times.append(execution_time)
            
            # Average execution time should be consistent
            avg_time = sum(times) / len(times)
            assert avg_time < 0.1
            assert all(r.success for r in [result])
