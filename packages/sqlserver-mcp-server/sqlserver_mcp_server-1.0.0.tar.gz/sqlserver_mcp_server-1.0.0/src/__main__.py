"""
Entry point for running the SQL Server MCP Server as a module.

This allows running the server with: python -m sqlserver_mcp
"""

import sys
import asyncio
from .mcp_tools.mcp_server import SQLServerMCPServer


async def main():
    """Main entry point for the MCP server."""
    try:
        # Create and start the server
        server = SQLServerMCPServer()
        await server.start()
        
        # Keep the server running
        await server.wait_for_shutdown()
        
    except KeyboardInterrupt:
        print("\nShutting down server...")
    except Exception as e:
        print(f"Server error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
