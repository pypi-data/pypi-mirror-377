"""
Example MCP client for SQL Server MCP Server.

This example demonstrates how to use the SQL Server MCP Server
with a simple MCP client.
"""

import asyncio
import json
import structlog
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

logger = structlog.get_logger(__name__)


async def main():
    """Example MCP client usage."""
    logger.info("Starting MCP client example")
    
    # Server parameters
    server_params = StdioServerParameters(
        command="python",
        args=["src/main.py"]
    )
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize the session
            await session.initialize()
            
            # List available tools
            tools = await session.list_tools()
            logger.info("Available tools", tools=[tool.name for tool in tools.tools])
            
            # Example 1: Create a connection
            logger.info("Creating connection...")
            create_result = await session.call_tool(
                "create_connection",
                {
                    "server": "localhost",
                    "database": "master",
                    "trusted_connection": True,
                    "encrypt": True
                }
            )
            
            connection_data = json.loads(create_result.content[0].text)
            connection_id = connection_data.get("connection_id")
            logger.info("Connection created", connection_id=connection_id)
            
            # Example 2: List databases
            logger.info("Listing databases...")
            databases_result = await session.call_tool(
                "list_databases",
                {
                    "include_system": False,
                    "include_metadata": True,
                    "connection_id": connection_id
                }
            )
            
            databases_data = json.loads(databases_result.content[0].text)
            logger.info("Databases found", count=len(databases_data.get("databases", [])))
            
            # Example 3: Execute a simple query
            logger.info("Executing query...")
            query_result = await session.call_tool(
                "execute_query",
                {
                    "query": "SELECT 1 as test_column, 'Hello MCP' as message",
                    "connection_id": connection_id
                }
            )
            
            query_data = json.loads(query_result.content[0].text)
            logger.info("Query executed", success=query_data.get("success"))
            
            # Example 4: Get schema information
            logger.info("Getting schema...")
            schema_result = await session.call_tool(
                "get_schema",
                {
                    "database": "master",
                    "connection_id": connection_id
                }
            )
            
            schema_data = json.loads(schema_result.content[0].text)
            logger.info("Schema retrieved", success=schema_data.get("success"))
            
            logger.info("MCP client example completed successfully")


if __name__ == "__main__":
    asyncio.run(main())
