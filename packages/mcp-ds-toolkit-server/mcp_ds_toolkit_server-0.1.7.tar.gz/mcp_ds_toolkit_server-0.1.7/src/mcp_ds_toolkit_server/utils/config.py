"""Configuration management for the MCP MLOps server."""

import logging
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from mcp_ds_toolkit_server.exceptions import ConfigurationError
from mcp_ds_toolkit_server.utils.common import ensure_directory

logger = logging.getLogger(__name__)


@dataclass
class Settings:
    """Configuration settings for the MCP MLOps server."""

    # Application settings
    app_name: str = field(default="mcp-ds-toolkit-server")
    app_version: str = field(default="0.1.7")
    app_description: str = field(
        default="MCP DS Toolkit Server - A comprehensive DS toolkit with natural language interface"
    )

    # Server settings
    debug: bool = field(
        default_factory=lambda: os.getenv("DEBUG", "false").lower() == "true"
    )
    log_level: str = field(default_factory=lambda: os.getenv("LOG_LEVEL", "INFO"))

    # Data settings - using artifacts directory structure resolved from current directory
    data_dir: Path = field(
        default_factory=lambda: Path(os.getenv("DATA_DIR", "artifacts/data")).resolve()
    )
    models_dir: Path = field(
        default_factory=lambda: Path(os.getenv("MODELS_DIR", "artifacts/models")).resolve()
    )
    experiments_dir: Path = field(
        default_factory=lambda: Path(
            os.getenv("EXPERIMENTS_DIR", "artifacts/experiments")
        ).resolve()
    )
    workspace_path: Path = field(
        default_factory=lambda: Path(os.getenv("WORKSPACE_PATH", "artifacts/workspace")).resolve()
    )


    # AWS Settings for S3 storage
    aws_access_key_id: Optional[str] = field(
        default_factory=lambda: os.getenv("AWS_ACCESS_KEY_ID")
    )
    aws_secret_access_key: Optional[str] = field(
        default_factory=lambda: os.getenv("AWS_SECRET_ACCESS_KEY")
    )
    aws_default_region: str = field(
        default_factory=lambda: os.getenv("AWS_DEFAULT_REGION", "us-east-1")
    )


    # Resource limits
    max_dataset_size_mb: int = field(
        default_factory=lambda: int(os.getenv("MAX_DATASET_SIZE_MB", "1000"))
    )
    max_model_size_mb: int = field(
        default_factory=lambda: int(os.getenv("MAX_MODEL_SIZE_MB", "500"))
    )
    max_concurrent_jobs: int = field(
        default_factory=lambda: int(os.getenv("MAX_CONCURRENT_JOBS", "4"))
    )

    # Training settings
    default_test_size: float = field(
        default_factory=lambda: float(os.getenv("DEFAULT_TEST_SIZE", "0.2"))
    )
    default_random_state: int = field(
        default_factory=lambda: int(os.getenv("DEFAULT_RANDOM_STATE", "42"))
    )
    default_cv_folds: int = field(
        default_factory=lambda: int(os.getenv("DEFAULT_CV_FOLDS", "5"))
    )

    # Deployment settings
    deployment_host: str = field(
        default_factory=lambda: os.getenv("DEPLOYMENT_HOST", "127.0.0.1")
    )
    deployment_port: int = field(
        default_factory=lambda: int(os.getenv("DEPLOYMENT_PORT", "8000"))
    )

    def __post_init__(self):
        """Initialize and validate configuration."""
        # Convert string paths to Path objects if needed
        if isinstance(self.data_dir, str):
            self.data_dir = Path(self.data_dir)
        if isinstance(self.models_dir, str):
            self.models_dir = Path(self.models_dir)
        if isinstance(self.experiments_dir, str):
            self.experiments_dir = Path(self.experiments_dir)
        if isinstance(self.workspace_path, str):
            self.workspace_path = Path(self.workspace_path)

        self._validate_config()
        # Don't create directories during initialization
        # They will be created on-demand when needed

    def _validate_config(self) -> None:
        """Validate configuration values."""
        if self.max_dataset_size_mb <= 0:
            raise ConfigurationError(
                f"max_dataset_size_mb must be positive, got {self.max_dataset_size_mb}"
            )

        if not (0 < self.default_test_size < 1):
            raise ConfigurationError(
                f"default_test_size must be between 0 and 1, got {self.default_test_size}"
            )

        if self.deployment_port <= 0 or self.deployment_port > 65535:
            raise ConfigurationError(
                f"deployment_port must be between 1 and 65535, got {self.deployment_port}"
            )

    def ensure_directories(self) -> None:
        """Ensure all required directories exist, using fallback to temp on failure."""
        directories = [
            ("data_dir", self.data_dir),
            ("models_dir", self.models_dir),
            ("experiments_dir", self.experiments_dir),
            ("workspace_path", self.workspace_path),
        ]

        created_dirs = []
        for name, directory in directories:
            try:
                ensured_dir = ensure_directory(directory, fallback_to_temp=True)
                # Update the attribute if it was changed due to fallback
                if ensured_dir != directory:
                    setattr(self, name, ensured_dir)
                created_dirs.append(str(ensured_dir))
            except Exception as e:
                logger.warning(f"Failed to create directory {directory}: {e}")


        logger.debug(f"Ensured directories: {created_dirs}")

    def get_data_path(self, filename: str) -> Path:
        """Get path for a data file, ensuring directory exists."""
        data_dir = ensure_directory(self.data_dir, fallback_to_temp=True)
        return data_dir / filename

    def get_model_path(self, filename: str) -> Path:
        """Get path for a model file, ensuring directory exists."""
        models_dir = ensure_directory(self.models_dir, fallback_to_temp=True)
        return models_dir / filename

    def get_experiment_path(self, filename: str) -> Path:
        """Get path for an experiment file, ensuring directory exists."""
        experiments_dir = ensure_directory(self.experiments_dir, fallback_to_temp=True)
        return experiments_dir / filename

    def get_workspace_path(self, filename: str) -> Path:
        """Get path for a workspace file, ensuring directory exists."""
        workspace_dir = ensure_directory(self.workspace_path, fallback_to_temp=True)
        return workspace_dir / filename

