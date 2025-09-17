"""
Entry point for running the CLI as a module.

This allows running the CLI with: python -m sqlserver_mcp.cli
"""

from .main import cli


if __name__ == "__main__":
    cli()