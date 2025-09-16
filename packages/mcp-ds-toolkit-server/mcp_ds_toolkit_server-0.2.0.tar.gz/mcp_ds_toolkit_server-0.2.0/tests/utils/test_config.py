"""Tests for the configuration module."""

import os
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from mcp_ds_toolkit_server.utils.config import Settings


class TestSettings:
    """Test cases for the Settings class."""

    def test_default_settings(self):
        """Test that default settings are correct."""
        settings = Settings()

        assert settings.app_name == "mcp-mlops-server"
        assert settings.app_version == "0.1.0"
        assert settings.debug is False
        assert settings.log_level == "INFO"
        assert settings.default_random_state == 42
        assert settings.default_test_size == 0.2
        assert settings.default_cv_folds == 5
        assert settings.deployment_host == "127.0.0.1"
        assert settings.deployment_port == 8000

    def test_environment_variable_override(self):
        """Test that environment variables override defaults."""
        env_vars = {
            "DEBUG": "true",
            "LOG_LEVEL": "DEBUG",
            "DEFAULT_RANDOM_STATE": "123",
            "DEFAULT_TEST_SIZE": "0.3",
            "DEFAULT_CV_FOLDS": "10",
            "DEPLOYMENT_PORT": "9000",
            "MAX_DATASET_SIZE_MB": "2000",
        }

        with patch.dict(os.environ, env_vars):
            settings = Settings()

            assert settings.debug is True
            assert settings.log_level == "DEBUG"
            assert settings.default_random_state == 123
            assert settings.default_test_size == 0.3
            assert settings.default_cv_folds == 10
            assert settings.deployment_port == 9000
            assert settings.max_dataset_size_mb == 2000


# DVC functionality removed - using local storage only

    def test_directory_creation(self):
        """Test that directories are created on initialization."""
        with tempfile.TemporaryDirectory() as temp_dir:
            env_vars = {
                "MLOPS_DIR_MODE": "custom",
                "MLOPS_BASE_PATH": temp_dir,
            }

            with patch.dict(os.environ, env_vars):
                settings = Settings()

                assert settings.data_dir.exists()
                assert settings.models_dir.exists()
                assert settings.experiments_dir.exists()

    def test_path_helpers(self):
        """Test path helper methods."""
        settings = Settings()

        data_path = settings.get_data_path("test.csv")
        model_path = settings.get_model_path("model.pkl")
        experiment_path = settings.get_experiment_path("experiment.json")

        assert data_path.name == "test.csv"
        assert model_path.name == "model.pkl"
        assert experiment_path.name == "experiment.json"
        assert data_path.parent == settings.data_dir
        assert model_path.parent == settings.models_dir
        assert experiment_path.parent == settings.experiments_dir

    def test_resource_limits(self):
        """Test resource limit settings."""
        settings = Settings()

        assert settings.max_dataset_size_mb == 1000
        assert settings.max_model_size_mb == 500
        assert settings.max_concurrent_jobs == 4
