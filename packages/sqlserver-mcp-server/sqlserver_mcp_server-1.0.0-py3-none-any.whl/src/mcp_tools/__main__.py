"""
Entry point for running the MCP tools as a module.

This allows running the MCP tools with: python -m sqlserver_mcp.mcp_tools
"""

import asyncio
from .mcp_server import SQLServerMCPServer


async def main():
    """Main entry point for the MCP tools module."""
    print("SQL Server MCP Server Tools")
    print("=" * 40)
    
    try:
        # Create and start the server
        server = SQLServerMCPServer()
        await server.start()
        
        print("Server started successfully!")
        print("Press Ctrl+C to stop the server")
        
        # Keep the server running
        await server.wait_for_shutdown()
        
    except KeyboardInterrupt:
        print("\nShutting down server...")
    except Exception as e:
        print(f"Server error: {e}")


if __name__ == "__main__":
    asyncio.run(main())