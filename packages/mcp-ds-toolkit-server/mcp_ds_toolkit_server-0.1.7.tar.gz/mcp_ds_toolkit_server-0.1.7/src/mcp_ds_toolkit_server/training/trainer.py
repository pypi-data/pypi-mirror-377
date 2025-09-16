"""
Model Trainer - Core training functionality with scikit-learn integration.

This module provides comprehensive model training capabilities including:
- Support for all scikit-learn algorithms
- Automated hyperparameter tuning
- Cross-validation and model evaluation
- Performance metrics and model comparison
"""

import json
import pickle
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator
from sklearn.ensemble import (
    ExtraTreesClassifier,
    ExtraTreesRegressor,
    GradientBoostingClassifier,
    GradientBoostingRegressor,
    RandomForestClassifier,
    RandomForestRegressor,
)
from sklearn.linear_model import (
    ElasticNet,
    Lasso,
    LinearRegression,
    LogisticRegression,
    Ridge,
)
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    mean_absolute_error,
    mean_squared_error,
    precision_score,
    r2_score,
    recall_score,
)
from sklearn.model_selection import (
    GridSearchCV,
    RandomizedSearchCV,
    cross_val_score,
    train_test_split,
)
from sklearn.naive_bayes import BernoulliNB, GaussianNB, MultinomialNB
from sklearn.neighbors import KNeighborsClassifier, KNeighborsRegressor
from sklearn.preprocessing import LabelEncoder
from sklearn.svm import SVC, SVR
from sklearn.tree import DecisionTreeClassifier, DecisionTreeRegressor
from sklearn.utils.validation import check_X_y

from mcp_ds_toolkit_server.exceptions import TrainingError, ValidationError
from mcp_ds_toolkit_server.utils.config import Settings
from mcp_ds_toolkit_server.utils.logger import make_logger
from mcp_ds_toolkit_server.utils.persistence import (
    ArtifactBridge,
    PersistenceConfig,
    create_default_persistence_config,
)

logger = make_logger(__name__)


@dataclass
class TrainingConfig:
    """Configuration for model training.
    
    This configuration now uses the unified persistence system to manage
    how artifacts (models, predictions, metrics) are stored and returned.
    """

    # Model settings
    model_type: str = "auto"  # 'auto', 'classification', 'regression'
    algorithm: str = "random_forest"  # Algorithm to use
    random_state: int = 42

    # Training settings
    test_size: float = 0.2
    validation_size: float = 0.2
    cv_folds: int = 5
    stratify: bool = True

    # Hyperparameter tuning
    enable_tuning: bool = False
    tuning_method: str = "grid_search"  # 'grid_search', 'random_search'
    tuning_cv: int = 3
    tuning_scoring: Optional[str] = None
    max_iter: int = 100

    # Performance settings
    enable_cross_validation: bool = True
    scoring_metrics: List[str] = field(default_factory=lambda: ["accuracy", "f1_macro"])

    # Persistence settings - replaces individual save_* flags
    persistence: PersistenceConfig = field(default_factory=lambda: create_default_persistence_config("memory_only"))
    
    # Legacy compatibility methods
    @property
    def save_model(self) -> bool:
        """Legacy compatibility for save_model flag."""
        return self.persistence.should_save_to_filesystem() or self.persistence.should_store_in_memory()
    
    @property
    def save_predictions(self) -> bool:
        """Legacy compatibility for save_predictions flag."""
        return self.persistence.should_save_to_filesystem() or self.persistence.should_store_in_memory()
    
    @property
    def save_metrics(self) -> bool:
        """Legacy compatibility for save_metrics flag."""
        return self.persistence.should_save_to_filesystem() or self.persistence.should_store_in_memory()


