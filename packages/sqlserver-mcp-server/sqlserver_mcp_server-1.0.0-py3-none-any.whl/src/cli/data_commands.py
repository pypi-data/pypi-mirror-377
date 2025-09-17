"""
Data CLI commands for SQL Server MCP Server.

This module provides command-line interface commands for
retrieving and exploring table data.
"""

import click
from typing import Optional, List
import structlog
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from ..services.data_service import DataService
from ..services.connection_manager import ConnectionManager

logger = structlog.get_logger(__name__)
console = Console()


@click.group()
def data_group():
    """Data retrieval commands."""
    pass


@data_group.command()
@click.option(
    "--connection-id", "-c",
    required=True,
    help="Connection ID to use"
)
@click.option(
    "--database", "-d",
    required=True,
    help="Database name"
)
@click.option(
    "--table", "-t",
    required=True,
    help="Table name"
)
@click.option(
    "--limit", "-l",
    type=int,
    default=100,
    help="Maximum number of rows to return (default: 100)"
)
@click.option(
    "--offset", "-o",
    type=int,
    default=0,
    help="Number of rows to skip (default: 0)"
)
@click.option(
    "--where",
    help="WHERE clause for filtering"
)
@click.option(
    "--order-by",
    help="ORDER BY clause for sorting"
)
@click.option(
    "--columns",
    help="Comma-separated list of columns to retrieve"
)
@click.option(
    "--output", "-f",
    type=click.Choice(["table", "json", "csv"]),
    default="table",
    help="Output format (default: table)"
)
def select(
    connection_id: str,
    database: str,
    table: str,
    limit: int,
    offset: int,
    where: Optional[str],
    order_by: Optional[str],
    columns: Optional[str],
    output: str
):
    """Select data from a table."""
    try:
        # Parse columns
        column_list = None
        if columns:
            column_list = [col.strip() for col in columns.split(",")]
        
        # Create services
        connection_manager = ConnectionManager()
        data_service = DataService(connection_manager)
        
        # Get table data
        result = data_service.get_table_data(
            connection_id=connection_id,
            table=table,
            database=database,
            limit=limit,
            offset=offset,
            where_clause=where,
            order_by=order_by,
            columns=column_list
        )
        
        if result["success"]:
            _display_table_data(result, output)
        else:
            click.echo(f"❌ Failed to retrieve table data", err=True)
            raise click.Abort()
        
        logger.info(
            "CLI table data retrieved",
            connection_id=connection_id,
            database=database,
            table=table,
            row_count=len(result["data"])
        )
        
    except Exception as e:
        click.echo(f"❌ Failed to select data: {str(e)}", err=True)
        logger.error("CLI data selection failed", error=str(e))
        raise click.Abort()


@data_group.command()
@click.option(
    "--connection-id", "-c",
    required=True,
    help="Connection ID to use"
)
@click.option(
    "--database", "-d",
    required=True,
    help="Database name"
)
@click.option(
    "--table", "-t",
    required=True,
    help="Table name"
)
@click.option(
    "--sample-size", "-s",
    type=int,
    default=10,
    help="Number of sample rows (default: 10)"
)
@click.option(
    "--columns",
    help="Comma-separated list of columns to retrieve"
)
@click.option(
    "--output", "-f",
    type=click.Choice(["table", "json", "csv"]),
    default="table",
    help="Output format (default: table)"
)
def sample(
    connection_id: str,
    database: str,
    table: str,
    sample_size: int,
    columns: Optional[str],
    output: str
):
    """Get a sample of data from a table."""
    try:
        # Parse columns
        column_list = None
        if columns:
            column_list = [col.strip() for col in columns.split(",")]
        
        # Create services
        connection_manager = ConnectionManager()
        data_service = DataService(connection_manager)
        
        # Get table sample
        result = data_service.get_table_sample(
            connection_id=connection_id,
            table=table,
            database=database,
            sample_size=sample_size,
            columns=column_list
        )
        
        if result["success"]:
            _display_table_data(result, output)
        else:
            click.echo(f"❌ Failed to retrieve table sample", err=True)
            raise click.Abort()
        
        logger.info(
            "CLI table sample retrieved",
            connection_id=connection_id,
            database=database,
            table=table,
            sample_size=sample_size
        )
        
    except Exception as e:
        click.echo(f"❌ Failed to get table sample: {str(e)}", err=True)
        logger.error("CLI table sample failed", error=str(e))
        raise click.Abort()


