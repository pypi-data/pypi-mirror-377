"""
Schema inspection commands for SQL Server MCP Server CLI.

This module provides CLI commands for inspecting database schema.
"""

import click
import asyncio
from typing import Optional
import structlog

from ..services.schema_service import SchemaService
from ..models.schema import SchemaRequest
from ..lib.exceptions import SchemaError


logger = structlog.get_logger(__name__)


@click.group()
def schema_group() -> None:
    """Inspect database schema."""
    pass


@schema_group.command()
@click.argument("connection_id")
@click.argument("database")
@click.option(
    "--table", "-t",
    help="Specific table name"
)
@click.option(
    "--include-indexes/--no-indexes",
    default=False,
    help="Include index information"
)
@click.option(
    "--include-relationships/--no-relationships",
    default=False,
    help="Include foreign key relationships"
)
@click.option(
    "--include-row-counts/--no-row-counts",
    default=False,
    help="Include row counts (may be slow)"
)
@click.option(
    "--output", "-o",
    type=click.Choice(["table", "json"]),
    default="table",
    help="Output format"
)
def inspect(
    connection_id: str,
    database: str,
    table: Optional[str],
    include_indexes: bool,
    include_relationships: bool,
    include_row_counts: bool,
    output: str
) -> None:
    """Inspect database or table schema."""
    
    async def _inspect():
        try:
            # Create schema request
            request = SchemaRequest(
                connection_id=connection_id,
                database=database,
                table_name=table,
                include_indexes=include_indexes,
                include_relationships=include_relationships,
                include_row_counts=include_row_counts
            )
            
            # Get schema
            schema_service = SchemaService()
            result = await schema_service.get_schema(request)
            
            if result.status == "error":
                click.echo(f"Schema inspection failed: {result.error_message}", err=True)
                raise click.Abort()
            
            # Format output
            if output == "json":
                import json
                click.echo(json.dumps(result.to_dict(), indent=2))
            else:
                _output_schema_table(result)
            
            logger.info("Schema inspected", 
                       connection_id=connection_id, 
                       database=database,
                       table=table)
            
        except Exception as e:
            logger.error("Schema inspection failed", error=str(e))
            click.echo(f"Schema inspection failed: {e}", err=True)
            raise click.Abort()
    
    asyncio.run(_inspect())


@schema_group.command()
@click.argument("connection_id")
@click.argument("database")
@click.option(
    "--output", "-o",
    type=click.Choice(["table", "json"]),
    default="table",
    help="Output format"
)
def tables(connection_id: str, database: str, output: str) -> None:
    """List all tables in a database."""
    
    async def _tables():
        try:
            # Create schema request for tables only
            request = SchemaRequest(
                connection_id=connection_id,
                database=database,
                include_columns=False,
                include_indexes=False,
                include_relationships=False,
                include_row_counts=False
            )
            
            # Get schema
            schema_service = SchemaService()
            result = await schema_service.get_schema(request)
            
            if result.status == "error":
                click.echo(f"Tables listing failed: {result.error_message}", err=True)
                raise click.Abort()
            
            # Format output
            if output == "json":
                import json
                click.echo(json.dumps(result.to_dict(), indent=2))
            else:
                _output_tables_list(result)
            
        except Exception as e:
            logger.error("Tables listing failed", error=str(e))
            click.echo(f"Tables listing failed: {e}", err=True)
            raise click.Abort()
    
    asyncio.run(_tables())


@schema_group.command()
@click.argument("connection_id")
@click.argument("database")
@click.argument("table")
@click.option(
    "--output", "-o",
    type=click.Choice(["table", "json"]),
    default="table",
    help="Output format"
)
def columns(connection_id: str, database: str, table: str, output: str) -> None:
    """List columns in a table."""
    
    async def _columns():
        try:
            # Create schema request for specific table columns
            request = SchemaRequest(
                connection_id=connection_id,
                database=database,
                table_name=table,
                include_columns=True,
                include_indexes=False,
                include_relationships=False,
                include_row_counts=False
            )
            
            # Get schema
            schema_service = SchemaService()
            result = await schema_service.get_schema(request)
            
            if result.status == "error":
                click.echo(f"Columns listing failed: {result.error_message}", err=True)
                raise click.Abort()
            
            # Format output
            if output == "json":
                import json
                click.echo(json.dumps(result.to_dict(), indent=2))
            else:
                _output_columns_list(result, table)
            
        except Exception as e:
            logger.error("Columns listing failed", error=str(e))
            click.echo(f"Columns listing failed: {e}", err=True)
            raise click.Abort()
    
    asyncio.run(_columns())


@schema_group.command()
@click.argument("connection_id")
@click.argument("database")
@click.argument("table")
@click.option(
    "--output", "-o",
    type=click.Choice(["table", "json"]),
    default="table",
    help="Output format"
)
def indexes(connection_id: str, database: str, table: str, output: str) -> None:
    """List indexes on a table."""
    
    async def _indexes():
        try:
            # Create schema request for specific table indexes
            request = SchemaRequest(
                connection_id=connection_id,
                database=database,
                table_name=table,
                include_columns=False,
                include_indexes=True,
                include_relationships=False,
                include_row_counts=False
            )
            
            # Get schema
            schema_service = SchemaService()
            result = await schema_service.get_schema(request)
            
            if result.status == "error":
                click.echo(f"Indexes listing failed: {result.error_message}", err=True)
                raise click.Abort()
            
            # Format output
            if output == "json":
                import json
                click.echo(json.dumps(result.to_dict(), indent=2))
            else:
                _output_indexes_list(result, table)
            
        except Exception as e:
            logger.error("Indexes listing failed", error=str(e))
            click.echo(f"Indexes listing failed: {e}", err=True)
            raise click.Abort()
    
    asyncio.run(_indexes())


