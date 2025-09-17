"""
Connection management commands for SQL Server MCP Server CLI.

This module provides CLI commands for managing database connections.
"""

import click
import asyncio
from typing import Optional
import structlog

from ..services.connection_manager import ConnectionManager
from ..models.connection import ConnectionConfig
from ..lib.exceptions import ConnectionError


logger = structlog.get_logger(__name__)


@click.group()
def connection_group() -> None:
    """Manage database connections."""
    pass


@connection_group.command()
@click.option(
    "--server", "-s",
    required=True,
    help="SQL Server instance name or IP address"
)
@click.option(
    "--database", "-d",
    help="Default database name"
)
@click.option(
    "--username", "-u",
    help="SQL Server username (required if not using Windows Auth)"
)
@click.option(
    "--password", "-p",
    help="SQL Server password (required if not using Windows Auth)"
)
@click.option(
    "--trusted-connection/--no-trusted-connection",
    default=True,
    help="Use Windows Authentication (default: True)"
)
@click.option(
    "--encrypt/--no-encrypt",
    default=True,
    help="Encrypt connection (default: True)"
)
@click.option(
    "--timeout",
    type=int,
    default=30,
    help="Connection timeout in seconds (default: 30)"
)
@click.option(
    "--pool-size",
    type=int,
    default=10,
    help="Connection pool size (default: 10)"
)
@click.option(
    "--output", "-o",
    type=click.Choice(["table", "json"]),
    default="table",
    help="Output format"
)
def connect(
    server: str,
    database: Optional[str],
    username: Optional[str],
    password: Optional[str],
    trusted_connection: bool,
    encrypt: bool,
    timeout: int,
    pool_size: int,
    output: str
) -> None:
    """Connect to a SQL Server database."""
    
    async def _connect():
        try:
            # Create connection configuration
            config = ConnectionConfig(
                server=server,
                database=database,
                username=username,
                password=password,
                trusted_connection=trusted_connection,
                encrypt=encrypt,
                connection_timeout=timeout,
                pool_size=pool_size
            )
            
            # Create connection manager
            connection_manager = ConnectionManager()
            
            # Create connection
            connection_id = await connection_manager.create_connection(config)
            
            # Get connection status
            status = await connection_manager.get_connection_status(connection_id)
            
            if output == "json":
                import json
                result = {
                    "success": True,
                    "connection_id": connection_id,
                    "status": status.to_dict() if status else None
                }
                click.echo(json.dumps(result, indent=2))
            else:
                # Table output
                click.echo("Connection created successfully!")
                click.echo("=" * 40)
                click.echo(f"Connection ID: {connection_id}")
                click.echo(f"Server: {server}")
                click.echo(f"Database: {database or 'default'}")
                click.echo(f"Authentication: {'Windows' if trusted_connection else 'SQL Server'}")
                click.echo(f"Encrypted: {encrypt}")
                click.echo(f"Pool Size: {pool_size}")
                
                if status:
                    click.echo(f"Status: {'Connected' if status.connected else 'Disconnected'}")
                    click.echo(f"Response Time: {status.response_time_ms:.2f}ms")
            
            # Store connection ID for future use
            # This would typically be stored in a config file or session
            logger.info("Connection created", connection_id=connection_id, server=server)
            
        except Exception as e:
            logger.error("Connection failed", error=str(e))
            if output == "json":
                import json
                result = {"success": False, "error": str(e)}
                click.echo(json.dumps(result, indent=2))
            else:
                click.echo(f"Connection failed: {e}", err=True)
            raise click.Abort()
    
    asyncio.run(_connect())


@connection_group.command()
@click.option(
    "--connection-id",
    help="Specific connection ID to check (optional)"
)
@click.option(
    "--output", "-o",
    type=click.Choice(["table", "json"]),
    default="table",
    help="Output format"
)
def status(connection_id: Optional[str], output: str) -> None:
    """Show connection status."""
    
    async def _status():
        try:
            connection_manager = ConnectionManager()
            
            if connection_id:
                # Get specific connection status
                status = await connection_manager.get_connection_status(connection_id)
                if not status:
                    click.echo(f"Connection {connection_id} not found", err=True)
                    raise click.Abort()
                
                connections = [status]
            else:
                # Get all connections
                connections = await connection_manager.list_connections()
            
            if output == "json":
                import json
                result = {
                    "connections": [conn.to_dict() for conn in connections]
                }
                click.echo(json.dumps(result, indent=2))
            else:
                # Table output
                if not connections:
                    click.echo("No active connections")
                    return
                
                click.echo(f"Active Connections ({len(connections)}):")
                click.echo("=" * 50)
                
                for conn in connections:
                    click.echo(f"ID: {conn.connection_id}")
                    click.echo(f"Server: {conn.server}")
                    click.echo(f"Database: {conn.database or 'default'}")
                    click.echo(f"Status: {'Connected' if conn.connected else 'Disconnected'}")
                    click.echo(f"Auth: {conn.authentication_method}")
                    click.echo(f"Response Time: {conn.response_time_ms:.2f}ms")
                    click.echo(f"Last Activity: {conn.last_activity}")
                    click.echo("-" * 30)
            
        except Exception as e:
            logger.error("Status check failed", error=str(e))
            if output == "json":
                import json
                result = {"error": str(e)}
                click.echo(json.dumps(result, indent=2))
            else:
                click.echo(f"Status check failed: {e}", err=True)
            raise click.Abort()
    
    asyncio.run(_status())


@connection_group.command()
@click.argument("connection_id")
@click.option(
    "--output", "-o",
    type=click.Choice(["table", "json"]),
    default="table",
    help="Output format"
)
def close(connection_id: str, output: str) -> None:
    """Close a database connection."""
    
    async def _close():
        try:
            connection_manager = ConnectionManager()
            
            # Close connection
            await connection_manager.close_connection(connection_id)
            
            if output == "json":
                import json
                result = {"success": True, "message": f"Connection {connection_id} closed"}
                click.echo(json.dumps(result, indent=2))
            else:
                click.echo(f"Connection {connection_id} closed successfully")
            
            logger.info("Connection closed", connection_id=connection_id)
            
        except Exception as e:
            logger.error("Close connection failed", error=str(e))
            if output == "json":
                import json
                result = {"success": False, "error": str(e)}
                click.echo(json.dumps(result, indent=2))
            else:
                click.echo(f"Close connection failed: {e}", err=True)
            raise click.Abort()
    
    asyncio.run(_close())


@connection_group.command()
@click.option(
    "--output", "-o",
    type=click.Choice(["table", "json"]),
    default="table",
    help="Output format"
)
def list_connections(output: str) -> None:
    """List all active connections."""
    # This is the same as status without connection_id
    status(None, output)