"""
CLI package for SQL Server MCP Server.

This package provides command-line interface functionality for the SQL Server MCP Server.
"""

from .main import cli
from .connection_commands import connection_group
from .query_commands import query_group
from .schema_commands import schema_group
from .config_commands import config_group

__all__ = [
    "cli",
    "connection_group",
    "query_group", 
    "schema_group",
    "config_group"
]