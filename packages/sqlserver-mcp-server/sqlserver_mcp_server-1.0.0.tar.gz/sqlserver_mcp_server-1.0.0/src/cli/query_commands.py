"""
Query execution commands for SQL Server MCP Server CLI.

This module provides CLI commands for executing SQL queries.
"""

import click
import asyncio
from typing import Optional, List, Any
import structlog

from ..services.query_executor import QueryExecutor
from ..models.query import QueryRequest
from ..lib.exceptions import QueryError


logger = structlog.get_logger(__name__)


@click.group()
def query_group() -> None:
    """Execute SQL queries."""
    pass


@query_group.command()
@click.argument("connection_id")
@click.argument("sql_query")
@click.option(
    "--database", "-d",
    help="Database name (overrides connection default)"
)
@click.option(
    "--timeout",
    type=int,
    default=30,
    help="Query timeout in seconds (default: 30)"
)
@click.option(
    "--output", "-o",
    type=click.Choice(["table", "json", "csv"]),
    default="table",
    help="Output format"
)
@click.option(
    "--limit",
    type=int,
    help="Limit number of rows returned"
)
def execute(
    connection_id: str,
    sql_query: str,
    database: Optional[str],
    timeout: int,
    output: str,
    limit: Optional[int]
) -> None:
    """Execute a SQL query."""
    
    async def _execute():
        try:
            # Create query request
            request = QueryRequest(
                connection_id=connection_id,
                query=sql_query,
                database=database,
                timeout=timeout
            )
            
            # Execute query
            query_executor = QueryExecutor()
            result = await query_executor.execute_query(request)
            
            if result.status == "error":
                click.echo(f"Query failed: {result.error_message}", err=True)
                raise click.Abort()
            
            # Format output
            if output == "json":
                import json
                click.echo(json.dumps(result.to_dict(), indent=2))
            elif output == "csv":
                _output_csv(result)
            else:
                _output_table(result, limit)
            
            logger.info("Query executed", 
                       connection_id=connection_id, 
                       rows_affected=result.rows_affected,
                       execution_time=result.execution_time_ms)
            
        except Exception as e:
            logger.error("Query execution failed", error=str(e))
            click.echo(f"Query execution failed: {e}", err=True)
            raise click.Abort()
    
    asyncio.run(_execute())


@query_group.command()
@click.argument("connection_id")
@click.argument("database")
@click.option(
    "--table", "-t",
    help="Specific table name"
)
@click.option(
    "--limit",
    type=int,
    default=10,
    help="Number of rows to show (default: 10)"
)
@click.option(
    "--output", "-o",
    type=click.Choice(["table", "json"]),
    default="table",
    help="Output format"
)
def sample(
    connection_id: str,
    database: str,
    table: Optional[str],
    limit: int,
    output: str
) -> None:
    """Show sample data from a table or database."""
    
    async def _sample():
        try:
            if table:
                # Show sample from specific table
                query = f"SELECT TOP {limit} * FROM [{table}]"
                request = QueryRequest(
                    connection_id=connection_id,
                    query=query,
                    database=database
                )
            else:
                # Show tables in database
                query = """
                SELECT 
                    TABLE_SCHEMA,
                    TABLE_NAME,
                    TABLE_TYPE
                FROM INFORMATION_SCHEMA.TABLES 
                WHERE TABLE_CATALOG = ?
                ORDER BY TABLE_SCHEMA, TABLE_NAME
                """
                request = QueryRequest(
                    connection_id=connection_id,
                    query=query,
                    database=database,
                    parameters=[database]
                )
            
            # Execute query
            query_executor = QueryExecutor()
            result = await query_executor.execute_query(request)
            
            if result.status == "error":
                click.echo(f"Sample query failed: {result.error_message}", err=True)
                raise click.Abort()
            
            # Format output
            if output == "json":
                import json
                click.echo(json.dumps(result.to_dict(), indent=2))
            else:
                _output_table(result, limit)
            
        except Exception as e:
            logger.error("Sample query failed", error=str(e))
            click.echo(f"Sample query failed: {e}", err=True)
            raise click.Abort()
    
    asyncio.run(_sample())


