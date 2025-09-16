"""Command-line interface for QATest."""

import sys
from pathlib import Path
from typing import Optional

import click
from rich.console import Console

from . import __version__
from .uploader import upload_test_cases
from .utils import load_config
from .validator import validate_directory

console = Console()


@click.group(invoke_without_command=True)
@click.option(
    '--version',
    is_flag=True,
    help='Show the version and exit.'
)
@click.pass_context
def cli(ctx, version):
    """QATest - Test case management tool for uploading JSON test cases."""
    if version:
        click.echo(f"qatest version {__version__}")
        ctx.exit()

    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())

    # Initialize context for subcommands
    ctx.ensure_object(dict)


@cli.command()
@click.argument(
    'directory',
    type=click.Path(exists=True, file_okay=False, dir_okay=True, path_type=Path),
    required=True
)
@click.option(
    '--pattern',
    default='*.json',
    help='File pattern to match (default: *.json)'
)
def validate(directory: Path, pattern: str):
    """
    Validate test case files in a directory.
    
    DIRECTORY: Path to directory containing test case JSON files
    """
    console.print("\n[bold cyan]QATest Validator[/bold cyan]")
    console.print(f"Directory: [yellow]{directory}[/yellow]")

    # Validate the directory
    result = validate_directory(directory, pattern)
    result.print_summary()

    # Exit with error code if validation failed
    if not result.is_valid:
        console.print("\n[red]✗ Validation failed![/red]")
        sys.exit(1)
    else:
        console.print("\n[green]✓ All test cases are valid![/green]")
        sys.exit(0)


@cli.command()
@click.argument(
    'directory',
    type=click.Path(exists=True, file_okay=False, dir_okay=True, path_type=Path),
    required=True
)
@click.option(
    '--no-validate',
    is_flag=True,
    help='Skip validation before upload'
)
@click.option(
    '--batch-size',
    type=int,
    default=50,
    help='Number of test cases to upload in each batch (default: 50)'
)
@click.option(
    '--clear/--no-clear',
    default=True,
    help='Clear existing test cases before upload (default: clear)'
)
@click.option(
    '--config',
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
    help='Path to configuration file'
)
@click.option(
    '-v', '--verbose',
    is_flag=True,
    help='Show detailed error messages for failed uploads'
)
@click.pass_context
def upload(ctx, directory: Path, no_validate: bool, batch_size: int, clear: bool, config: Optional[Path], verbose: bool):
    """
    Upload test cases from a directory to QATest API.
    
    DIRECTORY: Path to directory containing test case JSON files
    """
    # Load configuration
    config_data = load_config(config)

    # Get required configuration
    api_endpoint = config_data.get('api_endpoint')
    project_key = config_data.get('project_key')
    validate_first = not no_validate
    
    # Check if clear_before_upload is in config, otherwise use CLI option
    clear_before_upload = clear
    if 'clear_before_upload' in config_data and ctx.get_parameter_source('clear') == click.core.ParameterSource.DEFAULT:
        # Config file overrides default, but CLI option overrides config
        clear_before_upload = config_data.get('clear_before_upload', True)

    if not api_endpoint:
        console.print("[red]Error: No API endpoint configured.[/red]")
        console.print("\nPlease configure an API endpoint in qatest-config.yml file")
        sys.exit(1)

    if not project_key:
        console.print("[red]Error: No project key configured.[/red]")
        console.print("\nPlease configure a project key in qatest-config.yml file")
        sys.exit(1)

    console.print("\n[bold cyan]QATest Uploader[/bold cyan]")
    console.print(f"Directory: [yellow]{directory}[/yellow]")
    if clear_before_upload:
        console.print("Clear before upload: [cyan]Yes[/cyan]")
    else:
        console.print("Clear before upload: [yellow]No[/yellow]")

    try:
        # Upload test cases
        result = upload_test_cases(
            directory=directory,
            api_endpoint=api_endpoint,
            project_key=project_key,
            validate_first=validate_first,
            batch_size=batch_size,
            clear_before_upload=clear_before_upload,
            verbose=verbose
        )

        # Print summary (this will show errors at the end)
        result.print_summary(verbose=verbose)

        # Exit with appropriate code
        if result.critical_error:
            # Critical error already displayed in summary
            sys.exit(1)
        elif result.uploaded:
            if not result.failed:
                console.print(f"\n[green]✓ Successfully uploaded {len(result.uploaded)} test cases![/green]")
                sys.exit(0)
            else:
                # Some failed but some succeeded
                sys.exit(1)
        else:
            console.print("\n[red]✗ No test cases were uploaded.[/red]")
            sys.exit(1)

    except ConnectionError as e:
        console.print("\n[bold red]✗ CRITICAL ERROR:[/bold red]")
        console.print(f"[red]Connection Error: {e}[/red]")
        sys.exit(1)
    except PermissionError as e:
        console.print("\n[bold red]✗ CRITICAL ERROR:[/bold red]")
        console.print(f"[red]Permission Error: {e}[/red]")
        sys.exit(1)
    except Exception as e:
        console.print("\n[bold red]✗ CRITICAL ERROR:[/bold red]")
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)


@cli.command()
@click.argument('project_key', required=True)
@click.option(
    '--force',
    is_flag=True,
    help='Overwrite existing configuration file'
)
def init(project_key: str, force: bool):
    """
    Initialize a new qatest-config.yml file with specified project key.
    
    PROJECT_KEY: Your project API key
    """
    import yaml
    
    config_file = Path("qatest-config.yml")
    
    # Check if file already exists
    if config_file.exists() and not force:
        console.print("[yellow]Configuration file already exists.[/yellow]")
        console.print("Use --force to overwrite the existing file.")
        sys.exit(1)
    
    # Create default configuration with provided values
    default_config = {
        "api_endpoint": "http://127.0.0.1:8000",
        "project_key": project_key,
        "batch_size": 50,
        "validate_first": True,
        "clear_before_upload": True
    }
    
    # Write configuration file
    try:
        with open(config_file, 'w') as f:
            yaml.dump(default_config, f, default_flow_style=False, sort_keys=False)
        
        console.print(f"[green]✓ Created configuration file: {config_file}[/green]")
        console.print("\n[bold]Default configuration:[/bold]")
        for key, value in default_config.items():
            console.print(f"  {key}: [cyan]{value}[/cyan]")
        console.print("\n[yellow]Please update the configuration with your actual API endpoint.[/yellow]")
        sys.exit(0)
    except Exception as e:
        console.print(f"[red]Error creating configuration file: {e}[/red]")
        sys.exit(1)


def main():
    """Main entry point for the CLI."""
    try:
        cli(obj={})
    except KeyboardInterrupt:
        console.print("\n[yellow]Interrupted by user[/yellow]")
        sys.exit(130)
    except Exception as e:
        console.print(f"\n[red]Unexpected error: {e}[/red]")
        sys.exit(1)


if __name__ == '__main__':
    main()
