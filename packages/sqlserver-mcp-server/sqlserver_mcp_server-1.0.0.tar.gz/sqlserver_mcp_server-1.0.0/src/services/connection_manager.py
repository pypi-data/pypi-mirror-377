"""
Connection management service for SQL Server MCP Server.

This module provides connection pooling, health monitoring,
and lifecycle management for database connections.
"""

import asyncio
import time
import uuid
from typing import Dict, Optional, List, Any
from datetime import datetime, timedelta
import pyodbc
import structlog

from ..models.connection import ConnectionConfig, ConnectionStatus, ConnectionHealth, ConnectionMetadata
from ..lib.exceptions import ConnectionError, AuthenticationError, TimeoutError
from ..lib.performance import get_performance_monitor, performance_monitor
from ..lib.metrics import get_metrics_collector, counter, gauge, timer


logger = structlog.get_logger(__name__)


class ConnectionPool:
    """Manages a pool of database connections."""
    
    def __init__(self, config: ConnectionConfig, pool_size: int = 10):
        """Initialize connection pool."""
        self.config = config
        self.pool_size = pool_size
        self.connections: List[pyodbc.Connection] = []
        self.available_connections: List[pyodbc.Connection] = []
        self.connection_times: Dict[pyodbc.Connection, datetime] = {}
        self.lock = asyncio.Lock()
        self.connection_string = config.to_connection_string()
        
    async def initialize(self) -> None:
        """Initialize the connection pool."""
        async with self.lock:
            try:
                # Create initial connections
                for _ in range(min(2, self.pool_size)):  # Start with 2 connections
                    conn = await self._create_connection()
                    self.connections.append(conn)
                    self.available_connections.append(conn)
                    self.connection_times[conn] = datetime.utcnow()
                
                logger.info("Connection pool initialized", 
                           pool_size=len(self.connections),
                           available=len(self.available_connections))
                           
            except Exception as e:
                logger.error("Failed to initialize connection pool", error=str(e))
                raise ConnectionError(f"Failed to initialize connection pool: {e}")
    
    async def _create_connection(self) -> pyodbc.Connection:
        """Create a new database connection."""
        try:
            # Run in thread pool since pyodbc is synchronous
            loop = asyncio.get_event_loop()
            conn = await loop.run_in_executor(
                None, 
                pyodbc.connect, 
                self.connection_string
            )
            
            # Configure connection
            conn.timeout = self.config.connection_timeout
            conn.autocommit = False
            
            logger.debug("Created new database connection")
            return conn
            
        except pyodbc.Error as e:
            logger.error("Failed to create database connection", error=str(e))
            if "Login failed" in str(e):
                raise AuthenticationError(f"Authentication failed: {e}")
            elif "timeout" in str(e).lower():
                raise TimeoutError(f"Connection timeout: {e}")
            else:
                raise ConnectionError(f"Failed to create connection: {e}")
    
    async def get_connection(self) -> pyodbc.Connection:
        """Get an available connection from the pool."""
        async with self.lock:
            # Try to get an available connection
            if self.available_connections:
                conn = self.available_connections.pop()
                # Check if connection is still valid
                if await self._is_connection_valid(conn):
                    return conn
                else:
                    # Remove invalid connection
                    self.connections.remove(conn)
                    if conn in self.connection_times:
                        del self.connection_times[conn]
            
            # Create new connection if pool not full
            if len(self.connections) < self.pool_size:
                conn = await self._create_connection()
                self.connections.append(conn)
                self.connection_times[conn] = datetime.utcnow()
                return conn
            
            # Wait for available connection
            while not self.available_connections:
                await asyncio.sleep(0.1)
            
            conn = self.available_connections.pop()
            return conn
    
    async def return_connection(self, conn: pyodbc.Connection) -> None:
        """Return a connection to the pool."""
        async with self.lock:
            if conn in self.connections and conn not in self.available_connections:
                self.available_connections.append(conn)
    
    async def _is_connection_valid(self, conn: pyodbc.Connection) -> bool:
        """Check if a connection is still valid."""
        try:
            # Run in thread pool
            loop = asyncio.get_event_loop()
            cursor = await loop.run_in_executor(None, conn.cursor)
            await loop.run_in_executor(None, cursor.execute, "SELECT 1")
            await loop.run_in_executor(None, cursor.close)
            return True
        except Exception:
            return False
    
    async def close_all(self) -> None:
        """Close all connections in the pool."""
        async with self.lock:
            for conn in self.connections:
                try:
                    conn.close()
                except Exception as e:
                    logger.warning("Error closing connection", error=str(e))
            
            self.connections.clear()
            self.available_connections.clear()
            self.connection_times.clear()
            
            logger.info("All connections closed")