@schema_group.command()
@click.argument("connection_id")
@click.argument("database")
@click.argument("table")
@click.option(
    "--output", "-o",
    type=click.Choice(["table", "json"]),
    default="table",
    help="Output format"
)
def relationships(connection_id: str, database: str, table: str, output: str) -> None:
    """List foreign key relationships for a table."""
    
    async def _relationships():
        try:
            # Create schema request for specific table relationships
            request = SchemaRequest(
                connection_id=connection_id,
                database=database,
                table_name=table,
                include_columns=False,
                include_indexes=False,
                include_relationships=True,
                include_row_counts=False
            )
            
            # Get schema
            schema_service = SchemaService()
            result = await schema_service.get_schema(request)
            
            if result.status == "error":
                click.echo(f"Relationships listing failed: {result.error_message}", err=True)
                raise click.Abort()
            
            # Format output
            if output == "json":
                import json
                click.echo(json.dumps(result.to_dict(), indent=2))
            else:
                _output_relationships_list(result, table)
            
        except Exception as e:
            logger.error("Relationships listing failed", error=str(e))
            click.echo(f"Relationships listing failed: {e}", err=True)
            raise click.Abort()
    
    asyncio.run(_relationships())


def _output_schema_table(result: Any) -> None:
    """Output schema result in table format."""
    if not result.tables:
        click.echo("No tables found")
        return
    
    for table in result.tables:
        click.echo(f"\nTable: {table.schema}.{table.name}")
        click.echo("=" * 50)
        
        # Columns
        if table.columns:
            click.echo("\nColumns:")
            click.echo("-" * 30)
            for col in table.columns:
                nullable = "NULL" if col.is_nullable else "NOT NULL"
                pk = " (PK)" if col.is_primary_key else ""
                fk = " (FK)" if col.is_foreign_key else ""
                click.echo(f"  {col.name:<20} {col.data_type:<15} {nullable}{pk}{fk}")
        
        # Indexes
        if table.indexes:
            click.echo("\nIndexes:")
            click.echo("-" * 30)
            for idx in table.indexes:
                unique = "UNIQUE " if idx.is_unique else ""
                clustered = "CLUSTERED " if idx.is_clustered else ""
                click.echo(f"  {unique}{clustered}{idx.name}: {', '.join(idx.columns)}")
        
        # Relationships
        if table.relationships:
            click.echo("\nRelationships:")
            click.echo("-" * 30)
            for rel in table.relationships:
                click.echo(f"  {rel.name}: {rel.from_table}.{rel.from_column} -> {rel.to_table}.{rel.to_column}")
        
        # Row count
        if table.row_count is not None:
            click.echo(f"\nRow Count: {table.row_count:,}")


def _output_tables_list(result: Any) -> None:
    """Output tables list in table format."""
    if not result.tables:
        click.echo("No tables found")
        return
    
    click.echo(f"Tables in {result.database_name}:")
    click.echo("=" * 40)
    
    for table in result.tables:
        click.echo(f"  {table.schema}.{table.name}")


def _output_columns_list(result: Any, table_name: str) -> None:
    """Output columns list in table format."""
    if not result.tables:
        click.echo(f"Table {table_name} not found")
        return
    
    table = result.tables[0]  # Should be only one table
    if not table.columns:
        click.echo(f"No columns found for table {table_name}")
        return
    
    click.echo(f"Columns in {table.schema}.{table.name}:")
    click.echo("=" * 60)
    
    for col in table.columns:
        nullable = "NULL" if col.is_nullable else "NOT NULL"
        pk = " (PK)" if col.is_primary_key else ""
        fk = " (FK)" if col.is_foreign_key else ""
        click.echo(f"  {col.name:<25} {col.data_type:<20} {nullable}{pk}{fk}")


def _output_indexes_list(result: Any, table_name: str) -> None:
    """Output indexes list in table format."""
    if not result.tables:
        click.echo(f"Table {table_name} not found")
        return
    
    table = result.tables[0]  # Should be only one table
    if not table.indexes:
        click.echo(f"No indexes found for table {table_name}")
        return
    
    click.echo(f"Indexes on {table.schema}.{table.name}:")
    click.echo("=" * 60)
    
    for idx in table.indexes:
        unique = "UNIQUE " if idx.is_unique else ""
        clustered = "CLUSTERED " if idx.is_clustered else ""
        click.echo(f"  {unique}{clustered}{idx.name}")
        click.echo(f"    Columns: {', '.join(idx.columns)}")


def _output_relationships_list(result: Any, table_name: str) -> None:
    """Output relationships list in table format."""
    if not result.tables:
        click.echo(f"Table {table_name} not found")
        return
    
    table = result.tables[0]  # Should be only one table
    if not table.relationships:
        click.echo(f"No relationships found for table {table_name}")
        return
    
    click.echo(f"Relationships for {table.schema}.{table.name}:")
    click.echo("=" * 60)
    
    for rel in table.relationships:
        click.echo(f"  {rel.name}")
        click.echo(f"    {rel.from_table}.{rel.from_column} -> {rel.to_table}.{rel.to_column}")
        if rel.on_delete:
            click.echo(f"    ON DELETE: {rel.on_delete}")
        if rel.on_update:
            click.echo(f"    ON UPDATE: {rel.on_update}")