@dataclass
class TrainingResults:
    """Results from model training with unified persistence support.
    
    This class now includes both traditional filesystem references and
    new persistence-based artifact storage information.
    """

    model: BaseEstimator
    model_type: str
    algorithm: str

    # Performance metrics
    train_score: float
    test_score: float
    cv_scores: Optional[List[float]] = None
    cv_mean: Optional[float] = None
    cv_std: Optional[float] = None

    # Detailed metrics
    metrics: Dict[str, Any] = field(default_factory=dict)

    # Predictions
    train_predictions: Optional[np.ndarray] = None
    test_predictions: Optional[np.ndarray] = None

    # Model metadata
    feature_names: List[str] = field(default_factory=list)
    target_name: str = ""
    training_time: float = 0.0

    # Legacy filesystem paths (maintained for compatibility)
    model_path: Optional[Path] = None
    metrics_path: Optional[Path] = None
    predictions_path: Optional[Path] = None
    
    # Preprocessor artifacts
    preprocessor_path: Optional[Path] = None
    preprocessing_config: Optional[Dict] = None
    
    # New persistence-based artifact storage
    artifact_storage: Dict[str, Any] = field(default_factory=dict)
    model_artifact_key: Optional[str] = None
    metrics_artifact_key: Optional[str] = None
    predictions_artifact_key: Optional[str] = None
    preprocessor_artifact_key: Optional[str] = None


