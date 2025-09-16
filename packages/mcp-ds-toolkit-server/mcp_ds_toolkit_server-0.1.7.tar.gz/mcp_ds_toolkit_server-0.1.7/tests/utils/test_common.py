"""Tests for common utility functions."""

import os
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from mcp_ds_toolkit_server.utils.common import (
    DirectoryManager,
    ensure_directory,
    get_project_base_dir,
    is_writable,
    safe_file_write,
    validate_path,
)


class TestEnsureDirectory:
    """Test ensure_directory function."""

    def test_ensure_directory_creates_missing_directory(self, tmp_path):
        """Test that ensure_directory creates missing directories."""
        test_dir = tmp_path / "new_directory"
        assert not test_dir.exists()

        result = ensure_directory(test_dir)
        assert test_dir.exists()
        assert test_dir.is_dir()
        assert result == test_dir

    def test_ensure_directory_with_existing_directory(self, tmp_path):
        """Test that ensure_directory works with existing directories."""
        test_dir = tmp_path / "existing_directory"
        test_dir.mkdir()
        assert test_dir.exists()

        result = ensure_directory(test_dir)
        assert test_dir.exists()
        assert test_dir.is_dir()
        assert result == test_dir

    def test_ensure_directory_creates_nested_directories(self, tmp_path):
        """Test that ensure_directory creates nested directory structure."""
        nested_dir = tmp_path / "level1" / "level2" / "level3"
        assert not nested_dir.exists()

        result = ensure_directory(nested_dir)
        assert nested_dir.exists()
        assert nested_dir.is_dir()
        assert (tmp_path / "level1").exists()
        assert (tmp_path / "level1" / "level2").exists()

    def test_ensure_directory_with_string_path(self, tmp_path):
        """Test that ensure_directory works with string paths."""
        test_dir = str(tmp_path / "string_path_dir")
        assert not Path(test_dir).exists()

        result = ensure_directory(test_dir)
        assert Path(test_dir).exists()
        assert Path(test_dir).is_dir()
        assert result == Path(test_dir)

    def test_ensure_directory_fallback_to_temp(self, tmp_path):
        """Test fallback to temp directory when permission denied."""
        # Test with a path that is likely to cause permission issues
        # Use a system path that doesn't exist and shouldn't be writable
        test_dir = Path("/root/test_directory_that_should_not_exist")

        # This should fallback to temp directory
        result = ensure_directory(test_dir, fallback_to_temp=True)

        # Should return a temp directory path (check for common temp directory patterns)
        result_str = str(result).lower()
        temp_indicators = ["tmp", "temp", "/t/", "var/folders", "mcp-mlops-server"]
        assert any(indicator in result_str for indicator in temp_indicators)
        assert result.exists()


class TestIsWritable:
    """Test is_writable function."""

    def test_is_writable_with_writable_directory(self, tmp_path):
        """Test is_writable returns True for writable directory."""
        assert is_writable(tmp_path)

    def test_is_writable_with_string_path(self, tmp_path):
        """Test is_writable works with string paths."""
        assert is_writable(str(tmp_path))

    def test_is_writable_with_nonexistent_path(self, tmp_path):
        """Test is_writable creates and tests nonexistent path."""
        nonexistent = tmp_path / "new_dir"
        result = is_writable(nonexistent)
        # Should create the directory and return True
        assert result is True
        assert nonexistent.exists()


class TestValidatePath:
    """Test validate_path function."""

    def test_validate_path_with_valid_path(self, tmp_path):
        """Test validate_path with valid path."""
        test_file = tmp_path / "valid_file.txt"
        test_file.write_text("content")

        # Should not raise an exception
        result = validate_path(test_file)
        assert result.exists()

        result = validate_path(str(test_file))
        assert result.exists()

    def test_validate_path_with_directory(self, tmp_path):
        """Test validate_path with directory."""
        result = validate_path(tmp_path)
        assert result.exists()
        assert result.is_dir()

    def test_validate_path_with_nonexistent_path_not_required(self, tmp_path):
        """Test validate_path with nonexistent path when not required to exist."""
        nonexistent = tmp_path / "does_not_exist.txt"

        result = validate_path(nonexistent, must_exist=False)
        assert isinstance(result, Path)

    def test_validate_path_with_nonexistent_path_required(self, tmp_path):
        """Test validate_path with nonexistent path when required to exist."""
        nonexistent = tmp_path / "does_not_exist.txt"

        with pytest.raises(FileNotFoundError):
            validate_path(nonexistent, must_exist=True)


class TestSafeFileWrite:
    """Test safe_file_write function."""

    def test_safe_file_write_new_file(self, tmp_path):
        """Test safe_file_write with new file."""
        test_file = tmp_path / "new_file.txt"
        content = "Hello, World!"

        result = safe_file_write(content, test_file)

        assert test_file.exists()
        assert test_file.read_text() == content
        assert result == test_file

    def test_safe_file_write_existing_file_with_backup(self, tmp_path):
        """Test safe_file_write with existing file and backup."""
        test_file = tmp_path / "existing_file.txt"
        original_content = "Original content"
        new_content = "New content"

        # Create original file
        test_file.write_text(original_content)

        result = safe_file_write(new_content, test_file, backup=True)

        assert test_file.exists()
        assert test_file.read_text() == new_content

        # Check backup was created
        backup_file = test_file.with_suffix(test_file.suffix + ".backup")
        assert backup_file.exists()
        assert backup_file.read_text() == original_content

    def test_safe_file_write_existing_file_without_backup(self, tmp_path):
        """Test safe_file_write with existing file without backup."""
        test_file = tmp_path / "existing_file.txt"
        original_content = "Original content"
        new_content = "New content"

        # Create original file
        test_file.write_text(original_content)

        result = safe_file_write(new_content, test_file, backup=False)

        assert test_file.exists()
        assert test_file.read_text() == new_content

        # Check no backup was created
        backup_file = test_file.with_suffix(test_file.suffix + ".backup")
        assert not backup_file.exists()


