"""Tests for training evaluator module."""

import numpy as np
import pandas as pd
import pytest
from sklearn.datasets import make_classification
from sklearn.ensemble import RandomForestClassifier

from mcp_ds_toolkit_server.training.evaluator import (
    ComparisonResults,
    EvaluationConfig,
    ModelEvaluation,
    ModelEvaluator,
)
from mcp_ds_toolkit_server.utils.config import Settings


class TestEvaluationConfig:
    """Test EvaluationConfig dataclass."""

    def test_evaluation_config_creation(self):
        """Test EvaluationConfig creation with default values."""
        config = EvaluationConfig()

        # Test basic attributes exist
        assert hasattr(config, "cv_folds")
        assert hasattr(config, "scoring_metrics")
        assert hasattr(config, "enable_statistical_tests")


class TestModelEvaluation:
    """Test ModelEvaluation dataclass."""

    def test_model_evaluation_creation(self):
        """Test ModelEvaluation creation."""
        evaluation = ModelEvaluation(
            model_name="test_model",
            model_type="classification",
            cv_scores={"accuracy": [0.94, 0.95, 0.96, 0.93, 0.94]},
            cv_means={"accuracy": 0.944},
            cv_stds={"accuracy": 0.011},
            test_scores={"accuracy": 0.95},
            training_time=30.5,
        )

        assert evaluation.model_name == "test_model"
        assert evaluation.model_type == "classification"
        assert evaluation.cv_means["accuracy"] == 0.944
        assert evaluation.test_scores["accuracy"] == 0.95
        assert evaluation.training_time == 30.5
        assert len(evaluation.cv_scores["accuracy"]) == 5


class TestComparisonResults:
    """Test ComparisonResults dataclass."""

    def test_comparison_results_creation(self):
        """Test ComparisonResults creation."""
        eval1 = ModelEvaluation(model_name="model1", model_type="classification")
        eval2 = ModelEvaluation(model_name="model2", model_type="classification")

        results = ComparisonResults(
            evaluations=[eval1, eval2],
            rankings={"accuracy": ["model1", "model2"]},
            best_models={"accuracy": "model1"},
        )

        assert len(results.evaluations) == 2
        assert results.evaluations[0].model_name == "model1"
        assert results.evaluations[1].model_name == "model2"
        assert results.rankings["accuracy"] == ["model1", "model2"]
        assert results.best_models["accuracy"] == "model1"


class TestModelEvaluator:
    """Test ModelEvaluator class."""

    @pytest.fixture
    def settings(self):
        """Create test settings."""
        return Settings()

    @pytest.fixture
    def evaluator(self, settings):
        """Create ModelEvaluator instance."""
        return ModelEvaluator(settings)

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

    @pytest.fixture
    def trained_model(self, classification_data):
        """Create a trained classification model."""
        data, feature_names = classification_data
        X = data[feature_names]
        y = data["target"]

        model = RandomForestClassifier(n_estimators=10, random_state=42)
        model.fit(X, y)
        return model

    def test_evaluator_initialization(self, evaluator, settings):
        """Test ModelEvaluator initialization."""
        assert evaluator.settings == settings
        assert hasattr(evaluator, "logger")

    def test_evaluator_has_required_methods(self, evaluator):
        """Test that evaluator has required methods."""
        # Check that key methods exist
        assert hasattr(evaluator, "evaluate_model")
        assert callable(getattr(evaluator, "evaluate_model"))


class TestModelEvaluatorBasicFunctionality:
    """Test basic ModelEvaluator functionality."""

    @pytest.fixture
    def evaluator_setup(self):
        """Set up evaluator with test data."""
        settings = Settings()
        evaluator = ModelEvaluator(settings)

        # Create simple test data
        X, y = make_classification(
            n_samples=50, n_features=3, n_classes=2, random_state=42, n_redundant=0
        )
        feature_names = [f"feature_{i}" for i in range(X.shape[1])]
        data = pd.DataFrame(X, columns=feature_names)
        data["target"] = y

        # Train a simple model
        model = RandomForestClassifier(n_estimators=10, random_state=42)
        model.fit(data[feature_names], data["target"])

        return {
            "evaluator": evaluator,
            "model": model,
            "data": data,
            "feature_names": feature_names,
        }

    def test_evaluator_basic_workflow(self, evaluator_setup):
        """Test basic evaluator workflow."""
        setup = evaluator_setup

        # This is a basic test to ensure the evaluator can be instantiated
        # and has the expected structure
        assert setup["evaluator"] is not None
        assert setup["model"] is not None
        assert setup["data"] is not None
        assert len(setup["feature_names"]) == 3
        assert "target" in setup["data"].columns

        # Verify model was trained
        assert hasattr(setup["model"], "predict")
        assert hasattr(setup["model"], "predict_proba")

        # Test basic prediction
        X_test = setup["data"][setup["feature_names"]].iloc[:5]
        predictions = setup["model"].predict(X_test)
        assert len(predictions) == 5
