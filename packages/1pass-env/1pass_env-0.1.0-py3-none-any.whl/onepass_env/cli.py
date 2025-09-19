"""Main CLI interface for 1pass-env - Import command only."""

import os
import sys
from pathlib import Path
from typing import Optional

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from onepass_env.__about__ import __version__
from onepass_env.exceptions import OnePassEnvError

console = Console()


def print_version(ctx: click.Context, param: click.Parameter, value: bool) -> None:
    """Print version and exit."""
    if not value or ctx.resilient_parsing:
        return
    console.print(f"1pass-env version {__version__}")
    ctx.exit()


@click.group(invoke_without_command=True)
@click.option(
    "--version",
    is_flag=True,
    callback=print_version,
    expose_value=False,
    is_eager=True,
    help="Show version and exit.",
)
@click.pass_context
def cli(ctx: click.Context) -> None:
    """1pass-env: Import environment variables from 1Password.
    
    A focused CLI tool that imports secrets from 1Password items into
    environment files for your development workflow.
    """
    ctx.ensure_object(dict)
    
    if ctx.invoked_subcommand is None:
        console.print(Panel.fit(
            "[bold blue]1pass-env[/bold blue]\n\n"
            "Import environment variables from 1Password items.\n\n"
            f"Version: {__version__}\n\n"
            "Usage: [bold]1pass-env import [OPTIONS][/bold]\n"
            "Run [bold]1pass-env import --help[/bold] for details.",
            title="1pass-env"
        ))


