"""
Performance test configuration and fixtures.

This module provides common fixtures and configuration for performance tests.
"""

import pytest
import asyncio
import time
from unittest.mock import Mock, patch

from src.services.connection_manager import ConnectionManager
from src.services.query_executor import QueryExecutor
from src.services.schema_service import SchemaService
from src.services.data_service import DataService
from src.models.connection import ConnectionConfig
from src.lib.performance import get_performance_monitor, get_query_cache


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def performance_monitor():
    """Get performance monitor instance."""
    return get_performance_monitor()


@pytest.fixture
def query_cache():
    """Get query cache instance."""
    return get_query_cache()


@pytest.fixture
def connection_config():
    """Create test connection configuration."""
    return ConnectionConfig(
        server="localhost",
        database="test_db",
        trusted_connection=True,
        pool_size=10,
        connection_timeout=30
    )


@pytest.fixture
def mock_connection():
    """Create mock database connection."""
    mock_conn = Mock()
    mock_cursor = Mock()
    mock_conn.cursor.return_value = mock_cursor
    return mock_conn, mock_cursor


@pytest.fixture
def connection_manager():
    """Create connection manager for testing."""
    return ConnectionManager()


@pytest.fixture
def query_executor(connection_manager):
    """Create query executor for testing."""
    return QueryExecutor(connection_manager)


@pytest.fixture
def schema_service(connection_manager):
    """Create schema service for testing."""
    return SchemaService(connection_manager)


@pytest.fixture
def data_service(connection_manager, query_executor):
    """Create data service for testing."""
    return DataService(connection_manager, query_executor)


@pytest.fixture
def system_components(connection_manager, query_executor, schema_service, data_service):
    """Create all system components for testing."""
    return {
        'connection_manager': connection_manager,
        'query_executor': query_executor,
        'schema_service': schema_service,
        'data_service': data_service
    }


@pytest.fixture
def benchmark_config():
    """Benchmark configuration for performance tests."""
    return {
        'min_time': 0.1,  # Minimum time for benchmark
        'max_time': 10.0,  # Maximum time for benchmark
        'warmup_runs': 3,  # Number of warmup runs
        'benchmark_runs': 10,  # Number of benchmark runs
        'tolerance': 0.1  # 10% tolerance for performance variations
    }


@pytest.fixture
def load_test_config():
    """Load test configuration."""
    return {
        'concurrent_users': 50,
        'operations_per_user': 100,
        'ramp_up_time': 10,  # seconds
        'test_duration': 60,  # seconds
        'think_time': 0.1  # seconds between operations
    }


@pytest.fixture
def performance_thresholds():
    """Performance thresholds for tests."""
    return {
        'connection_creation': 1.0,  # seconds
        'query_execution': 0.1,  # seconds
        'schema_retrieval': 0.5,  # seconds
        'data_retrieval': 0.2,  # seconds
        'concurrent_operations': 5.0,  # seconds for 100 operations
        'memory_usage': 200.0,  # MB
        'cpu_usage': 50.0,  # percentage
        'throughput': 10.0,  # operations per second
        'latency_p95': 0.2,  # seconds
        'latency_p99': 0.5,  # seconds
        'success_rate': 0.95  # 95%
    }


@pytest.fixture(autouse=True)
def reset_performance_monitoring():
    """Reset performance monitoring between tests."""
    monitor = get_performance_monitor()
    cache = get_query_cache()
    
    # Clear metrics
    monitor.metrics.clear()
    monitor.counters.clear()
    monitor.timers.clear()
    
    # Clear cache
    asyncio.create_task(cache.clear())
    
    yield
    
    # Cleanup after test
    monitor.metrics.clear()
    monitor.counters.clear()
    monitor.timers.clear()
    asyncio.create_task(cache.clear())


@pytest.fixture
def mock_sql_server():
    """Mock SQL Server for testing."""
    with patch('pyodbc.connect') as mock_connect:
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn
        
        # Default mock responses
        mock_cursor.fetchall.return_value = [("test", 1)]
        mock_cursor.description = [("name",), ("id",)]
        
        yield mock_conn, mock_cursor


@pytest.fixture
def performance_data():
    """Generate performance test data."""
    return {
        'small_dataset': [(f"row_{i}", i) for i in range(100)],
        'medium_dataset': [(f"row_{i}", i, f"data_{i}") for i in range(1000)],
        'large_dataset': [(f"row_{i}", i, f"data_{i}" * 10) for i in range(10000)],
        'wide_dataset': [(f"row_{i}", i, f"col1_{i}", f"col2_{i}", f"col3_{i}", f"col4_{i}", f"col5_{i}") for i in range(1000)]
    }


@pytest.fixture
def benchmark_timer():
    """Benchmark timer utility."""
    class BenchmarkTimer:
        def __init__(self):
            self.start_time = None
            self.end_time = None
        
        def start(self):
            self.start_time = time.time()
        
        def stop(self):
            self.end_time = time.time()
            return self.elapsed
        
        @property
        def elapsed(self):
            if self.start_time is None:
                return 0.0
            end_time = self.end_time or time.time()
            return end_time - self.start_time
    
    return BenchmarkTimer()


# Performance test markers
pytest_plugins = []


def pytest_configure(config):
    """Configure pytest for performance tests."""
    config.addinivalue_line(
        "markers", "performance: mark test as a performance test"
    )
    config.addinivalue_line(
        "markers", "benchmark: mark test as a benchmark test"
    )
    config.addinivalue_line(
        "markers", "load: mark test as a load test"
    )
    config.addinivalue_line(
        "markers", "stress: mark test as a stress test"
    )
    config.addinivalue_line(
        "markers", "memory: mark test as a memory test"
    )
    config.addinivalue_line(
        "markers", "cpu: mark test as a CPU test"
    )


def pytest_collection_modifyitems(config, items):
    """Modify test collection for performance tests."""
    for item in items:
        # Add performance marker to all tests in performance directory
        if "performance" in str(item.fspath):
            item.add_marker(pytest.mark.performance)
        
        # Add timeout for performance tests
        if item.get_closest_marker("performance"):
            item.add_marker(pytest.mark.timeout(300))  # 5 minutes timeout