@query_group.command()
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
            query = """
            SELECT 
                TABLE_SCHEMA,
                TABLE_NAME,
                TABLE_TYPE
            FROM INFORMATION_SCHEMA.TABLES 
            WHERE TABLE_CATALOG = ?
            ORDER BY TABLE_SCHEMA, TABLE_NAME
            """
            
            request = QueryRequest(
                connection_id=connection_id,
                query=query,
                database=database,
                parameters=[database]
            )
            
            # Execute query
            query_executor = QueryExecutor()
            result = await query_executor.execute_query(request)
            
            if result.status == "error":
                click.echo(f"Tables query failed: {result.error_message}", err=True)
                raise click.Abort()
            
            # Format output
            if output == "json":
                import json
                click.echo(json.dumps(result.to_dict(), indent=2))
            else:
                _output_table(result)
            
        except Exception as e:
            logger.error("Tables query failed", error=str(e))
            click.echo(f"Tables query failed: {e}", err=True)
            raise click.Abort()
    
    asyncio.run(_tables())


@query_group.command()
@click.argument("connection_id")
@click.argument("database")
@click.argument("table")
@click.option(
    "--output", "-o",
    type=click.Choice(["table", "json"]),
    default="table",
    help="Output format"
)
def describe(connection_id: str, database: str, table: str, output: str) -> None:
    """Describe table structure (columns, types, constraints)."""
    
    async def _describe():
        try:
            query = """
            SELECT 
                COLUMN_NAME,
                DATA_TYPE,
                IS_NULLABLE,
                CHARACTER_MAXIMUM_LENGTH,
                NUMERIC_PRECISION,
                NUMERIC_SCALE,
                COLUMN_DEFAULT
            FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_CATALOG = ? AND TABLE_NAME = ?
            ORDER BY ORDINAL_POSITION
            """
            
            request = QueryRequest(
                connection_id=connection_id,
                query=query,
                database=database,
                parameters=[database, table]
            )
            
            # Execute query
            query_executor = QueryExecutor()
            result = await query_executor.execute_query(request)
            
            if result.status == "error":
                click.echo(f"Describe query failed: {result.error_message}", err=True)
                raise click.Abort()
            
            # Format output
            if output == "json":
                import json
                click.echo(json.dumps(result.to_dict(), indent=2))
            else:
                _output_table(result)
            
        except Exception as e:
            logger.error("Describe query failed", error=str(e))
            click.echo(f"Describe query failed: {e}", err=True)
            raise click.Abort()
    
    asyncio.run(_describe())


def _output_table(result: Any, limit: Optional[int] = None) -> None:
    """Output query result in table format."""
    if not result.data:
        click.echo("No data returned")
        return
    
    # Import rich for table formatting
    try:
        from rich.console import Console
        from rich.table import Table
        
        console = Console()
        table = Table(show_header=True, header_style="bold magenta")
        
        # Add columns
        for col in result.columns:
            table.add_column(col)
        
        # Add rows
        rows_to_show = result.data[:limit] if limit else result.data
        for row in rows_to_show:
            table.add_row(*[str(cell) for cell in row])
        
        console.print(table)
        
        # Show summary
        if limit and len(result.data) > limit:
            click.echo(f"\nShowing {limit} of {len(result.data)} rows")
        
        if result.rows_affected is not None:
            click.echo(f"Rows affected: {result.rows_affected}")
        
        if result.execution_time_ms:
            click.echo(f"Execution time: {result.execution_time_ms:.2f}ms")
            
    except ImportError:
        # Fallback to simple text output
        _output_simple_table(result, limit)


def _output_simple_table(result: Any, limit: Optional[int] = None) -> None:
    """Simple text table output without rich."""
    if not result.data:
        click.echo("No data returned")
        return
    
    # Calculate column widths
    col_widths = []
    for i, col in enumerate(result.columns):
        max_width = len(col)
        for row in result.data:
            if i < len(row):
                max_width = max(max_width, len(str(row[i])))
        col_widths.append(min(max_width, 50))  # Cap at 50 chars
    
    # Print header
    header = " | ".join(col.ljust(col_widths[i]) for i, col in enumerate(result.columns))
    click.echo(header)
    click.echo("-" * len(header))
    
    # Print rows
    rows_to_show = result.data[:limit] if limit else result.data
    for row in rows_to_show:
        row_str = " | ".join(str(row[i] if i < len(row) else "").ljust(col_widths[i]) 
                            for i in range(len(result.columns)))
        click.echo(row_str)
    
    # Show summary
    if limit and len(result.data) > limit:
        click.echo(f"\nShowing {limit} of {len(result.data)} rows")


def _output_csv(result: Any) -> None:
    """Output query result in CSV format."""
    import csv
    import io
    
    if not result.data:
        click.echo("No data returned")
        return
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow(result.columns)
    
    # Write data
    for row in result.data:
        writer.writerow(row)
    
    click.echo(output.getvalue())