@cli.command(name="import")
@click.option(
    "--vault",
    "-v",
    default="tokens",
    help="1Password vault name to import from (default: 'tokens').",
)
@click.option(
    "--name",
    "-n",
    help="Item name in vault (default: current folder name).",
)
@click.option(
    "--fields",
    "-f",
    help="Specific fields to import (comma-separated, e.g., API_KEY,SECRET_KEY). If not specified, imports all fields.",
)
@click.option(
    "--file",
    "env_file",
    default="1pass.env",
    help="Output file name (default: '1pass.env').",
)
@click.option(
    "--debug",
    is_flag=True,
    help="Enable debug logging.",
)
def import_command(
    vault: str,
    name: Optional[str],
    fields: Optional[str],
    env_file: str,
    debug: bool
) -> None:
    """Import environment variables from a 1Password item.
    
    This command imports secrets from an existing 1Password item into your
    environment file. By default, it imports all fields from the item.
    
    Examples:
    
    \b
        # Import all fields from current folder name
        1pass-env import
        
        # Import from specific item
        1pass-env import --name my-app
        
        # Import specific fields only
        1pass-env import --name my-app --fields API_KEY,DB_PASSWORD
        
        # Use different vault and output file
        1pass-env import --vault secrets --name my-app --file .env.prod
        
        # Enable debug logging
        1pass-env import --name my-app --debug
    """
    # Check service account token
    token = os.getenv("OP_SERVICE_ACCOUNT_TOKEN")
    if not token:
        console.print("[red]✗[/red] OP_SERVICE_ACCOUNT_TOKEN environment variable not set")
        console.print("\n[yellow]To fix this:[/yellow]")
        console.print("1. Create a service account at https://my.1password.com/developer-tools/infrastructure-secrets/serviceaccount")
        console.print("2. Export the token: [bold]export OP_SERVICE_ACCOUNT_TOKEN='your-token-here'[/bold]")
        sys.exit(1)
    
    # Get current folder name as default for item name
    if not name:
        name = Path.cwd().name
        if debug:
            console.print(f"[dim]Using current folder name as item name: {name}[/dim]")
    
    # Parse fields if provided
    field_list = None
    if fields:
        field_list = [field.strip() for field in fields.split(",")]
        if debug:
            console.print(f"[dim]Will import specific fields: {', '.join(field_list)}[/dim]")
    
    env_path = Path(env_file)
    
    # Check if file exists and ask for permission
    if env_path.exists():
        console.print(f"[yellow]⚠️[/yellow] File '{env_file}' already exists")
        if not click.confirm("Do you want to proceed and overwrite/merge with the existing file?"):
            console.print("[yellow]Operation cancelled[/yellow]")
            return
    
    try:
        from onepass_env.onepassword import OnePasswordClient
        
        if debug:
            console.print(f"[dim]Connecting to 1Password vault: {vault}[/dim]")
        
        op_client = OnePasswordClient(vault=vault, verbose=debug)
        
        # Check authentication
        if not op_client.is_authenticated():
            raise OnePassEnvError(
                "Not authenticated with 1Password. Please check your OP_SERVICE_ACCOUNT_TOKEN "
                "environment variable and ensure it has access to the specified vault."
            )
        
        # Search for the item by name
        if debug:
            console.print(f"[dim]Searching for item: {name}[/dim]")
        
        item = op_client.get_item_by_title(name)
        if not item:
            raise OnePassEnvError(f"Item '{name}' not found in vault '{vault}'")
        
        if debug:
            console.print(f"[dim]Found item: {item.title} (ID: {item.id})[/dim]")
        
        # Extract fields
        imported_vars = {}
        skipped_fields = []
        
        for field in item.fields:
            # Skip fields without titles or values
            if not field.title or not field.value:
                continue
            
            # If specific fields requested, check if this field is in the list
            if field_list and field.title not in field_list:
                skipped_fields.append(field.title)
                continue
            
            imported_vars[field.title] = field.value
            if debug:
                console.print(f"[dim]Imported field: {field.title}[/dim]")
        
        if not imported_vars:
            console.print(f"[yellow]![/yellow] No fields found to import from item '{name}'")
            if skipped_fields:
                console.print(f"[dim]Available fields: {', '.join(skipped_fields)}[/dim]")
            return
        
        # Read existing env file if it exists
        existing_vars = {}
        if env_path.exists():
            try:
                from dotenv import dotenv_values
                existing_vars = dict(dotenv_values(str(env_path)))
                if debug:
                    console.print(f"[dim]Found {len(existing_vars)} existing variables in {env_file}[/dim]")
            except Exception as e:
                if debug:
                    console.print(f"[dim]Could not read existing env file: {e}[/dim]")
        
        # Merge variables (imported variables take precedence)
        final_vars = {**existing_vars, **imported_vars}
        
        # Write to file
        with open(env_path, 'w') as f:
            # Add header comment
            f.write(f"# Environment variables imported from 1Password\n")
            f.write(f"# Vault: {vault}\n")
            f.write(f"# Item: {name}\n")
            f.write(f"# Generated by 1pass-env\n\n")
            
            # Write variables
            for key, value in final_vars.items():
                # Escape quotes in values
                escaped_value = str(value).replace('"', '\\"')
                f.write(f'{key}="{escaped_value}"\n')
        
        # Show summary
        console.print(f"[green]✓[/green] Successfully imported {len(imported_vars)} variables from '{name}'")
        console.print(f"[blue]ℹ[/blue] Saved to: {env_file}")
        
        # Show imported variables
        if debug or len(imported_vars) <= 10:
            table = Table(title="Imported Variables")
            table.add_column("Variable", style="cyan")
            table.add_column("Value", style="green")
            
            for key, value in imported_vars.items():
                # Mask the value for security
                masked_value = "*" * min(len(str(value)), 8) if not debug else str(value)
                table.add_row(key, masked_value)
            
            console.print(table)
        else:
            console.print(f"[dim]Use --debug to see all imported values[/dim]")
        
        if skipped_fields:
            console.print(f"[yellow]![/yellow] Skipped {len(skipped_fields)} fields not in filter")
            if debug:
                console.print(f"[dim]Skipped: {', '.join(skipped_fields)}[/dim]")
        
        # Show usage instructions
        console.print(f"\n[blue]💡[/blue] To use these variables:")
        console.print(f"   • Load manually: [bold]source {env_file}[/bold]")
        console.print(f"   • Use with dotenv: [bold]python-dotenv load {env_file}[/bold]")
        console.print(f"   • Docker: [bold]docker run --env-file {env_file} myapp[/bold]")
        
    except OnePassEnvError as e:
        console.print(f"[red]✗[/red] Error: {e}")
        sys.exit(1)
    except Exception as e:
        console.print(f"[red]✗[/red] Unexpected error: {e}")
        if debug:
            import traceback
            console.print(traceback.format_exc())
        sys.exit(1)


