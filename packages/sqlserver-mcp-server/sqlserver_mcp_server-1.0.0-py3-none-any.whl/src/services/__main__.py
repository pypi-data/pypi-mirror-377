"""
Entry point for running the services as a module.

This allows running the services with: python -m sqlserver_mcp.services
"""

import asyncio
from .connection_manager import ConnectionManager
from .query_executor import QueryExecutor
from .schema_service import SchemaService
from .data_service import DataService


async def main():
    """Main entry point for the services module."""
    print("SQL Server MCP Server Services")
    print("=" * 40)
    
    # This is a placeholder for testing services
    # In a real application, you would have proper service initialization
    print("Available services:")
    print("  - ConnectionManager")
    print("  - QueryExecutor")
    print("  - SchemaService")
    print("  - DataService")
    
    print("\nServices are ready for use!")


if __name__ == "__main__":
    asyncio.run(main())