class TestDirectoryManager:
    """Test DirectoryManager class."""

    def test_directory_manager_default_initialization(self):
        """Test DirectoryManager with default initialization."""
        manager = DirectoryManager()
        assert manager.base_dir is not None
        assert isinstance(manager.base_dir, Path)

    def test_directory_manager_custom_base_dir(self, tmp_path):
        """Test DirectoryManager with custom base directory."""
        manager = DirectoryManager(base_dir=tmp_path)
        assert manager.base_dir == tmp_path

    def test_get_data_dir(self, tmp_path):
        """Test get_data_dir method."""
        manager = DirectoryManager(base_dir=tmp_path)

        data_dir = manager.get_data_dir()
        assert data_dir.exists()
        assert data_dir.name == "data"
        assert data_dir.parent == tmp_path

    def test_get_data_dir_with_subdir(self, tmp_path):
        """Test get_data_dir with subdirectory."""
        manager = DirectoryManager(base_dir=tmp_path)

        subdir_path = manager.get_data_dir("training")
        assert subdir_path.exists()
        assert subdir_path.name == "training"
        assert subdir_path.parent.name == "data"

    def test_get_models_dir(self, tmp_path):
        """Test get_models_dir method."""
        manager = DirectoryManager(base_dir=tmp_path)

        models_dir = manager.get_models_dir()
        assert models_dir.exists()
        assert models_dir.name == "models"
        assert models_dir.parent == tmp_path

    def test_get_experiments_dir(self, tmp_path):
        """Test get_experiments_dir method."""
        manager = DirectoryManager(base_dir=tmp_path)

        experiments_dir = manager.get_experiments_dir()
        assert experiments_dir.exists()
        assert experiments_dir.name == "experiments"
        assert experiments_dir.parent == tmp_path

    def test_get_workspace_dir(self, tmp_path):
        """Test get_workspace_dir method."""
        manager = DirectoryManager(base_dir=tmp_path)

        workspace_dir = manager.get_workspace_dir()
        assert workspace_dir.exists()
        assert workspace_dir.name == "workspace"
        assert workspace_dir.parent == tmp_path



class TestGetProjectBaseDir:
    """Test get_project_base_dir function."""

    def test_get_project_base_dir(self):
        """Test get_project_base_dir returns valid path."""
        base_dir = get_project_base_dir()
        assert isinstance(base_dir, Path)
        assert base_dir.exists()

    def test_get_project_base_dir_fallback_to_temp(self):
        """Test get_project_base_dir fallback to temp directory."""
        with patch("mcp_ds_toolkit_server.utils.common.is_writable", return_value=False):
            base_dir = get_project_base_dir()
            assert isinstance(base_dir, Path)
            assert base_dir.exists()
            # Should contain temp directory indicators
            base_dir_str = str(base_dir).lower()
            temp_indicators = ["tmp", "temp", "/t/", "var/folders", "mcp-mlops-server"]
            assert any(indicator in base_dir_str for indicator in temp_indicators)


class TestIntegrationScenarios:
    """Integration tests for common utility functions."""

    def test_complete_directory_setup(self, tmp_path):
        """Test complete directory setup workflow."""
        # Create directory manager
        manager = DirectoryManager(base_dir=tmp_path)

        # Create all standard directories
        data_dir = manager.get_data_dir()
        models_dir = manager.get_models_dir()
        experiments_dir = manager.get_experiments_dir()
        workspace_dir = manager.get_workspace_dir()

        # Verify all directories exist
        assert data_dir.exists()
        assert models_dir.exists()
        assert experiments_dir.exists()
        assert workspace_dir.exists()

        # Test file operations in each directory
        test_content = "test content"

        test_files = [
            data_dir / "test_data.csv",
            models_dir / "test_model.pkl",
            experiments_dir / "test_experiment.json",
            workspace_dir / "test_workspace.txt",
        ]

        for test_file in test_files:
            result = safe_file_write(test_content, test_file)
            assert result.exists()
            assert result.read_text() == test_content

    def test_path_validation_workflow(self, tmp_path):
        """Test complete path validation workflow."""
        # Create test structure
        data_dir = tmp_path / "data"
        ensure_directory(data_dir)

        test_file = data_dir / "test.csv"
        safe_file_write("csv,data\n1,2", test_file)

        # Validate paths
        validated_dir = validate_path(data_dir, must_exist=True)
        validated_file = validate_path(test_file, must_exist=True)

        assert validated_dir.exists()
        assert validated_file.exists()
        assert is_writable(validated_dir)

        # Test with new file in validated directory
        new_file = validated_dir / "new_file.txt"
        result = safe_file_write("new content", new_file)
        assert result.exists()
