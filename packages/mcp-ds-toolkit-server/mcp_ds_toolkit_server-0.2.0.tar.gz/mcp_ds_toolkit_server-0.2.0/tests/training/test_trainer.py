"""Tests for training trainer module."""

from pathlib import Path

import numpy as np
import pandas as pd
import pytest
from sklearn.datasets import make_classification
from sklearn.ensemble import RandomForestClassifier

from mcp_ds_toolkit_server.training.trainer import (
    ModelTrainer,
    TrainingConfig,
    TrainingResults,
)
from mcp_ds_toolkit_server.utils.config import Settings


class TestTrainingConfig:
    """Test TrainingConfig dataclass."""

    def test_training_config_creation(self):
        """Test TrainingConfig creation with default values."""
        config = TrainingConfig()

        # Test basic attributes exist
        assert hasattr(config, "random_state")
        assert hasattr(config, "test_size")
        assert hasattr(config, "cv_folds")


class TestTrainingResults:
    """Test TrainingResults dataclass."""

    def test_training_results_creation(self):
        """Test TrainingResults creation."""
        # Create a simple model for testing
        model = RandomForestClassifier(n_estimators=10, random_state=42)

        result = TrainingResults(
            model=model,
            model_type="classification",
            algorithm="random_forest",
            train_score=0.95,
            test_score=0.90,
            cv_scores=[0.88, 0.92, 0.90, 0.89, 0.91],
            feature_names=["feature1", "feature2"],
            training_time=30.5,
        )

        assert result.model == model
        assert result.model_type == "classification"
        assert result.algorithm == "random_forest"
        assert result.train_score == 0.95
        assert result.test_score == 0.90
        assert len(result.cv_scores) == 5
        assert len(result.feature_names) == 2
        assert result.training_time == 30.5


class TestModelTrainer:
    """Test ModelTrainer class."""

    @pytest.fixture
    def settings(self):
        """Create test settings."""
        return Settings()

    @pytest.fixture
    def trainer(self, settings):
        """Create ModelTrainer instance."""
        return ModelTrainer(settings)

    @pytest.fixture
    def classification_data(self):
        """Create classification dataset."""
        X, y = make_classification(
            n_samples=100, n_features=4, n_classes=2, random_state=42, n_redundant=0
        )
        feature_names = [f"feature_{i}" for i in range(X.shape[1])]
        df = pd.DataFrame(X, columns=feature_names)
        df["target"] = y
        return df, feature_names

    def test_trainer_initialization(self, trainer, settings):
        """Test ModelTrainer initialization."""
        assert trainer.settings == settings
        assert hasattr(trainer, "logger")

    def test_trainer_has_required_methods(self, trainer):
        """Test that trainer has required methods."""
        # Check that key methods exist
        assert hasattr(trainer, "train_model")
        assert callable(getattr(trainer, "train_model"))


class TestModelTrainerBasicFunctionality:
    """Test basic ModelTrainer functionality."""

    @pytest.fixture
    def trainer_setup(self):
        """Set up trainer with test data."""
        settings = Settings()
        trainer = ModelTrainer(settings)

        # Create simple test data
        X, y = make_classification(
            n_samples=50, n_features=3, n_classes=2, random_state=42, n_redundant=0
        )
        feature_names = [f"feature_{i}" for i in range(X.shape[1])]
        data = pd.DataFrame(X, columns=feature_names)
        data["target"] = y

        return {"trainer": trainer, "data": data, "feature_names": feature_names}

    def test_trainer_basic_workflow(self, trainer_setup):
        """Test basic trainer workflow."""
        setup = trainer_setup

        # This is a basic test to ensure the trainer can be instantiated
        # and has the expected structure
        assert setup["trainer"] is not None
        assert setup["data"] is not None
        assert len(setup["feature_names"]) == 3
        assert "target" in setup["data"].columns

        # Verify data structure
        assert setup["data"].shape[0] == 50  # 50 samples
        assert setup["data"].shape[1] == 4  # 3 features + 1 target
