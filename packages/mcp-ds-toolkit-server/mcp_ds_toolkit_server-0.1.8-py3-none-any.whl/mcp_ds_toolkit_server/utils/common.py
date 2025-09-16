"""
Common utilities and shared functionality for the MCP MLOps server.

This module provides reusable utilities for directory management, error handling,
and configuration validation used across the codebase.
"""

import logging
import os
import tempfile
from pathlib import Path
from typing import Optional, Union

logger = logging.getLogger(__name__)


def ensure_directory(
    path: Union[str, Path], create_parents: bool = True, fallback_to_temp: bool = True
) -> Path:
    """
    Ensure a directory exists with consistent error handling.

    Args:
        path: Directory path to ensure
        create_parents: Whether to create parent directories
        fallback_to_temp: Whether to fallback to temp directory on failure

    Returns:
        Path object pointing to the ensured directory

    Raises:
        OSError: If directory creation fails and fallback is disabled
    """
    path = Path(path)

    try:
        path.mkdir(parents=create_parents, exist_ok=True)

        # Verify writability
        test_file = path / ".test_write"
        test_file.touch()
        test_file.unlink()

        return path

    except (OSError, PermissionError) as e:
        if fallback_to_temp:
            temp_base = Path(tempfile.gettempdir()) / "mcp-mlops-server"
            temp_base.mkdir(parents=True, exist_ok=True)

            # Create relative path structure in temp
            relative_path = path.name if path.is_absolute() else path
            temp_path = temp_base / relative_path
            temp_path.mkdir(parents=True, exist_ok=True)

            logger.warning(
                f"Cannot create directory {path}: {e}. "
                f"Using temporary directory: {temp_path}"
            )
            return temp_path
        else:
            raise OSError(f"Cannot create directory {path}: {e}")


def is_writable(path: Union[str, Path]) -> bool:
    """
    Check if a directory is writable.

    Args:
        path: Directory path to check

    Returns:
        True if directory is writable, False otherwise
    """
    try:
        path = Path(path)
        path.mkdir(parents=True, exist_ok=True)
        test_file = path / ".test_write"
        test_file.touch()
        test_file.unlink()
        return True
    except (OSError, PermissionError):
        return False


def get_project_base_dir() -> Path:
    """
    Get the project base directory, handling read-only environments.

    Returns:
        Path to use as base directory
    """
    try:
        project_root = Path(__file__).parent.parent.parent
        if is_writable(project_root):
            return project_root
        else:
            temp_base = Path(tempfile.gettempdir()) / "mcp-mlops-server"
            return ensure_directory(temp_base)
    except Exception:
        temp_base = Path(tempfile.gettempdir()) / "mcp-mlops-server"
        return ensure_directory(temp_base)


class DirectoryManager:
    """Manages directory creation and validation for the project."""

    def __init__(self, base_dir: Optional[Path] = None):
        self.base_dir = base_dir or get_project_base_dir()

    def get_data_dir(self, subdir: Optional[str] = None) -> Path:
        """Get data directory path."""
        path = self.base_dir / "data"
        if subdir:
            path = path / subdir
        return ensure_directory(path)

    def get_models_dir(self, subdir: Optional[str] = None) -> Path:
        """Get models directory path."""
        path = self.base_dir / "models"
        if subdir:
            path = path / subdir
        return ensure_directory(path)

    def get_experiments_dir(self, subdir: Optional[str] = None) -> Path:
        """Get experiments directory path."""
        path = self.base_dir / "experiments"
        if subdir:
            path = path / subdir
        return ensure_directory(path)

    def get_workspace_dir(self, subdir: Optional[str] = None) -> Path:
        """Get workspace directory path."""
        path = self.base_dir / "workspace"
        if subdir:
            path = path / subdir
        return ensure_directory(path)



def validate_path(path: Union[str, Path], must_exist: bool = False) -> Path:
    """
    Validate and normalize a path.

    Args:
        path: Path to validate
        must_exist: Whether the path must exist

    Returns:
        Normalized Path object

    Raises:
        FileNotFoundError: If path must exist and doesn't
        ValueError: If path is invalid
    """
    try:
        path = Path(path).resolve()
        if must_exist and not path.exists():
            raise FileNotFoundError(f"Path does not exist: {path}")
        return path
    except FileNotFoundError:
        # Re-raise FileNotFoundError as-is
        raise
    except Exception as e:
        raise ValueError(f"Invalid path: {e}")


def safe_file_write(
    content: str, filepath: Union[str, Path], mode: str = "w", backup: bool = True
) -> Path:
    """
    Safely write content to a file with optional backup.

    Args:
        content: Content to write
        filepath: Target file path
        mode: File mode for writing
        backup: Whether to create a backup if file exists

    Returns:
        Path to the written file
    """
    filepath = Path(filepath)
    ensure_directory(filepath.parent)

    if backup and filepath.exists():
        backup_path = filepath.with_suffix(filepath.suffix + ".backup")
        filepath.rename(backup_path)

    filepath.write_text(content, encoding="utf-8")
    return filepath
