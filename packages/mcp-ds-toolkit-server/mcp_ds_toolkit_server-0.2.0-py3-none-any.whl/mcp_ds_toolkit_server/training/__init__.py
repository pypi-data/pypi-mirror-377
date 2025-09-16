"""
Model Training - Comprehensive model training and evaluation capabilities.

This module provides scikit-learn model training functionality including:
- Model training with all scikit-learn algorithms
- Hyperparameter tuning and optimization
- Model evaluation and validation
- Cross-validation and performance metrics
"""

from mcp_ds_toolkit_server.training.evaluator import (
    ComparisonResults,
    EvaluationConfig,
    ModelEvaluation,
    ModelEvaluator,
)
from mcp_ds_toolkit_server.training.trainer import ModelTrainer, TrainingConfig, TrainingResults

__all__ = [
    "ModelTrainer",
    "TrainingConfig",
    "TrainingResults",
    "ModelEvaluator",
    "EvaluationConfig",
    "ModelEvaluation",
    "ComparisonResults",
]
