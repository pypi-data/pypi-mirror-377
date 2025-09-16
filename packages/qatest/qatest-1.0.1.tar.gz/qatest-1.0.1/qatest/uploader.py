"""Upload functionality for QATest test cases."""

from pathlib import Path
from typing import List, Optional, Tuple

from rich.console import Console
from rich.progress import BarColumn, Progress, SpinnerColumn, TaskProgressColumn, TextColumn

from .client import QATestClient
from .models import TestCase
from .validator import validate_directory

console = Console()


class UploadResult:
    """Container for upload results."""

    def __init__(self):
        self.uploaded: List[Tuple[Path, TestCase]] = []
        self.failed: List[Tuple[Path, str]] = []
        self.skipped: List[Tuple[Path, str]] = []
        self.critical_error: Optional[str] = None

    @property
    def total_processed(self) -> int:
        return len(self.uploaded) + len(self.failed) + len(self.skipped)

    @property
    def success_rate(self) -> float:
        if self.total_processed == 0:
            return 0.0
        return len(self.uploaded) / self.total_processed * 100

    def print_summary(self, verbose: bool = False):
        """Print a summary of upload results."""
        console.print("\n[bold]Upload Summary:[/bold]")
        console.print(f"  ✓ Uploaded: [green]{len(self.uploaded)}[/green]")
        if self.failed:
            console.print(f"  ✗ Failed: [red]{len(self.failed)}[/red]")
        if self.skipped:
            console.print(f"  ⊘ Skipped: [yellow]{len(self.skipped)}[/yellow]")

        if self.total_processed > 0:
            console.print(f"  Success Rate: [cyan]{self.success_rate:.1f}%[/cyan]")
        
        # Show detailed errors if verbose flag is set
        if verbose and self.failed:
            console.print("\n[bold red]Failed uploads:[/bold red]")
            for file_path, error in self.failed:
                console.print(f"  [yellow]{file_path}[/yellow]")
                console.print(f"    [red]Error: {error}[/red]")
        
        # Show critical error prominently at the end
        if self.critical_error:
            console.print("\n[bold red]✗ CRITICAL ERROR:[/bold red]")
            console.print(f"[red]{self.critical_error}[/red]")


def upload_test_cases(
    directory: Path,
    api_endpoint: str,
    project_key: str,
    validate_first: bool = True,
    batch_size: int = 50,
    clear_before_upload: bool = True,
    verbose: bool = False
) -> UploadResult:
    """
    Upload test cases from a directory to the QATest API.
    
    Args:
        directory: Path to the directory containing test cases
        api_endpoint: API endpoint URL from configuration
        project_key: Project API key from configuration
        validate_first: Whether to validate test cases before uploading
        batch_size: Number of test cases to upload in each batch
        clear_before_upload: Whether to clear existing test cases before uploading
        verbose: Whether to show detailed error messages for failed uploads
    
    Returns:
        UploadResult object with upload results
    """
    result = UploadResult()

    # Validate test cases first
    if validate_first:
        validation_result = validate_directory(directory)
        validation_result.print_summary()

        if not validation_result.valid_files:
            console.print("\n[red]No valid test cases to upload.[/red]")
            return result

        if not validation_result.is_valid:
            console.print("\n[yellow]Warning: Some test cases are invalid and will be skipped.[/yellow]")
            # Add invalid files to skipped
            for file_path, error in validation_result.invalid_files:
                result.skipped.append((file_path, f"Validation error: {error}"))

        test_cases_to_upload = validation_result.valid_files
    else:
        # If not validating, try to load all JSON files
        console.print("[cyan]Loading test cases...[/cyan]")
        test_cases_to_upload = []
        json_files = list(directory.rglob("*.json"))

        for file_path in json_files:
            try:
                import json
                with open(file_path) as f:
                    data = json.load(f)
                
                # Calculate directory path relative to the base directory
                relative_path = file_path.relative_to(directory)
                directory_path = str(relative_path.parent)
                if directory_path == ".":
                    # Use "/" for files at root level
                    directory_path = "/"
                
                # Add directory_path to the data
                data['directory_path'] = directory_path
                
                test_case = TestCase(**data)
                test_cases_to_upload.append((file_path, test_case))
            except Exception as e:
                result.skipped.append((file_path, str(e)))

    if not test_cases_to_upload:
        console.print("\n[yellow]No test cases to upload.[/yellow]")
        return result

    # Initialize API client
    client = QATestClient(api_endpoint, project_key)

    # Check API health
    console.print(f"\n[cyan]Connecting to API: {client.api_endpoint}[/cyan]")
    if not client.health_check():
        console.print("[yellow]Warning: API health check failed. Attempting upload anyway...[/yellow]")
    
    # Clear existing test cases if requested
    if clear_before_upload:
        console.print("\n[cyan]Clearing existing test cases...[/cyan]")
        try:
            client.clear_test_cases()
            console.print("[green]✓ Existing test cases cleared[/green]")
        except Exception as e:
            console.print(f"[red]✗ Failed to clear existing test cases: {e}[/red]")
            result.critical_error = f"Failed to clear existing test cases: {e}"
            return result

    # Upload in batches
    total_cases = len(test_cases_to_upload)
    console.print(f"\n[bold]Uploading {total_cases} test cases...[/bold]")

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        console=console
    ) as progress:
        upload_task = progress.add_task(
            "[cyan]Uploading test cases...",
            total=total_cases
        )

        # Process in batches
        for i in range(0, total_cases, batch_size):
            batch = test_cases_to_upload[i:i + batch_size]
            batch_test_cases = [tc for _, tc in batch]

            try:
                # Upload batch
                client.bulk_upload(batch_test_cases)

                # Mark as uploaded
                for file_path, test_case in batch:
                    result.uploaded.append((file_path, test_case))

                progress.update(upload_task, advance=len(batch))

            except Exception as e:
                # If batch fails and verbose mode is on, try uploading individually to get specific errors
                if verbose and not isinstance(e, (ConnectionError, PermissionError)):
                    for file_path, test_case in batch:
                        try:
                            client.upload_single(test_case)
                            result.uploaded.append((file_path, test_case))
                        except Exception as individual_error:
                            result.failed.append((file_path, str(individual_error)))
                        progress.update(upload_task, advance=1)
                else:
                    # Mark entire batch as failed with the same error
                    for file_path, _ in batch:
                        result.failed.append((file_path, str(e)))
                    progress.update(upload_task, advance=len(batch))

                # Stop on critical errors
                if isinstance(e, (ConnectionError, PermissionError)):
                    result.critical_error = str(e)
                    # Mark remaining as skipped
                    for j in range(i + batch_size, total_cases):
                        file_path, _ = test_cases_to_upload[j]
                        result.skipped.append((file_path, "Upload cancelled due to critical error"))
                    break

    return result


def upload_single_file(
    file_path: Path,
    api_endpoint: str,
    project_key: str
) -> Tuple[bool, Optional[str]]:
    """
    Upload a single test case file.
    
    Args:
        file_path: Path to the test case file
        api_endpoint: API endpoint URL from configuration
        project_key: Project API key from configuration
    
    Returns:
        Tuple of (success, error_message)
    """
    try:
        # Load and validate the test case
        import json
        with open(file_path) as f:
            data = json.load(f)

        # For single file upload, use the parent directory name as directory_path
        directory_path = str(file_path.parent.name) if file_path.parent.name != file_path.parent.anchor else ""
        data['directory_path'] = directory_path

        test_case = TestCase(**data)

        # Upload
        client = QATestClient(api_endpoint, project_key)
        client.upload_single(test_case)

        return True, None

    except Exception as e:
        return False, str(e)
