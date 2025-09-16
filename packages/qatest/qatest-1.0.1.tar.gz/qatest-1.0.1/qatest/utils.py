"""Utility functions for QATest."""

import contextlib
import os
from pathlib import Path
from typing import Any, Dict, Optional

import yaml
from dotenv import load_dotenv


def load_config(config_file: Optional[Path] = None) -> Dict[str, Any]:
    """
    Load configuration from file and environment variables.
    
    Priority order:
    1. Command-line arguments (handled by caller)
    2. Environment variables
    3. Config file
    4. Defaults
    
    Args:
        config_file: Optional path to config file
    
    Returns:
        Configuration dictionary
    """
    config = {
        "api_endpoint": None,  # Must be configured via config file
        "project_key": None,  # Must be configured via config file
        "batch_size": 50,
        "validate_first": True,
    }

    # Load from config file if exists
    if config_file is None:
        # Look for default config files
        for name in ["qatest-config.yml", "qatest-config.yaml"]:
            if Path(name).exists():
                config_file = Path(name)
                break

    if config_file and config_file.exists():
        try:
            with open(config_file) as f:
                file_config = yaml.safe_load(f)
                if file_config:
                    config.update(file_config)
        except Exception as e:
            print(f"Warning: Failed to load config file {config_file}: {e}")

    # Load from environment variables (only for batch_size and validate_first)
    load_dotenv()

    batch_size_env = os.getenv("QATEST_BATCH_SIZE")
    if batch_size_env:
        with contextlib.suppress(ValueError):
            config["batch_size"] = int(batch_size_env)

    if os.getenv("QATEST_VALIDATE_FIRST"):
        config["validate_first"] = os.getenv("QATEST_VALIDATE_FIRST").lower() in ("true", "1", "yes")

    return config


def get_version() -> str:
    """Get the version of the qatest package."""
    from . import __version__
    return __version__


def format_file_size(size_bytes: float) -> str:
    """
    Format file size in human-readable format.
    
    Args:
        size_bytes: Size in bytes
    
    Returns:
        Formatted string
    """
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"


def count_test_cases_in_directory(directory: Path) -> int:
    """
    Count the number of JSON files in a directory.
    
    Args:
        directory: Path to directory
    
    Returns:
        Number of JSON files
    """
    if not directory.exists() or not directory.is_dir():
        return 0

    return len(list(directory.rglob("*.json")))
