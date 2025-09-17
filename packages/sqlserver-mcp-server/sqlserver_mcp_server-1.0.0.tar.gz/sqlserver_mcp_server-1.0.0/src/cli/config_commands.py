"""
Configuration management commands for SQL Server MCP Server CLI.

This module provides CLI commands for managing configuration.
"""

import click
import json
import os
from pathlib import Path
from typing import Dict, Any, Optional
import structlog

from ..lib.config import ConfigManager
from ..lib.exceptions import ConfigError


logger = structlog.get_logger(__name__)


@click.group()
def config_group() -> None:
    """Manage configuration."""
    pass


@config_group.command()
@click.option(
    "--output", "-o",
    type=click.Choice(["table", "json"]),
    default="table",
    help="Output format"
)
def show(output: str) -> None:
    """Show current configuration."""
    
    try:
        config_manager = ConfigManager()
        config = config_manager.get_config()
        
        if output == "json":
            click.echo(json.dumps(config, indent=2))
        else:
            _output_config_table(config)
        
    except Exception as e:
        logger.error("Config show failed", error=str(e))
        click.echo(f"Config show failed: {e}", err=True)
        raise click.Abort()


@config_group.command()
@click.argument("key")
@click.argument("value")
def set(key: str, value: str) -> None:
    """Set a configuration value."""
    
    try:
        config_manager = ConfigManager()
        
        # Parse value based on key type
        parsed_value = _parse_config_value(key, value)
        
        # Set the value
        config_manager.set_config_value(key, parsed_value)
        
        click.echo(f"Configuration updated: {key} = {parsed_value}")
        logger.info("Config value set", key=key, value=parsed_value)
        
    except Exception as e:
        logger.error("Config set failed", error=str(e))
        click.echo(f"Config set failed: {e}", err=True)
        raise click.Abort()


@config_group.command()
@click.argument("key")
def get(key: str) -> None:
    """Get a configuration value."""
    
    try:
        config_manager = ConfigManager()
        value = config_manager.get_config_value(key)
        
        if value is None:
            click.echo(f"Configuration key '{key}' not found")
        else:
            click.echo(f"{key} = {value}")
        
    except Exception as e:
        logger.error("Config get failed", error=str(e))
        click.echo(f"Config get failed: {e}", err=True)
        raise click.Abort()


@config_group.command()
@click.argument("key")
def unset(key: str) -> None:
    """Remove a configuration value."""
    
    try:
        config_manager = ConfigManager()
        config_manager.unset_config_value(key)
        
        click.echo(f"Configuration key '{key}' removed")
        logger.info("Config value unset", key=key)
        
    except Exception as e:
        logger.error("Config unset failed", error=str(e))
        click.echo(f"Config unset failed: {e}", err=True)
        raise click.Abort()


@config_group.command()
@click.option(
    "--force/--no-force",
    default=False,
    help="Force reset without confirmation"
)
def reset(force: bool) -> None:
    """Reset configuration to defaults."""
    
    if not force:
        if not click.confirm("Are you sure you want to reset all configuration to defaults?"):
            click.echo("Configuration reset cancelled")
            return
    
    try:
        config_manager = ConfigManager()
        config_manager.reset_to_defaults()
        
        click.echo("Configuration reset to defaults")
        logger.info("Config reset to defaults")
        
    except Exception as e:
        logger.error("Config reset failed", error=str(e))
        click.echo(f"Config reset failed: {e}", err=True)
        raise click.Abort()


@config_group.command()
@click.argument("file_path", type=click.Path(exists=True))
@click.option(
    "--force/--no-force",
    default=False,
    help="Force import without confirmation"
)
def import_config(file_path: str, force: bool) -> None:
    """Import configuration from a JSON file."""
    
    if not force:
        if not click.confirm(f"Are you sure you want to import configuration from {file_path}?"):
            click.echo("Configuration import cancelled")
            return
    
    try:
        config_manager = ConfigManager()
        
        # Load configuration from file
        with open(file_path, 'r') as f:
            imported_config = json.load(f)
        
        # Import the configuration
        config_manager.import_config(imported_config)
        
        click.echo(f"Configuration imported from {file_path}")
        logger.info("Config imported", file_path=file_path)
        
    except Exception as e:
        logger.error("Config import failed", error=str(e))
        click.echo(f"Config import failed: {e}", err=True)
        raise click.Abort()


@config_group.command()
@click.argument("file_path", type=click.Path())
def export_config(file_path: str) -> None:
    """Export configuration to a JSON file."""
    
    try:
        config_manager = ConfigManager()
        config = config_manager.get_config()
        
        # Ensure directory exists
        file_path_obj = Path(file_path)
        file_path_obj.parent.mkdir(parents=True, exist_ok=True)
        
        # Export configuration
        with open(file_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        click.echo(f"Configuration exported to {file_path}")
        logger.info("Config exported", file_path=file_path)
        
    except Exception as e:
        logger.error("Config export failed", error=str(e))
        click.echo(f"Config export failed: {e}", err=True)
        raise click.Abort()


@config_group.command()
@click.option(
    "--output", "-o",
    type=click.Choice(["table", "json"]),
    default="table",
    help="Output format"
)
def validate(output: str) -> None:
    """Validate current configuration."""
    
    try:
        config_manager = ConfigManager()
        validation_result = config_manager.validate_config()
        
        if output == "json":
            click.echo(json.dumps(validation_result, indent=2))
        else:
            _output_validation_table(validation_result)
        
        if validation_result["valid"]:
            click.echo("Configuration is valid")
        else:
            click.echo("Configuration has errors", err=True)
            raise click.Abort()
        
    except Exception as e:
        logger.error("Config validation failed", error=str(e))
        click.echo(f"Config validation failed: {e}", err=True)
        raise click.Abort()


def _parse_config_value(key: str, value: str) -> Any:
    """Parse configuration value based on key type."""
    # Define known configuration keys and their types
    config_types = {
        "log_level": str,
        "log_format": str,
        "default_timeout": int,
        "default_pool_size": int,
        "default_encrypt": bool,
        "default_trusted_connection": bool,
        "output_format": str,
        "max_rows": int,
        "page_size": int,
    }
    
    value_type = config_types.get(key, str)
    
    if value_type == bool:
        return value.lower() in ("true", "1", "yes", "on")
    elif value_type == int:
        return int(value)
    else:
        return value


def _output_config_table(config: Dict[str, Any]) -> None:
    """Output configuration in table format."""
    click.echo("Current Configuration:")
    click.echo("=" * 40)
    
    for key, value in config.items():
        click.echo(f"  {key:<25} = {value}")


def _output_validation_table(validation_result: Dict[str, Any]) -> None:
    """Output validation result in table format."""
    click.echo("Configuration Validation:")
    click.echo("=" * 40)
    
    if validation_result["valid"]:
        click.echo("✓ Configuration is valid")
    else:
        click.echo("✗ Configuration has errors")
        
        if "errors" in validation_result:
            click.echo("\nErrors:")
            for error in validation_result["errors"]:
                click.echo(f"  - {error}")
        
        if "warnings" in validation_result:
            click.echo("\nWarnings:")
            for warning in validation_result["warnings"]:
                click.echo(f"  - {warning}")