"""
Data service for SQL Server MCP Server.

This module provides data retrieval operations,
including table data fetching with pagination and filtering.
"""

import asyncio
import time
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
import pyodbc
import structlog

from ..models.schema import ColumnInfo
from ..models.query import QueryResult, QueryParameter
from ..lib.exceptions import DataError, ConnectionError


logger = structlog.get_logger(__name__)


class DataService:
    """Provides data retrieval operations."""
    
    def __init__(self, connection_manager, query_executor):
        """Initialize data service."""
        self.connection_manager = connection_manager
        self.query_executor = query_executor
    
    async def get_table_data(
        self,
        connection_id: str,
        table_name: str,
        database: Optional[str] = None,
        schema: Optional[str] = None,
        columns: Optional[List[str]] = None,
        where_clause: Optional[str] = None,
        order_by: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> QueryResult:
        """Get data from a table with pagination and filtering."""
        start_time = time.time()
        
        try:
            # Build SELECT query
            query = self._build_select_query(
                table_name, schema, columns, where_clause, order_by, limit, offset
            )
            
            # Execute query
            result = await self.query_executor.execute_simple_query(
                connection_id, query, database
            )
            
            # Add pagination metadata
            total_rows = await self._get_table_row_count(
                connection_id, table_name, database, schema, where_clause
            )
            
            # Create enhanced result with pagination info
            enhanced_result = QueryResult(
                success=result.success,
                data=result.data,
                columns=result.columns,
                row_count=result.row_count,
                execution_time_ms=result.execution_time_ms,
                query_id=result.query_id,
                error_message=result.error_message
            )
            
            # Add pagination metadata to result
            enhanced_result.metadata = {
                "pagination": {
                    "limit": limit,
                    "offset": offset,
                    "total_rows": total_rows,
                    "has_more": (offset + limit) < total_rows
                },
                "table": table_name,
                "database": database,
                "schema": schema
            }
            
            execution_time = (time.time() - start_time) * 1000
            logger.info("Retrieved table data", 
                       table=table_name,
                       row_count=result.row_count,
                       execution_time_ms=execution_time)
            
            return enhanced_result
            
        except Exception as e:
            logger.error("Failed to get table data", 
                        table=table_name,
                        error=str(e))
            raise DataError(f"Failed to get table data: {e}")
    
    def _build_select_query(
        self,
        table_name: str,
        schema: Optional[str] = None,
        columns: Optional[List[str]] = None,
        where_clause: Optional[str] = None,
        order_by: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> str:
        """Build a SELECT query with the specified parameters."""
        # Build column list
        if columns:
            column_list = ", ".join([f"[{col}]" for col in columns])
        else:
            column_list = "*"
        
        # Build table reference
        if schema:
            table_ref = f"[{schema}].[{table_name}]"
        else:
            table_ref = f"[{table_name}]"
        
        # Build base query
        query = f"SELECT {column_list} FROM {table_ref}"
        
        # Add WHERE clause
        if where_clause:
            query += f" WHERE {where_clause}"
        
        # Add ORDER BY clause
        if order_by:
            query += f" ORDER BY {order_by}"
        else:
            # Default ordering by first column for consistent pagination
            if columns:
                query += f" ORDER BY [{columns[0]}]"
            else:
                query += f" ORDER BY (SELECT NULL)"  # No specific ordering
        
        # Add pagination
        if offset > 0:
            query += f" OFFSET {offset} ROWS"
        
        if limit > 0:
            query += f" FETCH NEXT {limit} ROWS ONLY"
        
        return query
    
    async def _get_table_row_count(
        self,
        connection_id: str,
        table_name: str,
        database: Optional[str] = None,
        schema: Optional[str] = None,
        where_clause: Optional[str] = None
    ) -> int:
        """Get total row count for a table with optional WHERE clause."""
        try:
            # Build table reference
            if schema:
                table_ref = f"[{schema}].[{table_name}]"
            else:
                table_ref = f"[{table_name}]"
            
            # Build COUNT query
            query = f"SELECT COUNT(*) FROM {table_ref}"
            if where_clause:
                query += f" WHERE {where_clause}"
            
            # Execute count query
            result = await self.query_executor.execute_simple_query(
                connection_id, query, database
            )
            
            if result.success and result.data:
                return result.data[0][list(result.data[0].keys())[0]]
            else:
                return 0
                
        except Exception as e:
            logger.warning("Failed to get table row count", 
                          table=table_name,
                          error=str(e))
            return 0