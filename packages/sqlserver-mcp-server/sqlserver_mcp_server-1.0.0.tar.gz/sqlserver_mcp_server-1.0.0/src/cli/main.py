"""
Main CLI entry point for SQL Server MCP Server.

This module provides the main CLI interface and command groups.
"""

import click
import structlog
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from .connection_commands import connection_group
from .query_commands import query_group
from .schema_commands import schema_group
from .config_commands import config_group
from ..lib.config import ConfigManager
from ..lib.logging import setup_logging


console = Console()


@click.group()
@click.option(
    "--verbose", "-v",
    is_flag=True,
    help="Enable verbose logging"
)
@click.option(
    "--log-level",
    type=click.Choice(["DEBUG", "INFO", "WARNING", "ERROR"]),
    default="INFO",
    help="Set logging level"
)
@click.option(
    "--config-file",
    type=click.Path(),
    help="Path to configuration file"
)
@click.pass_context
def cli(ctx: click.Context, verbose: bool, log_level: str, config_file: str) -> None:
    """
    SQL Server MCP Server CLI
    
    A command-line interface for interacting with SQL Server databases
    through the Model Context Protocol (MCP) server.
    """
    
    # Ensure context object exists
    ctx.ensure_object(dict)
    
    # Set up logging
    setup_logging(log_level if not verbose else "DEBUG")
    logger = structlog.get_logger(__name__)
    
    # Load configuration
    try:
        config_manager = ConfigManager()
        if config_file:
            config_manager.load_config_file(config_file)
        config = config_manager.get_config()
        ctx.obj["config"] = config
        ctx.obj["config_manager"] = config_manager
    except Exception as e:
        logger.error("Failed to load configuration", error=str(e))
        if not verbose:
            click.echo(f"Warning: Configuration load failed: {e}", err=True)
    
    # Show banner in verbose mode
    if verbose:
        _show_banner()


# Add command groups
cli.add_command(connection_group, name="connection")
cli.add_command(query_group, name="query")
cli.add_command(schema_group, name="schema")
cli.add_command(config_group, name="config")


@cli.command()
def version() -> None:
    """Show version information."""
    try:
        from .. import __version__
        click.echo(f"SQL Server MCP Server CLI v{__version__}")
    except ImportError:
        click.echo("SQL Server MCP Server CLI (version unknown)")


@cli.command()
def info() -> None:
    """Show system information."""
    import platform
    import sys
    
    click.echo("System Information:")
    click.echo("=" * 40)
    click.echo(f"Python Version: {sys.version}")
    click.echo(f"Platform: {platform.platform()}")
    click.echo(f"Architecture: {platform.architecture()[0]}")
    click.echo(f"Machine: {platform.machine()}")
    click.echo(f"Processor: {platform.processor()}")


@cli.command()
@click.option(
    "--output", "-o",
    type=click.Choice(["table", "json"]),
    default="table",
    help="Output format"
)
def status(output: str) -> None:
    """Show server status."""
    
    try:
        # This would typically connect to the MCP server
        # For now, we'll show a placeholder status
        status_info = {
            "server_status": "unknown",
            "active_connections": 0,
            "uptime": "unknown",
            "version": "unknown"
        }
        
        if output == "json":
            import json
            click.echo(json.dumps(status_info, indent=2))
        else:
            click.echo("Server Status:")
            click.echo("=" * 30)
            click.echo(f"Status: {status_info['server_status']}")
            click.echo(f"Active Connections: {status_info['active_connections']}")
            click.echo(f"Uptime: {status_info['uptime']}")
            click.echo(f"Version: {status_info['version']}")
            
    except Exception as e:
        click.echo(f"Status check failed: {e}", err=True)


def _show_banner() -> None:
    """Show application banner."""
    banner_text = Text("SQL Server MCP Server CLI", style="bold blue")
    banner = Panel(
        banner_text,
        title="[bold green]Welcome[/bold green]",
        border_style="blue",
        padding=(1, 2)
    )
    console.print(banner)


if __name__ == "__main__":
    cli()