@data_group.command()
@click.option(
    "--connection-id", "-c",
    required=True,
    help="Connection ID to use"
)
@click.option(
    "--database", "-d",
    required=True,
    help="Database name"
)
@click.option(
    "--table", "-t",
    required=True,
    help="Table name"
)
@click.option(
    "--search-term", "-s",
    required=True,
    help="Term to search for"
)
@click.option(
    "--columns",
    help="Comma-separated list of columns to search in"
)
@click.option(
    "--limit", "-l",
    type=int,
    default=100,
    help="Maximum number of results (default: 100)"
)
@click.option(
    "--output", "-f",
    type=click.Choice(["table", "json", "csv"]),
    default="table",
    help="Output format (default: table)"
)
def search(
    connection_id: str,
    database: str,
    table: str,
    search_term: str,
    columns: Optional[str],
    limit: int,
    output: str
):
    """Search for data in a table."""
    try:
        # Parse columns
        column_list = None
        if columns:
            column_list = [col.strip() for col in columns.split(",")]
        
        # Create services
        connection_manager = ConnectionManager()
        data_service = DataService(connection_manager)
        
        # Search table data
        result = data_service.search_table_data(
            connection_id=connection_id,
            table=table,
            database=database,
            search_term=search_term,
            search_columns=column_list,
            limit=limit
        )
        
        if result["success"]:
            _display_table_data(result, output)
        else:
            click.echo(f"❌ Failed to search table data", err=True)
            raise click.Abort()
        
        logger.info(
            "CLI table search completed",
            connection_id=connection_id,
            database=database,
            table=table,
            search_term=search_term,
            result_count=len(result["data"])
        )
        
    except Exception as e:
        click.echo(f"❌ Failed to search data: {str(e)}", err=True)
        logger.error("CLI data search failed", error=str(e))
        raise click.Abort()


@data_group.command()
@click.option(
    "--connection-id", "-c",
    required=True,
    help="Connection ID to use"
)
@click.option(
    "--database", "-d",
    required=True,
    help="Database name"
)
@click.option(
    "--table", "-t",
    required=True,
    help="Table name"
)
def statistics(
    connection_id: str,
    database: str,
    table: str
):
    """Get statistics about a table."""
    try:
        # Create services
        connection_manager = ConnectionManager()
        data_service = DataService(connection_manager)
        
        # Get table statistics
        stats = data_service.get_table_statistics(
            connection_id=connection_id,
            table=table,
            database=database
        )
        
        # Display statistics
        _display_table_statistics(stats)
        
        logger.info(
            "CLI table statistics displayed",
            connection_id=connection_id,
            database=database,
            table=table
        )
        
    except Exception as e:
        click.echo(f"❌ Failed to get table statistics: {str(e)}", err=True)
        logger.error("CLI table statistics failed", error=str(e))
        raise click.Abort()


def _display_table_data(result: dict, output_format: str):
    """Display table data in the specified format."""
    data = result["data"]
    columns = result["columns"]
    pagination = result["pagination"]
    
    # Show pagination info
    if pagination["has_more"]:
        click.echo(f"📊 Showing {len(data)} of {pagination['total_rows']} rows")
    else:
        click.echo(f"📊 Showing {len(data)} rows")
    
    if output_format == "table":
        _display_data_table(data, columns)
    elif output_format == "json":
        import json
        console.print_json(json.dumps(data, indent=2))
    elif output_format == "csv":
        _display_data_csv(data, columns)
    
    # Show metadata
    metadata = result["metadata"]
    click.echo()
    click.echo(f"⏱️  Execution time: {metadata['execution_time_ms']:.2f}ms")
    click.echo(f"🖥️  Server: {metadata['server']}")
    click.echo(f"📅 Timestamp: {metadata['timestamp']}")


def _display_data_table(data: List[dict], columns: List[dict]):
    """Display data as a table."""
    if not data:
        click.echo("📊 No data found")
        return
    
    # Create table
    table = Table(show_header=True, header_style="bold magenta")
    
    # Add columns
    for col in columns:
        table.add_column(col["name"], style="cyan")
    
    # Add rows
    for row in data:
        table.add_row(*[str(row.get(col["name"], "")) for col in columns])
    
    console.print(table)


def _display_data_csv(data: List[dict], columns: List[dict]):
    """Display data as CSV."""
    if not data:
        return
    
    # Header
    header = ",".join([f'"{col["name"]}"' for col in columns])
    click.echo(header)
    
    # Data rows
    for row in data:
        values = []
        for col in columns:
            value = row.get(col["name"], "")
            # Escape quotes and wrap in quotes
            value_str = str(value).replace('"', '""')
            values.append(f'"{value_str}"')
        click.echo(",".join(values))


def _display_table_statistics(stats: dict):
    """Display table statistics."""
    panel = Panel.fit(
        f"📊 Table: {stats['table']}\n"
        f"🗄️  Database: {stats['database']}\n"
        f"📋 Rows: {stats['row_count']:,}\n"
        f"📝 Columns: {stats['column_count']}\n"
        f"💾 Size: {stats['size_mb']:.2f} MB\n"
        f"📅 Retrieved: {stats['timestamp']}",
        title="Table Statistics",
        border_style="green"
    )
    console.print(panel)


# Export the command group
data_commands = data_group