class ConnectionManager:
    """Manages database connections and connection pools."""
    
    def __init__(self):
        """Initialize connection manager."""
        self.pools: Dict[str, ConnectionPool] = {}
        self.connection_statuses: Dict[str, ConnectionStatus] = {}
        self.connection_health: Dict[str, ConnectionHealth] = {}
        self.connection_metadata: Dict[str, ConnectionMetadata] = {}
        self.lock = asyncio.Lock()
        self.performance_monitor = get_performance_monitor()
    
    @performance_monitor(get_performance_monitor(), "create_connection")
    async def create_connection(self, config: ConnectionConfig) -> str:
        """Create a new database connection."""
        connection_id = f"conn_{uuid.uuid4().hex[:8]}"
        
        try:
            # Create connection pool
            pool = ConnectionPool(config, config.pool_size)
            await pool.initialize()
            
            # Store pool and status
            async with self.lock:
                self.pools[connection_id] = pool
                
                # Create status
                status = ConnectionStatus(
                    connection_id=connection_id,
                    connected=True,
                    server=config.server,
                    database=config.database,
                    authentication_method=self._get_auth_method(config),
                    pool_status={
                        "total": config.pool_size,
                        "available": config.pool_size,
                        "active": 0
                    },
                    response_time_ms=0.0,
                    uptime_seconds=0.0
                )
                self.connection_statuses[connection_id] = status
                
                # Create health tracking
                health = ConnectionHealth(
                    response_time_ms=0.0,
                    error_count=0,
                    uptime_seconds=0.0
                )
                self.connection_health[connection_id] = health
                
                # Create metadata
                metadata = ConnectionMetadata(
                    server_version=None,  # Will be populated later
                    driver_version=pyodbc.version
                )
                self.connection_metadata[connection_id] = metadata
            
            logger.info("Database connection created", 
                       connection_id=connection_id,
                       server=config.server,
                       database=config.database)
            
            return connection_id
            
        except Exception as e:
            logger.error("Failed to create database connection", 
                        connection_id=connection_id,
                        error=str(e))
            raise ConnectionError(f"Failed to create connection: {e}")
    
    def _get_auth_method(self, config: ConnectionConfig) -> str:
        """Get authentication method description."""
        if config.trusted_connection:
            return "Windows Authentication"
        else:
            return "SQL Server Authentication"
    
    @performance_monitor(get_performance_monitor(), "get_connection")
    async def get_connection(self, connection_id: str) -> pyodbc.Connection:
        """Get a database connection from the pool."""
        start_time = time.time()
        
        async with self.lock:
            if connection_id not in self.pools:
                raise ConnectionError(f"Connection {connection_id} not found")
            
            pool = self.pools[connection_id]
        
        try:
            conn = await pool.get_connection()
            
            # Record wait time
            wait_time = time.time() - start_time
            await self.performance_monitor.record_metric("connection_wait_time", wait_time)
            
            # Record metrics
            timer("connection_wait_time", wait_time, {"connection_id": connection_id})
            counter("connections_acquired", 1.0, {"connection_id": connection_id})
            
            # Update status
            async with self.lock:
                if connection_id in self.connection_statuses:
                    status = self.connection_statuses[connection_id]
                    status.pool_status["active"] += 1
                    status.pool_status["available"] -= 1
                    status.last_activity = datetime.utcnow()
                    
                    # Update pool metrics
                    gauge("connection_pool_active", status.pool_status["active"], {"connection_id": connection_id})
                    gauge("connection_pool_available", status.pool_status["available"], {"connection_id": connection_id})
            
            return conn
            
        except Exception as e:
            logger.error("Failed to get connection", 
                        connection_id=connection_id,
                        error=str(e))
            raise ConnectionError(f"Failed to get connection: {e}")
    
    async def return_connection(self, connection_id: str, conn: pyodbc.Connection) -> None:
        """Return a database connection to the pool."""
        async with self.lock:
            if connection_id not in self.pools:
                logger.warning("Attempted to return connection to non-existent pool",
                             connection_id=connection_id)
                return
            
            pool = self.pools[connection_id]
        
        try:
            await pool.return_connection(conn)
            
            # Update status
            async with self.lock:
                if connection_id in self.connection_statuses:
                    status = self.connection_statuses[connection_id]
                    status.pool_status["active"] -= 1
                    status.pool_status["available"] += 1
                    status.last_activity = datetime.utcnow()
            
        except Exception as e:
            logger.error("Failed to return connection", 
                        connection_id=connection_id,
                        error=str(e))
    
    async def close_connection(self, connection_id: str) -> None:
        """Close a database connection and remove it from the manager."""
        async with self.lock:
            if connection_id not in self.pools:
                logger.warning("Attempted to close non-existent connection",
                             connection_id=connection_id)
                return
            
            pool = self.pools[connection_id]
        
        try:
            await pool.close_all()
            
            # Remove from manager
            async with self.lock:
                del self.pools[connection_id]
                if connection_id in self.connection_statuses:
                    del self.connection_statuses[connection_id]
                if connection_id in self.connection_health:
                    del self.connection_health[connection_id]
                if connection_id in self.connection_metadata:
                    del self.connection_metadata[connection_id]
            
            logger.info("Database connection closed", connection_id=connection_id)
            
        except Exception as e:
            logger.error("Failed to close connection", 
                        connection_id=connection_id,
                        error=str(e))
            raise ConnectionError(f"Failed to close connection: {e}")
    
    async def get_connection_status(self, connection_id: str) -> Optional[ConnectionStatus]:
        """Get the status of a connection."""
        async with self.lock:
            return self.connection_statuses.get(connection_id)
    
    async def get_connection_health(self, connection_id: str) -> Optional[ConnectionHealth]:
        """Get the health information of a connection."""
        async with self.lock:
            return self.connection_health.get(connection_id)
    
    async def list_connections(self) -> List[ConnectionStatus]:
        """List all active connections."""
        async with self.lock:
            return list(self.connection_statuses.values())
    
    async def health_check(self, connection_id: str) -> bool:
        """Perform a health check on a connection."""
        try:
            start_time = time.time()
            conn = await self.get_connection(connection_id)
            
            # Test query
            loop = asyncio.get_event_loop()
            cursor = await loop.run_in_executor(None, conn.cursor)
            await loop.run_in_executor(None, cursor.execute, "SELECT 1")
            await loop.run_in_executor(None, cursor.close)
            
            await self.return_connection(connection_id, conn)
            
            response_time = (time.time() - start_time) * 1000
            
            # Update health
            async with self.lock:
                if connection_id in self.connection_health:
                    health = self.connection_health[connection_id]
                    health.response_time_ms = response_time
                    health.uptime_seconds = time.time() - health.uptime_seconds
                
                if connection_id in self.connection_statuses:
                    status = self.connection_statuses[connection_id]
                    status.response_time_ms = response_time
            
            return True
            
        except Exception as e:
            logger.error("Health check failed", 
                        connection_id=connection_id,
                        error=str(e))
            
            # Update error count
            async with self.lock:
                if connection_id in self.connection_health:
                    health = self.connection_health[connection_id]
                    health.error_count += 1
                    health.last_error = str(e)
                
                if connection_id in self.connection_statuses:
                    status = self.connection_statuses[connection_id]
                    status.error_count += 1
                    status.last_error = str(e)
            
            return False
    
    async def close_all_connections(self) -> None:
        """Close all connections."""
        async with self.lock:
            connection_ids = list(self.pools.keys())
        
        for connection_id in connection_ids:
            try:
                await self.close_connection(connection_id)
            except Exception as e:
                logger.error("Error closing connection", 
                           connection_id=connection_id,
                           error=str(e))
        
        logger.info("All connections closed")