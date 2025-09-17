"""
Schema service for SQL Server MCP Server.

This module provides database schema information retrieval,
including tables, columns, indexes, and relationships.
"""

import asyncio
import time
from typing import Dict, List, Optional, Any
from datetime import datetime
import pyodbc
import structlog

from ..models.schema import (
    TableInfo, ColumnInfo, IndexInfo, RelationshipInfo, 
    DatabaseInfo, SchemaMetadata, DatabaseListMetadata
)
from ..lib.exceptions import SchemaError, ConnectionError


logger = structlog.get_logger(__name__)


class SchemaService:
    """Provides database schema information."""
    
    def __init__(self, connection_manager):
        """Initialize schema service."""
        self.connection_manager = connection_manager
    
    async def get_database_list(
        self, 
        connection_id: str,
        include_system: bool = False,
        include_metadata: bool = True
    ) -> List[DatabaseInfo]:
        """Get list of databases."""
        start_time = time.time()
        
        try:
            conn = await self.connection_manager.get_connection(connection_id)
            
            try:
                # Run in thread pool since pyodbc is synchronous
                loop = asyncio.get_event_loop()
                cursor = await loop.run_in_executor(None, conn.cursor)
                
                try:
                    # Query to get database information
                    query = """
                    SELECT 
                        name,
                        database_id,
                        create_date,
                        collation_name,
                        CASE 
                            WHEN name IN ('master', 'tempdb', 'model', 'msdb') THEN 1 
                            ELSE 0 
                        END as is_system
                    FROM sys.databases
                    WHERE state = 0  -- ONLINE
                    """
                    
                    if not include_system:
                        query += " AND name NOT IN ('master', 'tempdb', 'model', 'msdb')"
                    
                    query += " ORDER BY name"
                    
                    await loop.run_in_executor(None, cursor.execute, query)
                    rows = await loop.run_in_executor(None, cursor.fetchall)
                    
                    databases = []
                    for row in rows:
                        db_info = DatabaseInfo(
                            name=row[0],
                            database_id=row[1],
                            create_date=row[2],
                            collation_name=row[3],
                            is_system=bool(row[4])
                        )
                        
                        # Add optional metadata if requested
                        if include_metadata:
                            db_info.size_mb = await self._get_database_size(conn, row[0])
                            db_info.status = "ONLINE"
                            db_info.recovery_model = await self._get_recovery_model(conn, row[0])
                        
                        databases.append(db_info)
                    
                    execution_time = (time.time() - start_time) * 1000
                    logger.info("Retrieved database list", 
                               count=len(databases),
                               execution_time_ms=execution_time)
                    
                    return databases
                    
                finally:
                    await loop.run_in_executor(None, cursor.close)
                    
            finally:
                await self.connection_manager.return_connection(connection_id, conn)
                
        except Exception as e:
            logger.error("Failed to get database list", error=str(e))
            raise SchemaError(f"Failed to get database list: {e}")
    
    async def get_table_list(
        self, 
        connection_id: str,
        database: Optional[str] = None,
        schema: Optional[str] = None
    ) -> List[TableInfo]:
        """Get list of tables in a database."""
        start_time = time.time()
        
        try:
            conn = await self.connection_manager.get_connection(connection_id)
            
            try:
                # Switch database if specified
                if database:
                    await self._switch_database(conn, database)
                
                # Run in thread pool since pyodbc is synchronous
                loop = asyncio.get_event_loop()
                cursor = await loop.run_in_executor(None, conn.cursor)
                
                try:
                    # Query to get table information
                    query = """
                    SELECT 
                        t.name as table_name,
                        s.name as schema_name
                    FROM sys.tables t
                    INNER JOIN sys.schemas s ON t.schema_id = s.schema_id
                    """
                    
                    params = []
                    if schema:
                        query += " WHERE s.name = ?"
                        params.append(schema)
                    
                    query += " ORDER BY s.name, t.name"
                    
                    if params:
                        await loop.run_in_executor(None, cursor.execute, query, params)
                    else:
                        await loop.run_in_executor(None, cursor.execute, query)
                    
                    rows = await loop.run_in_executor(None, cursor.fetchall)
                    
                    tables = []
                    for row in rows:
                        table_name = row[0]
                        schema_name = row[1]
                        
                        # Get detailed table information
                        table_info = await self._get_table_details(
                            conn, table_name, schema_name
                        )
                        tables.append(table_info)
                    
                    execution_time = (time.time() - start_time) * 1000
                    logger.info("Retrieved table list", 
                               count=len(tables),
                               execution_time_ms=execution_time)
                    
                    return tables
                    
                finally:
                    await loop.run_in_executor(None, cursor.close)
                    
            finally:
                await self.connection_manager.return_connection(connection_id, conn)
                
        except Exception as e:
            logger.error("Failed to get table list", error=str(e))
            raise SchemaError(f"Failed to get table list: {e}")
    
    async def get_table_schema(
        self, 
        connection_id: str,
        table_name: str,
        database: Optional[str] = None,
        schema: Optional[str] = None,
        include_indexes: bool = True,
        include_relationships: bool = True
    ) -> TableInfo:
        """Get detailed schema information for a table."""
        start_time = time.time()
        
        try:
            conn = await self.connection_manager.get_connection(connection_id)
            
            try:
                # Switch database if specified
                if database:
                    await self._switch_database(conn, database)
                
                # Get table details
                table_info = await self._get_table_details(
                    conn, table_name, schema or "dbo", include_indexes, include_relationships
                )
                
                execution_time = (time.time() - start_time) * 1000
                logger.info("Retrieved table schema", 
                           table=table_name,
                           execution_time_ms=execution_time)
                
                return table_info
                
            finally:
                await self.connection_manager.return_connection(connection_id, conn)
                
        except Exception as e:
            logger.error("Failed to get table schema", 
                        table=table_name,
                        error=str(e))
            raise SchemaError(f"Failed to get table schema: {e}")
    
    async def _switch_database(self, conn: pyodbc.Connection, database: str) -> None:
        """Switch to a specific database."""
        try:
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None, conn.execute, f"USE [{database}]"
            )
        except Exception as e:
            raise SchemaError(f"Failed to switch to database {database}: {e}")
    
    async def _get_table_details(
        self, 
        conn: pyodbc.Connection, 
        table_name: str, 
        schema_name: str,
        include_indexes: bool = True,
        include_relationships: bool = True
    ) -> TableInfo:
        """Get detailed information for a specific table."""
        loop = asyncio.get_event_loop()
        cursor = await loop.run_in_executor(None, conn.cursor)
        
        try:
            # Get columns
            columns = await self._get_table_columns(cursor, table_name, schema_name)
            
            # Get indexes
            indexes = []
            if include_indexes:
                indexes = await self._get_table_indexes(cursor, table_name, schema_name)
            
            # Get relationships
            relationships = []
            if include_relationships:
                relationships = await self._get_table_relationships(cursor, table_name, schema_name)
            
            return TableInfo(
                name=table_name,
                schema=schema_name,
                columns=columns,
                indexes=indexes,
                relationships=relationships
            )
            
        finally:
            await loop.run_in_executor(None, cursor.close)
    
    async def _get_table_columns(
        self, 
        cursor: pyodbc.Cursor, 
        table_name: str, 
        schema_name: str
    ) -> List[ColumnInfo]:
        """Get column information for a table."""
        loop = asyncio.get_event_loop()
        
        query = """
        SELECT 
            c.name,
            t.name as data_type,
            c.max_length,
            c.precision,
            c.scale,
            c.is_nullable,
            c.is_identity,
            dc.definition as default_value,
            c.column_id
        FROM sys.columns c
        INNER JOIN sys.types t ON c.user_type_id = t.user_type_id
        INNER JOIN sys.tables tb ON c.object_id = tb.object_id
        INNER JOIN sys.schemas s ON tb.schema_id = s.schema_id
        LEFT JOIN sys.default_constraints dc ON c.default_object_id = dc.object_id
        WHERE tb.name = ? AND s.name = ?
        ORDER BY c.column_id
        """
        
        await loop.run_in_executor(None, cursor.execute, query, [table_name, schema_name])
        rows = await loop.run_in_executor(None, cursor.fetchall)
        
        columns = []
        for row in rows:
            column = ColumnInfo(
                name=row[0],
                data_type=row[1],
                max_length=row[2] if row[2] != -1 else None,
                precision=row[3] if row[3] != 0 else None,
                scale=row[4] if row[4] != 0 else None,
                is_nullable=bool(row[5]),
                is_identity=bool(row[6]),
                default_value=row[7],
                column_id=row[8]
            )
            columns.append(column)
        
        return columns
    
    async def _get_table_indexes(
        self, 
        cursor: pyodbc.Cursor, 
        table_name: str, 
        schema_name: str
    ) -> List[IndexInfo]:
        """Get index information for a table."""
        loop = asyncio.get_event_loop()
        
        query = """
        SELECT 
            i.name,
            i.type_desc,
            i.is_unique,
            i.is_primary_key,
            STRING_AGG(c.name, ', ') as columns
        FROM sys.indexes i
        INNER JOIN sys.tables t ON i.object_id = t.object_id
        INNER JOIN sys.schemas s ON t.schema_id = s.schema_id
        INNER JOIN sys.index_columns ic ON i.object_id = ic.object_id AND i.index_id = ic.index_id
        INNER JOIN sys.columns c ON ic.object_id = c.object_id AND ic.column_id = c.column_id
        WHERE t.name = ? AND s.name = ? AND i.index_id > 0
        GROUP BY i.name, i.type_desc, i.is_unique, i.is_primary_key
        ORDER BY i.name
        """
        
        await loop.run_in_executor(None, cursor.execute, query, [table_name, schema_name])
        rows = await loop.run_in_executor(None, cursor.fetchall)
        
        indexes = []
        for row in rows:
            index = IndexInfo(
                name=row[0],
                type=row[1],
                is_unique=bool(row[2]),
                is_primary_key=bool(row[3]),
                columns=row[4].split(', ') if row[4] else []
            )
            indexes.append(index)
        
        return indexes
    
    async def _get_table_relationships(
        self, 
        cursor: pyodbc.Cursor, 
        table_name: str, 
        schema_name: str
    ) -> List[RelationshipInfo]:
        """Get foreign key relationships for a table."""
        loop = asyncio.get_event_loop()
        
        query = """
        SELECT 
            fk.name,
            rt.name as referenced_table,
            rs.name as referenced_schema,
            c.name as column_name,
            rc.name as referenced_column
        FROM sys.foreign_keys fk
        INNER JOIN sys.tables t ON fk.parent_object_id = t.object_id
        INNER JOIN sys.schemas s ON t.schema_id = s.schema_id
        INNER JOIN sys.foreign_key_columns fkc ON fk.object_id = fkc.constraint_object_id
        INNER JOIN sys.columns c ON fkc.parent_object_id = c.object_id AND fkc.parent_column_id = c.column_id
        INNER JOIN sys.tables rt ON fkc.referenced_object_id = rt.object_id
        INNER JOIN sys.schemas rs ON rt.schema_id = rs.schema_id
        INNER JOIN sys.columns rc ON fkc.referenced_object_id = rc.object_id AND fkc.referenced_column_id = rc.column_id
        WHERE t.name = ? AND s.name = ?
        ORDER BY fk.name, fkc.constraint_column_id
        """
        
        await loop.run_in_executor(None, cursor.execute, query, [table_name, schema_name])
        rows = await loop.run_in_executor(None, cursor.fetchall)
        
        # Group by relationship name
        relationships = {}
        for row in rows:
            rel_name = row[0]
            if rel_name not in relationships:
                relationships[rel_name] = {
                    'name': rel_name,
                    'referenced_table': row[1],
                    'referenced_schema': row[2],
                    'columns': []
                }
            
            relationships[rel_name]['columns'].append({
                'column': row[3],
                'referenced_column': row[4]
            })
        
        # Convert to RelationshipInfo objects
        relationship_list = []
        for rel_data in relationships.values():
            relationship = RelationshipInfo(
                name=rel_data['name'],
                referenced_table=rel_data['referenced_table'],
                referenced_schema=rel_data['referenced_schema'],
                columns=[RelationshipColumn(**col) for col in rel_data['columns']]
            )
            relationship_list.append(relationship)
        
        return relationship_list
    
    async def _get_database_size(self, conn: pyodbc.Connection, database_name: str) -> Optional[float]:
        """Get database size in MB."""
        try:
            loop = asyncio.get_event_loop()
            cursor = await loop.run_in_executor(None, conn.cursor)
            
            try:
                query = """
                SELECT 
                    CAST(SUM(CAST(FILEPROPERTY(name, 'SpaceUsed') AS bigint) * 8192.) / 1024 / 1024 AS DECIMAL(15,2))
                FROM sys.database_files
                WHERE type = 0
                """
                
                await loop.run_in_executor(None, cursor.execute, query)
                row = await loop.run_in_executor(None, cursor.fetchone)
                
                return float(row[0]) if row and row[0] is not None else None
                
            finally:
                await loop.run_in_executor(None, cursor.close)
                
        except Exception:
            return None
    
    async def _get_recovery_model(self, conn: pyodbc.Connection, database_name: str) -> Optional[str]:
        """Get database recovery model."""
        try:
            loop = asyncio.get_event_loop()
            cursor = await loop.run_in_executor(None, conn.cursor)
            
            try:
                query = "SELECT recovery_model_desc FROM sys.databases WHERE name = ?"
                await loop.run_in_executor(None, cursor.execute, query, [database_name])
                row = await loop.run_in_executor(None, cursor.fetchone)
                
                return row[0] if row else None
                
            finally:
                await loop.run_in_executor(None, cursor.close)
                
        except Exception:
            return None