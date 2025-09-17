"""
Main entry point for SQL Server MCP Server.

This module provides the main entry point for running the MCP server
and handles command line arguments and configuration.
"""

import asyncio
import sys
import argparse
from typing import Optional
import structlog

from .mcp_tools.mcp_server import main as mcp_main
from .lib.logging import setup_logging
from .lib.exceptions import MCPError


logger = structlog.get_logger(__name__)


def parse_arguments() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="SQL Server MCP Server - Comprehensive SQL Server operations via MCP protocol",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m src.main                    # Run MCP server
  python -m src.main --log-level debug  # Run with debug logging
  python -m src.main --version          # Show version information
        """
    )
    
    parser.add_argument(
        "--log-level",
        choices=["debug", "info", "warning", "error"],
        default="info",
        help="Set the logging level (default: info)"
    )
    
    parser.add_argument(
        "--log-file",
        type=str,
        help="Log to a specific file (default: stdout)"
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version="SQL Server MCP Server 1.0.0"
    )
    
    parser.add_argument(
        "--config",
        type=str,
        help="Path to configuration file (not implemented yet)"
    )
    
    return parser.parse_args()


def setup_logging_from_args(args: argparse.Namespace) -> None:
    """Setup logging based on command line arguments."""
    log_level = args.log_level.upper()
    log_file = args.log_file
    
    setup_logging(level=log_level, log_file=log_file)


async def run_server() -> None:
    """Run the MCP server."""
    try:
        logger.info("Starting SQL Server MCP Server")
        await mcp_main()
    except KeyboardInterrupt:
        logger.info("Server interrupted by user")
    except Exception as e:
        logger.error("Server failed", error=str(e))
        raise


def main() -> None:
    """Main entry point."""
    try:
        # Parse arguments
        args = parse_arguments()
        
        # Setup logging
        setup_logging_from_args(args)
        
        # Log startup information
        logger.info("SQL Server MCP Server starting", 
                   version="1.0.0",
                   log_level=args.log_level)
        
        # Run the server
        asyncio.run(run_server())
        
    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error("Application failed", error=str(e))
        sys.exit(1)


if __name__ == "__main__":
    main()