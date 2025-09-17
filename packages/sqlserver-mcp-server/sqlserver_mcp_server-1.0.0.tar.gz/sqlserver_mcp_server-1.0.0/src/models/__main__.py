"""
Entry point for running the models as a module.

This allows running the models with: python -m sqlserver_mcp.models
"""

from .connection import ConnectionParams, ConnectionStatus
from .query import QueryRequest, QueryResult
from .schema import (
    Column, Index, Relationship, Table, Database,
    SchemaRequest, SchemaResult
)


def main():
    """Main entry point for the models module."""
    print("SQL Server MCP Server Models")
    print("=" * 40)
    
    print("Available models:")
    print("  - ConnectionParams, ConnectionStatus")
    print("  - QueryRequest, QueryResult")
    print("  - Column, Index, Relationship, Table, Database")
    print("  - SchemaRequest, SchemaResult")
    
    print("\nModels are ready for use!")


if __name__ == "__main__":
    main()