@cli.command(name="export")
@click.option(
    "--vault",
    "-v",
    default="tokens",
    help="1Password vault name to export to (default: 'tokens').",
)
@click.option(
    "--name",
    "-n",
    help="Item name for vault (default: current folder name).",
)
@click.option(
    "--fields",
    "-f",
    help="Specific fields to export (comma-separated, e.g., API_KEY,SECRET_KEY). If not specified, exports all fields.",
)
@click.option(
    "--file",
    "env_file",
    default=".env",
    help="Input file name (default: '.env').",
)
@click.option(
    "--overwrite",
    is_flag=True,
    help="Overwrite existing item in 1Password if it exists.",
)
@click.option(
    "--debug",
    is_flag=True,
    help="Enable debug logging.",
)
def export_command(
    vault: str,
    name: Optional[str],
    fields: Optional[str],
    env_file: str,
    overwrite: bool,
    debug: bool
) -> None:
    """Export environment variables from a file to 1Password.
    
    This command reads environment variables from a file and creates or updates
    a 1Password item with those values as secure fields.
    
    Examples:
    
    \b
        # Export all variables from .env to current folder name
        1pass-env export
        
        # Export from specific file to specific item
        1pass-env export --file .env.prod --name my-app-prod
        
        # Export specific fields only
        1pass-env export --fields API_KEY,DB_PASSWORD
        
        # Use different vault and overwrite existing item
        1pass-env export --vault secrets --name my-app --overwrite
        
        # Enable debug logging
        1pass-env export --name my-app --debug
    """
    # Check service account token
    token = os.getenv("OP_SERVICE_ACCOUNT_TOKEN")
    if not token:
        console.print("[red]✗[/red] OP_SERVICE_ACCOUNT_TOKEN environment variable not set")
        console.print("\n[yellow]To fix this:[/yellow]")
        console.print("1. Create a service account at https://my.1password.com/developer-tools/infrastructure-secrets/serviceaccount")
        console.print("2. Export the token: [bold]export OP_SERVICE_ACCOUNT_TOKEN='your-token-here'[/bold]")
        sys.exit(1)
    
    # Get current folder name as default for item name
    if not name:
        name = Path.cwd().name
        if debug:
            console.print(f"[dim]Using current folder name as item name: {name}[/dim]")
    
    # Parse fields if provided
    field_list = None
    if fields:
        field_list = [field.strip() for field in fields.split(",")]
        if debug:
            console.print(f"[dim]Will export specific fields: {', '.join(field_list)}[/dim]")
    
    env_path = Path(env_file)
    
    # Check if input file exists
    if not env_path.exists():
        console.print(f"[red]✗[/red] Input file '{env_file}' not found")
        sys.exit(1)
    
    try:
        from onepass_env.core import EnvExporter
        from onepass_env.validation import validate_fields, validate_input_file
        
        # Validate fields if provided
        if field_list:
            valid, error = validate_fields(field_list)
            if not valid:
                console.print(f"[red]✗[/red] Validation Error: {error}")
                sys.exit(1)
        
        # Validate input file
        valid, error = validate_input_file(env_file)
        if not valid:
            console.print(f"[red]✗[/red] Validation Error: {error}")
            sys.exit(1)
        
        if debug:
            console.print(f"[dim]Exporting from file: {env_file}[/dim]")
            console.print(f"[dim]Target vault: {vault}[/dim]")
            console.print(f"[dim]Target item: {name}[/dim]")
        
        exporter = EnvExporter(vault=vault, verbose=debug)
        
        # Check authentication
        if not exporter.op_client.is_authenticated():
            raise OnePassEnvError(
                "Not authenticated with 1Password. Please check your OP_SERVICE_ACCOUNT_TOKEN "
                "environment variable and ensure it has access to the specified vault."
            )
        
        # Export variables
        exported_vars = exporter.export_from_file(
            input_file=env_file,
            item_name=name,
            field_filter=field_list,
            overwrite=overwrite
        )
        
        # Show summary
        console.print(f"[green]✓[/green] Successfully exported {len(exported_vars)} variables to '{name}' in vault '{vault}'")
        
        # Show exported variables
        if debug or len(exported_vars) <= 10:
            table = Table(title="Exported Variables")
            table.add_column("Variable", style="cyan")
            table.add_column("Value", style="green")
            
            for key, value in exported_vars.items():
                # Mask the value for security
                masked_value = "*" * min(len(str(value)), 8) if not debug else str(value)
                table.add_row(key, masked_value)
            
            console.print(table)
        else:
            console.print(f"[dim]Use --debug to see all exported values[/dim]")
        
        console.print(f"\n[blue]💡[/blue] Variables are now securely stored in 1Password")
        console.print(f"   • Vault: [bold]{vault}[/bold]")
        console.print(f"   • Item: [bold]{name}[/bold]")
        
    except OnePassEnvError as e:
        console.print(f"[red]✗[/red] Error: {e}")
        sys.exit(1)
    except Exception as e:
        console.print(f"[red]✗[/red] Unexpected error: {e}")
        if debug:
            import traceback
            console.print(traceback.format_exc())
        sys.exit(1)


def main() -> None:
    """Entry point for the CLI."""
    try:
        cli()
    except KeyboardInterrupt:
        console.print("\n[yellow]Operation cancelled by user[/yellow]")
        sys.exit(1)
    except Exception as e:
        console.print(f"[red]Unexpected error: {e}[/red]")
        sys.exit(1)


if __name__ == "__main__":
    main()
