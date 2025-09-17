"""
Query execution service for SQL Server MCP Server.

This module provides SQL query execution, parameter binding,
result processing, and query history tracking.
"""

import asyncio
import time
import uuid
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import pyodbc
import structlog

from ..models.query import (
    QueryRequest, QueryResult, QueryHistory, QueryParameter, 
    ColumnInfo, QueryMetadata, QueryStatistics
)
from ..lib.exceptions import QueryError, TimeoutError, ConnectionError
from ..lib.cache import get_cached_query_result, cache_query_result
from ..lib.metrics import get_metrics_collector, time_function, counter, gauge


logger = structlog.get_logger(__name__)


class QueryExecutor:
    """Executes SQL queries and manages query history."""
    
    def __init__(self, connection_manager):
        """Initialize query executor."""
        self.connection_manager = connection_manager
        self.query_history: List[QueryHistory] = []
        self.query_statistics = QueryStatistics()
        self.lock = asyncio.Lock()
    
    async def execute_query(
        self, 
        connection_id: str, 
        request: QueryRequest
    ) -> QueryResult:
        """Execute a SQL query with caching and performance monitoring."""
        query_id = request.generate_query_id()
        start_time = time.time()
        
        # Check cache first
        cached_result = get_cached_query_result(
            request.query,
            request.parameters,
            request.database
        )
        
        if cached_result:
            logger.info("Query result retrieved from cache", query_id=query_id)
            counter("query_cache_hits", 1.0, {"database": request.database or "default"})
            return cached_result
        
        counter("query_cache_misses", 1.0, {"database": request.database or "default"})
        
        try:
            # Get connection
            conn = await self.connection_manager.get_connection(connection_id)
            
            try:
                # Execute query with timing
                result = await self._execute_query_with_connection(
                    conn, request, query_id, start_time
                )
                
                # Update statistics
                await self._update_statistics(result, start_time)
                
                # Record history
                await self._record_history(request, result, connection_id, start_time)
                
                # Cache successful results
                if result.success and result.data:
                    cache_query_result(
                        request.query,
                        result,
                        request.parameters,
                        request.database,
                        ttl=300,  # 5 minutes default TTL
                        metadata={
                            "query_id": query_id,
                            "database": request.database,
                            "execution_time_ms": result.execution_time_ms,
                            "row_count": result.row_count
                        }
                    )
                
                # Record performance metrics
                execution_time_seconds = result.execution_time_ms / 1000.0
                get_metrics_collector().timer(
                    "query_execution_time",
                    execution_time_seconds,
                    {
                        "database": request.database or "default",
                        "success": str(result.success).lower()
                    }
                )
                
                counter("queries_executed", 1.0, {
                    "database": request.database or "default",
                    "success": str(result.success).lower()
                })
                
                gauge("active_queries", len(self.query_history))
                
                return result
                
            finally:
                # Always return connection to pool
                await self.connection_manager.return_connection(connection_id, conn)
                
        except Exception as e:
            execution_time = (time.time() - start_time) * 1000
            
            # Create error result
            result = QueryResult(
                success=False,
                data=[],
                columns=[],
                row_count=0,
                execution_time_ms=execution_time,
                query_id=query_id,
                error_message=str(e)
            )
            
            # Update statistics
            await self._update_statistics(result, start_time)
            
            # Record history
            await self._record_history(request, result, connection_id, start_time)
            
            logger.error("Query execution failed", 
                        query_id=query_id,
                        error=str(e))
            
            raise QueryError(f"Query execution failed: {e}")
    
    async def _execute_query_with_connection(
        self, 
        conn: pyodbc.Connection, 
        request: QueryRequest, 
        query_id: str,
        start_time: float
    ) -> QueryResult:
        """Execute query with a specific connection."""
        try:
            # Run in thread pool since pyodbc is synchronous
            loop = asyncio.get_event_loop()
            cursor = await loop.run_in_executor(None, conn.cursor)
            
            try:
                # Set query timeout
                cursor.timeout = request.timeout
                
                # Execute query with parameters
                if request.parameters:
                    # Convert parameters to tuple format for pyodbc
                    param_values = [param.value for param in request.parameters]
                    await loop.run_in_executor(
                        None, cursor.execute, request.query, param_values
                    )
                else:
                    await loop.run_in_executor(None, cursor.execute, request.query)
                
                # Get column information
                columns = await self._get_column_info(cursor)
                
                # Fetch results
                rows = await loop.run_in_executor(None, cursor.fetchall)
                
                # Convert rows to dictionaries
                data = []
                for row in rows:
                    row_dict = {}
                    for i, column in enumerate(columns):
                        row_dict[column.name] = row[i]
                    data.append(row_dict)
                
                execution_time = (time.time() - start_time) * 1000
                
                return QueryResult(
                    success=True,
                    data=data,
                    columns=columns,
                    row_count=len(data),
                    execution_time_ms=execution_time,
                    query_id=query_id
                )
                
            finally:
                await loop.run_in_executor(None, cursor.close)
                
        except pyodbc.Error as e:
            execution_time = (time.time() - start_time) * 1000
            
            if "timeout" in str(e).lower():
                raise TimeoutError(f"Query timeout: {e}")
            else:
                raise QueryError(f"Query execution failed: {e}")
    
    async def _get_column_info(self, cursor) -> List[ColumnInfo]:
        """Get column information from cursor."""
        try:
            columns = []
            for i, column in enumerate(cursor.description):
                col_info = ColumnInfo(
                    name=column[0] or f"Column{i+1}",
                    type=str(column[1]) if column[1] else "unknown",
                    nullable=column[6] if len(column) > 6 else True
                )
                columns.append(col_info)
            return columns
        except Exception as e:
            logger.warning("Failed to get column info", error=str(e))
            return []
    
    async def _update_statistics(self, result: QueryResult, start_time: float) -> None:
        """Update query statistics."""
        async with self.lock:
            self.query_statistics.total_queries += 1
            
            if result.success:
                self.query_statistics.successful_queries += 1
            else:
                self.query_statistics.failed_queries += 1
            
            self.query_statistics.total_execution_time_ms += result.execution_time_ms
            self.query_statistics.average_execution_time_ms = (
                self.query_statistics.total_execution_time_ms / 
                self.query_statistics.total_queries
            )
    
    async def _record_history(
        self, 
        request: QueryRequest, 
        result: QueryResult, 
        connection_id: str,
        start_time: float
    ) -> None:
        """Record query in history."""
        async with self.lock:
            history = QueryHistory(
                query_id=result.query_id,
                query=request.query,
                database=request.database or "default",
                execution_time_ms=result.execution_time_ms,
                row_count=result.row_count,
                status="success" if result.success else "error",
                error_message=result.error_message,
                timestamp=datetime.utcnow(),
                parameters=request.parameters or []
            )
            
            self.query_history.append(history)
            
            # Keep only last 1000 queries
            if len(self.query_history) > 1000:
                self.query_history = self.query_history[-1000:]
    
    async def get_query_history(
        self, 
        limit: int = 100, 
        offset: int = 0
    ) -> List[QueryHistory]:
        """Get query execution history."""
        async with self.lock:
            return self.query_history[offset:offset + limit]
    
    async def get_query_statistics(self) -> QueryStatistics:
        """Get query execution statistics."""
        async with self.lock:
            return self.query_statistics
    
    async def clear_history(self) -> None:
        """Clear query execution history."""
        async with self.lock:
            self.query_history.clear()
            self.query_statistics = QueryStatistics()
        
        logger.info("Query history cleared")
    
    async def get_query_by_id(self, query_id: str) -> Optional[QueryHistory]:
        """Get a specific query by ID."""
        async with self.lock:
            for history in self.query_history:
                if history.query_id == query_id:
                    return history
            return None
    
    async def execute_parameterized_query(
        self,
        connection_id: str,
        query: str,
        parameters: List[QueryParameter],
        database: Optional[str] = None,
        timeout: int = 30
    ) -> QueryResult:
        """Execute a parameterized query."""
        request = QueryRequest(
            query=query,
            database=database,
            timeout=timeout,
            parameters=parameters
        )
        
        return await self.execute_query(connection_id, request)
    
    async def execute_simple_query(
        self,
        connection_id: str,
        query: str,
        database: Optional[str] = None,
        timeout: int = 30
    ) -> QueryResult:
        """Execute a simple query without parameters."""
        request = QueryRequest(
            query=query,
            database=database,
            timeout=timeout
        )
        
        return await self.execute_query(connection_id, request)
    
    async def validate_query(self, query: str) -> Tuple[bool, Optional[str]]:
        """Validate a SQL query syntax (basic validation)."""
        try:
            # Basic validation - check for common SQL keywords
            query_upper = query.upper().strip()
            
            if not query_upper:
                return False, "Query cannot be empty"
            
            # Check for dangerous operations
            dangerous_keywords = ["DROP", "DELETE", "TRUNCATE", "ALTER", "CREATE", "INSERT", "UPDATE"]
            for keyword in dangerous_keywords:
                if keyword in query_upper:
                    return False, f"Query contains potentially dangerous operation: {keyword}"
            
            # Check for basic SQL structure
            if not any(keyword in query_upper for keyword in ["SELECT", "WITH", "EXEC", "EXECUTE"]):
                return False, "Query must be a SELECT statement or stored procedure call"
            
            return True, None
            
        except Exception as e:
            return False, f"Query validation failed: {e}"
    
    async def get_query_performance_stats(self) -> Dict[str, Any]:
        """Get query performance statistics."""
        async with self.lock:
            if not self.query_history:
                return {
                    "total_queries": 0,
                    "average_execution_time_ms": 0.0,
                    "slowest_query": None,
                    "fastest_query": None
                }
            
            # Find slowest and fastest queries
            slowest = max(self.query_history, key=lambda h: h.execution_time_ms)
            fastest = min(self.query_history, key=lambda h: h.execution_time_ms)
            
            return {
                "total_queries": len(self.query_history),
                "average_execution_time_ms": self.query_statistics.average_execution_time_ms,
                "slowest_query": {
                    "query_id": slowest.query_id,
                    "execution_time_ms": slowest.execution_time_ms,
                    "query": slowest.query[:100] + "..." if len(slowest.query) > 100 else slowest.query
                },
                "fastest_query": {
                    "query_id": fastest.query_id,
                    "execution_time_ms": fastest.execution_time_ms,
                    "query": fastest.query[:100] + "..." if len(fastest.query) > 100 else fastest.query
                }
            }