class ModelTrainer:
    """Comprehensive model trainer with scikit-learn integration."""

    # Supported algorithms
    CLASSIFICATION_ALGORITHMS = {
        "random_forest": RandomForestClassifier,
        "gradient_boosting": GradientBoostingClassifier,
        "extra_trees": ExtraTreesClassifier,
        "logistic_regression": LogisticRegression,
        "svm": SVC,
        "knn": KNeighborsClassifier,
        "gaussian_nb": GaussianNB,
        "multinomial_nb": MultinomialNB,
        "bernoulli_nb": BernoulliNB,
        "decision_tree": DecisionTreeClassifier,
    }

    REGRESSION_ALGORITHMS = {
        "random_forest": RandomForestRegressor,
        "gradient_boosting": GradientBoostingRegressor,
        "extra_trees": ExtraTreesRegressor,
        "linear_regression": LinearRegression,
        "ridge": Ridge,
        "lasso": Lasso,
        "elastic_net": ElasticNet,
        "svm": SVR,
        "knn": KNeighborsRegressor,
        "decision_tree": DecisionTreeRegressor,
    }

    # Default hyperparameter grids
    HYPERPARAMETER_GRIDS = {
        "random_forest": {
            "n_estimators": [50, 100, 200],
            "max_depth": [None, 10, 20, 30],
            "min_samples_split": [2, 5, 10],
            "min_samples_leaf": [1, 2, 4],
        },
        "gradient_boosting": {
            "n_estimators": [50, 100, 200],
            "learning_rate": [0.01, 0.1, 0.2],
            "max_depth": [3, 5, 7],
        },
        "logistic_regression": {
            "C": [0.01, 0.1, 1, 10, 100],
            "solver": ["liblinear", "lbfgs"],
        },
        "svm": {
            "C": [0.1, 1, 10, 100],
            "kernel": ["linear", "rbf", "poly"],
            "gamma": ["scale", "auto"],
        },
    }

    def __init__(self, settings: Optional[Settings] = None, artifact_bridge: Optional[ArtifactBridge] = None):
        """Initialize the model trainer.

        Args:
            settings: Configuration settings.
            artifact_bridge: Artifact storage bridge for persistence operations.
        """
        self.settings = settings or Settings()
        self.logger = make_logger(__name__)
        
        # Initialize artifact bridge with default persistence config if not provided
        self.artifact_bridge = artifact_bridge or ArtifactBridge(
            create_default_persistence_config("memory_only")
        )

        # Initialize label encoder for classification
        self.label_encoder = LabelEncoder()
        self._is_label_encoded = False

    def train_model(
        self,
        X: Union[pd.DataFrame, np.ndarray],
        y: Union[pd.Series, np.ndarray],
        config: Optional[TrainingConfig] = None,
        output_dir: Optional[Path] = None,
    ) -> TrainingResults:
        """Train a machine learning model.

        Args:
            X: Feature matrix.
            y: Target vector.
            config: Training configuration.
            output_dir: Directory to save outputs.

        Returns:
            Training results with model and metrics.

        Raises:
            TrainingError: If training fails.
            ValidationError: If input validation fails.
        """
        config = config or TrainingConfig()
        output_dir = output_dir or self.settings.models_dir

        try:
            # Validate inputs
            X, y = self._validate_inputs(X, y)

            # Determine model type
            model_type = self._determine_model_type(y, config.model_type)

            # Get feature and target names
            feature_names = self._get_feature_names(X)
            target_name = self._get_target_name(y)

            # Prepare data
            X_processed, y_processed = self._prepare_data(X, y, model_type)

            # Split data
            X_train, X_test, y_train, y_test = self._split_data(
                X_processed, y_processed, config
            )

            # Create and configure model
            model = self._create_model(config.algorithm, model_type, config)

            # Train model
            import time

            start_time = time.time()

            if config.enable_tuning:
                model = self._tune_hyperparameters(model, X_train, y_train, config)

            model.fit(X_train, y_train)
            training_time = time.time() - start_time

            # Evaluate model
            results = self._evaluate_model(
                model, X_train, X_test, y_train, y_test, config, model_type
            )

            # Update results with metadata
            results.model_type = model_type
            results.algorithm = config.algorithm
            results.feature_names = feature_names
            results.target_name = target_name
            results.training_time = training_time

            # Save outputs using the new persistence system
            if config.persistence.should_store_in_memory() or config.persistence.should_save_to_filesystem():
                self._save_outputs_with_persistence(results, config, output_dir)

            self.logger.info(
                f"Successfully trained {config.algorithm} model "
                f"(type: {model_type}, score: {results.test_score:.4f})"
            )

            return results

        except Exception as e:
            self.logger.error(f"Model training failed: {str(e)}")
            raise TrainingError(f"Model training failed: {str(e)}") from e

    def _validate_inputs(
        self, X: Union[pd.DataFrame, np.ndarray], y: Union[pd.Series, np.ndarray]
    ) -> Tuple[np.ndarray, np.ndarray]:
        """Validate and convert inputs to numpy arrays."""
        try:
            # Convert to numpy arrays
            if isinstance(X, pd.DataFrame):
                X_array = X.values
            else:
                X_array = np.asarray(X)

            if isinstance(y, (pd.Series, pd.DataFrame)):
                y_array = y.values.ravel()
            else:
                y_array = np.asarray(y).ravel()

            # Validate using sklearn
            X_array, y_array = check_X_y(X_array, y_array)

            # Check for minimum samples
            if len(X_array) < 10:
                raise ValidationError("Need at least 10 samples for training")

            # Check for missing values
            if np.isnan(X_array).any():
                raise ValidationError("Features contain missing values")

            if np.isnan(y_array).any():
                raise ValidationError("Target contains missing values")

            return X_array, y_array

        except Exception as e:
            raise ValidationError(f"Input validation failed: {str(e)}") from e

    def _determine_model_type(self, y: np.ndarray, model_type: str) -> str:
        """Determine if this is a classification or regression problem."""
        if model_type in ["classification", "regression"]:
            return model_type

        # Auto-detect based on target variable
        unique_values = np.unique(y)

        # Check if target is numeric and continuous
        if np.issubdtype(y.dtype, np.number):
            # If few unique values relative to sample size, likely classification
            if len(unique_values) <= max(10, len(y) // 20):
                return "classification"
            else:
                return "regression"
        else:
            # Non-numeric target is classification
            return "classification"

    def _get_feature_names(self, X: Union[pd.DataFrame, np.ndarray]) -> List[str]:
        """Get feature names from input data."""
        if isinstance(X, pd.DataFrame):
            return list(X.columns)
        else:
            return [f"feature_{i}" for i in range(X.shape[1])]

    def _get_target_name(self, y: Union[pd.Series, np.ndarray]) -> str:
        """Get target name from input data."""
        if isinstance(y, pd.Series):
            return y.name or "target"
        else:
            return "target"

    def _prepare_data(
        self, X: np.ndarray, y: np.ndarray, model_type: str
    ) -> Tuple[np.ndarray, np.ndarray]:
        """Prepare data for training."""
        X_processed = X.copy()
        y_processed = y.copy()

        # For classification, encode string labels if necessary
        if model_type == "classification" and y_processed.dtype == object:
            y_processed = self.label_encoder.fit_transform(y_processed)
            self._is_label_encoded = True

        return X_processed, y_processed

    def _split_data(
        self, X: np.ndarray, y: np.ndarray, config: TrainingConfig
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        """Split data into training and testing sets."""
        stratify = y if config.stratify and len(np.unique(y)) > 1 else None

        return train_test_split(
            X,
            y,
            test_size=config.test_size,
            random_state=config.random_state,
            stratify=stratify,
        )

    def _create_model(
        self, algorithm: str, model_type: str, config: TrainingConfig
    ) -> BaseEstimator:
        """Create and configure a model."""
        # Select algorithm dict based on model type
        if model_type == "classification":
            algorithms = self.CLASSIFICATION_ALGORITHMS
        else:
            algorithms = self.REGRESSION_ALGORITHMS

        if algorithm not in algorithms:
            available = list(algorithms.keys())
            raise TrainingError(
                f"Algorithm '{algorithm}' not available for {model_type}. "
                f"Available: {available}"
            )

        model_class = algorithms[algorithm]

        # Set random state if the model supports it
        kwargs = {}
        if hasattr(model_class, "random_state"):
            kwargs["random_state"] = config.random_state

        # Special configurations for specific algorithms
        if algorithm == "logistic_regression":
            kwargs["max_iter"] = config.max_iter
        elif algorithm in ["ridge", "lasso", "elastic_net"]:
            kwargs["random_state"] = config.random_state

        return model_class(**kwargs)

    def _tune_hyperparameters(
        self,
        model: BaseEstimator,
        X: np.ndarray,
        y: np.ndarray,
        config: TrainingConfig,
    ) -> BaseEstimator:
        """Tune model hyperparameters."""
        algorithm = config.algorithm

        if algorithm not in self.HYPERPARAMETER_GRIDS:
            self.logger.warning(
                f"No hyperparameter grid defined for {algorithm}, skipping tuning"
            )
            return model

        param_grid = self.HYPERPARAMETER_GRIDS[algorithm]

        # Choose search method
        if config.tuning_method == "grid_search":
            search = GridSearchCV(
                model,
                param_grid,
                cv=config.tuning_cv,
                scoring=config.tuning_scoring,
                n_jobs=-1,
            )
        else:  # random_search
            search = RandomizedSearchCV(
                model,
                param_grid,
                n_iter=20,
                cv=config.tuning_cv,
                scoring=config.tuning_scoring,
                random_state=config.random_state,
                n_jobs=-1,
            )

        search.fit(X, y)

        self.logger.info(f"Best hyperparameters for {algorithm}: {search.best_params_}")

        return search.best_estimator_

    def _evaluate_model(
        self,
        model: BaseEstimator,
        X_train: np.ndarray,
        X_test: np.ndarray,
        y_train: np.ndarray,
        y_test: np.ndarray,
        config: TrainingConfig,
        model_type: str,
    ) -> TrainingResults:
        """Evaluate model performance."""
        # Get predictions
        train_pred = model.predict(X_train)
        test_pred = model.predict(X_test)

        # Calculate basic scores
        if model_type == "classification":
            train_score = accuracy_score(y_train, train_pred)
            test_score = accuracy_score(y_test, test_pred)
        else:
            train_score = r2_score(y_train, train_pred)
            test_score = r2_score(y_test, test_pred)

        # Cross-validation
        cv_scores = None
        cv_mean = None
        cv_std = None

        if config.enable_cross_validation:
            cv_scores = cross_val_score(model, X_train, y_train, cv=config.cv_folds)
            cv_mean = np.mean(cv_scores)
            cv_std = np.std(cv_scores)

        # Detailed metrics
        metrics = self._calculate_detailed_metrics(
            y_train, y_test, train_pred, test_pred, model_type
        )

        return TrainingResults(
            model=model,
            model_type=model_type,
            algorithm="",  # Will be set by caller
            train_score=train_score,
            test_score=test_score,
            cv_scores=cv_scores.tolist() if cv_scores is not None else None,
            cv_mean=cv_mean,
            cv_std=cv_std,
            metrics=metrics,
            train_predictions=train_pred,
            test_predictions=test_pred,
        )

    def _calculate_detailed_metrics(
        self,
        y_train: np.ndarray,
        y_test: np.ndarray,
        train_pred: np.ndarray,
        test_pred: np.ndarray,
        model_type: str,
    ) -> Dict[str, Any]:
        """Calculate detailed performance metrics."""
        metrics = {}

        if model_type == "classification":
            # Classification metrics
            metrics.update(
                {
                    "train_accuracy": accuracy_score(y_train, train_pred),
                    "test_accuracy": accuracy_score(y_test, test_pred),
                    "train_precision": precision_score(
                        y_train, train_pred, average="weighted", zero_division=0
                    ),
                    "test_precision": precision_score(
                        y_test, test_pred, average="weighted", zero_division=0
                    ),
                    "train_recall": recall_score(
                        y_train, train_pred, average="weighted", zero_division=0
                    ),
                    "test_recall": recall_score(
                        y_test, test_pred, average="weighted", zero_division=0
                    ),
                    "train_f1": f1_score(
                        y_train, train_pred, average="weighted", zero_division=0
                    ),
                    "test_f1": f1_score(
                        y_test, test_pred, average="weighted", zero_division=0
                    ),
                }
            )

            # Classification report
            try:
                metrics["classification_report"] = classification_report(
                    y_test, test_pred, output_dict=True, zero_division=0
                )
                metrics["confusion_matrix"] = confusion_matrix(
                    y_test, test_pred
                ).tolist()
            except Exception as e:
                self.logger.warning(f"Could not generate classification report: {e}")

        else:
            # Regression metrics
            metrics.update(
                {
                    "train_r2": r2_score(y_train, train_pred),
                    "test_r2": r2_score(y_test, test_pred),
                    "train_mse": mean_squared_error(y_train, train_pred),
                    "test_mse": mean_squared_error(y_test, test_pred),
                    "train_rmse": np.sqrt(mean_squared_error(y_train, train_pred)),
                    "test_rmse": np.sqrt(mean_squared_error(y_test, test_pred)),
                    "train_mae": mean_absolute_error(y_train, train_pred),
                    "test_mae": mean_absolute_error(y_test, test_pred),
                }
            )

        return metrics

    def _save_outputs_with_persistence(
        self, results: TrainingResults, config: TrainingConfig, output_dir: Path
    ) -> None:
        """Save training outputs using the new persistence system.
        
        This method replaces the legacy _save_outputs method and uses the
        ArtifactBridge for unified persistence management.
        """
        timestamp = pd.Timestamp.now().strftime("%Y%m%d_%H%M%S")
        base_name = f"{results.algorithm}_{timestamp}"
        
        # Update artifact bridge configuration if needed
        if self.artifact_bridge.config != config.persistence:
            self.artifact_bridge = ArtifactBridge(config.persistence)

        # Save model
        if config.save_model:
            model_key = f"{base_name}_model"
            model_path = output_dir / f"{base_name}_model.pkl" if config.persistence.should_save_to_filesystem() else None
            
            model_storage = self.artifact_bridge.store_artifact(
                key=model_key,
                artifact=results.model,
                artifact_type="model",
                filesystem_path=model_path
            )
            
            results.model_artifact_key = model_key
            results.artifact_storage["model"] = model_storage
            
            # Maintain legacy compatibility
            if "filesystem_reference" in model_storage:
                results.model_path = Path(model_storage["filesystem_reference"].replace("file://", ""))
            
            self.logger.info(f"Model stored with key: {model_key}")

        # Save metrics
        if config.save_metrics:
            metrics_data = {
                "model_type": results.model_type,
                "algorithm": results.algorithm,
                "train_score": results.train_score,
                "test_score": results.test_score,
                "cv_mean": results.cv_mean,
                "cv_std": results.cv_std,
                "training_time": results.training_time,
                "feature_names": results.feature_names,
                "target_name": results.target_name,
                "metrics": results.metrics,
            }

            metrics_key = f"{base_name}_metrics"
            metrics_path = output_dir / f"{base_name}_metrics.json" if config.persistence.should_save_to_filesystem() else None
            
            metrics_storage = self.artifact_bridge.store_artifact(
                key=metrics_key,
                artifact=metrics_data,
                artifact_type="metrics",
                filesystem_path=metrics_path
            )
            
            results.metrics_artifact_key = metrics_key
            results.artifact_storage["metrics"] = metrics_storage
            
            # Maintain legacy compatibility
            if "filesystem_reference" in metrics_storage:
                results.metrics_path = Path(metrics_storage["filesystem_reference"].replace("file://", ""))
            
            self.logger.info(f"Metrics stored with key: {metrics_key}")

        # Save predictions
        if config.save_predictions:
            predictions_data = {
                "train_predictions": results.train_predictions.tolist(),
                "test_predictions": results.test_predictions.tolist(),
            }

            predictions_key = f"{base_name}_predictions"
            predictions_path = output_dir / f"{base_name}_predictions.json" if config.persistence.should_save_to_filesystem() else None
            
            predictions_storage = self.artifact_bridge.store_artifact(
                key=predictions_key,
                artifact=predictions_data,
                artifact_type="predictions",
                filesystem_path=predictions_path
            )
            
            results.predictions_artifact_key = predictions_key
            results.artifact_storage["predictions"] = predictions_storage
            
            # Maintain legacy compatibility
            if "filesystem_reference" in predictions_storage:
                results.predictions_path = Path(predictions_storage["filesystem_reference"].replace("file://", ""))
                
            self.logger.info(f"Predictions stored with key: {predictions_key}")

    def _save_outputs(
        self, results: TrainingResults, config: TrainingConfig, output_dir: Path
    ) -> None:
        """Legacy save outputs method for backward compatibility.
        
        This method is deprecated and will be removed in a future version.
        Use _save_outputs_with_persistence instead.
        """
        self.logger.warning("Using deprecated _save_outputs method. Please update to use _save_outputs_with_persistence.")
        
        # Convert legacy config to persistence config and delegate
        legacy_persistence = create_default_persistence_config("filesystem")
        old_persistence = config.persistence
        config.persistence = legacy_persistence
        
        try:
            self._save_outputs_with_persistence(results, config, output_dir)
        finally:
            config.persistence = old_persistence

    def get_available_algorithms(self, model_type: str = "all") -> Dict[str, List[str]]:
        """Get list of available algorithms.

        Args:
            model_type: 'all', 'classification', or 'regression'.

        Returns:
            Dictionary of available algorithms by type.
        """
        if model_type == "classification":
            return {"classification": list(self.CLASSIFICATION_ALGORITHMS.keys())}
        elif model_type == "regression":
            return {"regression": list(self.REGRESSION_ALGORITHMS.keys())}
        else:
            return {
                "classification": list(self.CLASSIFICATION_ALGORITHMS.keys()),
                "regression": list(self.REGRESSION_ALGORITHMS.keys()),
            }

    def load_model(self, model_path: Path) -> BaseEstimator:
        """Load a saved model.

        Args:
            model_path: Path to the saved model file.

        Returns:
            Loaded model.

        Raises:
            TrainingError: If model loading fails.
        """
        try:
            with open(model_path, "rb") as f:
                model = pickle.load(f)

            self.logger.info(f"Model loaded from {model_path}")
            return model

        except Exception as e:
            raise TrainingError(
                f"Failed to load model from {model_path}: {str(e)}"
            ) from e

    def get_artifact(self, artifact_key: str) -> Optional[Any]:
        """Retrieve an artifact from the artifact bridge.
        
        Args:
            artifact_key: The key of the artifact to retrieve
            
        Returns:
            The stored artifact, or None if not found
        """
        return self.artifact_bridge.retrieve_artifact(artifact_key)
    
    def list_artifacts(self) -> Dict[str, Dict[str, Any]]:
        """List all stored artifacts with their metadata.
        
        Returns:
            Dictionary mapping artifact keys to their metadata
        """
        return self.artifact_bridge.list_artifacts()
    
    def export_session(self, output_dir: Path, include_types: Optional[List[str]] = None) -> Dict[str, Any]:
        """Export the current training session to filesystem.
        
        Args:
            output_dir: Directory to export artifacts to
            include_types: Optional list of artifact types to include
            
        Returns:
            Export manifest with details of exported artifacts
        """
        return self.artifact_bridge.export_session_to_filesystem(output_dir, include_types)
    
    def update_persistence_config(self, persistence_config: PersistenceConfig) -> None:
        """Update the persistence configuration for this trainer.
        
        Args:
            persistence_config: New persistence configuration to use
        """
        self.artifact_bridge = ArtifactBridge(persistence_config)
        self.logger.info(f"Updated persistence config to mode: {persistence_config.mode.value}")
