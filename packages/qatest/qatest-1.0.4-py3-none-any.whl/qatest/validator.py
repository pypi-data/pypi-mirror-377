"""Validation utilities for QATest test cases."""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from pydantic import ValidationError
from rich.console import Console
from rich.table import Table

from .models import TestCase

console = Console()


class ValidationResult:
    """Container for validation results."""

    def __init__(self):
        self.valid_files: List[Tuple[Path, TestCase]] = []
        self.invalid_files: List[Tuple[Path, str]] = []
        self.skipped_files: List[Tuple[Path, str]] = []

    @property
    def total_files(self) -> int:
        return len(self.valid_files) + len(self.invalid_files) + len(self.skipped_files)

    @property
    def is_valid(self) -> bool:
        return len(self.invalid_files) == 0

    def print_summary(self):
        """Print a summary of validation results."""
        if self.total_files == 0:
            console.print("[yellow]No test case files found.[/yellow]")
            return

        # Summary
        console.print("\n[bold]Validation Summary:[/bold]")
        console.print(f"  ✓ Valid: [green]{len(self.valid_files)}[/green]")
        if self.invalid_files:
            console.print(f"  ✗ Invalid: [red]{len(self.invalid_files)}[/red]")
        if self.skipped_files:
            console.print(f"  ⊘ Skipped: [yellow]{len(self.skipped_files)}[/yellow]")

        # Details of invalid files
        if self.invalid_files:
            console.print("\n[bold red]Invalid Files:[/bold red]")
            table = Table(show_header=True, header_style="bold red")
            table.add_column("File", style="cyan")
            table.add_column("Error", style="red")

            for file_path, error in self.invalid_files:
                relative_path = file_path.name
                if len(str(file_path)) > 50:
                    relative_path = f".../{'/'.join(file_path.parts[-2:])}"
                else:
                    relative_path = str(file_path)
                table.add_row(relative_path, error)

            console.print(table)

        # Details of skipped files
        if self.skipped_files:
            console.print("\n[bold yellow]Skipped Files:[/bold yellow]")
            for file_path, reason in self.skipped_files:
                relative_path = file_path.name
                console.print(f"  • {relative_path}: {reason}")


def validate_test_case(file_path: Path, base_directory: Optional[Path] = None) -> Tuple[bool, Optional[TestCase], Optional[str]]:
    """
    Validate a single test case file.
    
    Args:
        file_path: Path to the JSON file
        base_directory: Base directory for calculating relative paths
    
    Returns:
        Tuple of (is_valid, test_case_object, error_message)
    """
    try:
        # Read the file
        with open(file_path, encoding='utf-8') as f:
            content = f.read()

        # Parse JSON
        try:
            data = json.loads(content)
        except json.JSONDecodeError as e:
            return False, None, f"Invalid JSON syntax at line {e.lineno}: {e.msg}"

        # Calculate directory path if base directory is provided
        if base_directory:
            relative_path = file_path.relative_to(base_directory)
            directory_path = str(relative_path.parent)
            if directory_path == ".":
                # Use "/" for files at root level
                directory_path = "/"
        else:
            # Use parent directory name if no base directory
            directory_path = str(file_path.parent.name) if file_path.parent.name != file_path.parent.anchor else "/"
        
        # Add directory_path to data
        data['directory_path'] = directory_path

        # Validate against model
        test_case = TestCase(**data)
        return True, test_case, None

    except ValidationError as e:
        # Format validation errors
        errors = []
        for error in e.errors():
            field_path = " -> ".join(str(loc) for loc in error['loc'])
            errors.append(f"{field_path}: {error['msg']}")
        return False, None, "; ".join(errors)

    except FileNotFoundError:
        return False, None, "File not found"

    except Exception as e:
        return False, None, f"Unexpected error: {str(e)}"


def validate_directory(directory: Path, pattern: str = "*.json") -> ValidationResult:
    """
    Validate all test case files in a directory.
    
    Args:
        directory: Path to the directory containing test cases
        pattern: File pattern to match (default: "*.json")
    
    Returns:
        ValidationResult object with validation results
    """
    result = ValidationResult()

    if not directory.exists():
        console.print(f"[red]Directory not found: {directory}[/red]")
        return result

    if not directory.is_dir():
        console.print(f"[red]Path is not a directory: {directory}[/red]")
        return result

    # Find all JSON files recursively
    json_files = list(directory.rglob(pattern))

    if not json_files:
        console.print(f"[yellow]No JSON files found in {directory}[/yellow]")
        return result

    console.print(f"\n[bold]Validating {len(json_files)} test case files...[/bold]")

    with console.status("[cyan]Validating test cases...[/cyan]") as status:
        for i, file_path in enumerate(json_files, 1):
            status.update(f"[cyan]Validating [{i}/{len(json_files)}]: {file_path.name}[/cyan]")

            # Skip non-test files (you can customize this logic)
            if file_path.stem.startswith('_') or file_path.stem.startswith('.'):
                result.skipped_files.append((file_path, "Hidden or system file"))
                continue

            # Validate the file with base directory for path calculation
            is_valid, test_case, error = validate_test_case(file_path, directory)

            if is_valid and test_case:
                result.valid_files.append((file_path, test_case))
            else:
                result.invalid_files.append((file_path, error or "Unknown error"))

    return result


def validate_json_structure(data: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
    """
    Validate the basic structure of a test case JSON without Pydantic.
    Useful for quick checks.
    
    Args:
        data: Dictionary representing the test case
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    # Check required fields
    if 'id' not in data:
        return False, "Missing required field: 'id'"

    if 'title' not in data:
        return False, "Missing required field: 'title'"

    if 'steps' not in data:
        return False, "Missing required field: 'steps'"

    # Check types
    if not isinstance(data['id'], int):
        return False, "'id' must be an integer"

    if not isinstance(data['title'], str):
        return False, "'title' must be a string"

    if not isinstance(data['steps'], list):
        return False, "'steps' must be a list"

    # Check steps - empty steps are now allowed

    for i, step in enumerate(data['steps']):
        if not isinstance(step, dict):
            return False, f"Step {i+1} must be an object"

        if 'action' not in step:
            return False, f"Step {i+1} missing required field: 'action'"

        if 'expected_result' not in step:
            return False, f"Step {i+1} missing required field: 'expected_result'"

        if not isinstance(step['action'], str):
            return False, f"Step {i+1}: 'action' must be a string"

        if not isinstance(step['expected_result'], str):
            return False, f"Step {i+1}: 'expected_result' must be a string"

    return True, None
