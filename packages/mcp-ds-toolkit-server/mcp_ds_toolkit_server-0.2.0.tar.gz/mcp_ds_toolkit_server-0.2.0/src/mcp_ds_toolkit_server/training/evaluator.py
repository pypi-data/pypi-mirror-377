"""
Model Evaluator - Comprehensive model evaluation and comparison.

This module provides functionality for:
- Model performance evaluation
- Model comparison and ranking
- Cross-validation and statistical testing
- Evaluation metric calculation
"""

import json
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import numpy as np
import pandas as pd
from scipy import stats
from sklearn.base import BaseEstimator
from sklearn.metrics import (
    accuracy_score,
    average_precision_score,
    classification_report,
    confusion_matrix,
    explained_variance_score,
    f1_score,
    mean_absolute_error,
    mean_squared_error,
    precision_score,
    r2_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import cross_validate, learning_curve, validation_curve

from mcp_ds_toolkit_server.exceptions import EvaluationError
from mcp_ds_toolkit_server.utils.config import Settings
from mcp_ds_toolkit_server.utils.logger import make_logger

logger = make_logger(__name__)


@dataclass
class EvaluationConfig:
    """Configuration for model evaluation."""

    # Evaluation settings
    cv_folds: int = 5
    scoring_metrics: List[str] = field(default_factory=lambda: ["accuracy", "f1_macro"])

    # Statistical testing
    enable_statistical_tests: bool = True
    significance_level: float = 0.05

    # Learning curves
    generate_learning_curves: bool = False
    learning_curve_train_sizes: List[float] = field(
        default_factory=lambda: [0.1, 0.33, 0.55, 0.78, 1.0]
    )

    # Output settings
    save_results: bool = True
    detailed_metrics: bool = True


@dataclass
class ModelEvaluation:
    """Results from model evaluation."""

    model_name: str
    model_type: str  # 'classification' or 'regression'

    # Cross-validation scores
    cv_scores: Dict[str, List[float]] = field(default_factory=dict)
    cv_means: Dict[str, float] = field(default_factory=dict)
    cv_stds: Dict[str, float] = field(default_factory=dict)

    # Test set performance
    test_scores: Dict[str, float] = field(default_factory=dict)

    # Detailed metrics
    detailed_metrics: Dict[str, Any] = field(default_factory=dict)

    # Learning curves (if generated)
    learning_curves: Optional[Dict[str, Any]] = None

    # Model metadata
    training_time: float = 0.0
    prediction_time: float = 0.0


@dataclass
class ComparisonResults:
    """Results from model comparison."""

    evaluations: List[ModelEvaluation] = field(default_factory=list)
    rankings: Dict[str, List[str]] = field(default_factory=dict)
    statistical_tests: Dict[str, Any] = field(default_factory=dict)
    best_models: Dict[str, str] = field(default_factory=dict)

    # Summary statistics
    summary_table: Optional[pd.DataFrame] = None


class ModelEvaluator:
    """Comprehensive model evaluation and comparison."""

    # Classification metrics
    CLASSIFICATION_METRICS = {
        "accuracy": accuracy_score,
        "precision_micro": lambda y_true, y_pred: precision_score(
            y_true, y_pred, average="micro", zero_division=0
        ),
        "precision_macro": lambda y_true, y_pred: precision_score(
            y_true, y_pred, average="macro", zero_division=0
        ),
        "precision_weighted": lambda y_true, y_pred: precision_score(
            y_true, y_pred, average="weighted", zero_division=0
        ),
        "recall_micro": lambda y_true, y_pred: recall_score(
            y_true, y_pred, average="micro", zero_division=0
        ),
        "recall_macro": lambda y_true, y_pred: recall_score(
            y_true, y_pred, average="macro", zero_division=0
        ),
        "recall_weighted": lambda y_true, y_pred: recall_score(
            y_true, y_pred, average="weighted", zero_division=0
        ),
        "f1_micro": lambda y_true, y_pred: f1_score(
            y_true, y_pred, average="micro", zero_division=0
        ),
        "f1_macro": lambda y_true, y_pred: f1_score(
            y_true, y_pred, average="macro", zero_division=0
        ),
        "f1_weighted": lambda y_true, y_pred: f1_score(
            y_true, y_pred, average="weighted", zero_division=0
        ),
    }

    # Regression metrics
    REGRESSION_METRICS = {
        "r2": r2_score,
        "mse": mean_squared_error,
        "rmse": lambda y_true, y_pred: np.sqrt(mean_squared_error(y_true, y_pred)),
        "mae": mean_absolute_error,
        "explained_variance": explained_variance_score,
    }

    def __init__(self, settings: Optional[Settings] = None):
        """Initialize the model evaluator.

        Args:
            settings: Configuration settings.
        """
        self.settings = settings or Settings()
        self.logger = make_logger(__name__)

    def evaluate_model(
        self,
        model: BaseEstimator,
        X: Union[pd.DataFrame, np.ndarray],
        y: Union[pd.Series, np.ndarray],
        model_name: str = "model",
        config: Optional[EvaluationConfig] = None,
    ) -> ModelEvaluation:
        """Evaluate a single model.

        Args:
            model: Trained model to evaluate.
            X: Feature matrix.
            y: Target vector.
            model_name: Name for the model.
            config: Evaluation configuration.

        Returns:
            Model evaluation results.

        Raises:
            EvaluationError: If evaluation fails.
        """
        config = config or EvaluationConfig()

        try:
            # Convert inputs to numpy arrays
            X_array = np.asarray(X)
            y_array = np.asarray(y).ravel()

            # Determine model type
            model_type = self._determine_model_type(model, y_array)

            # Get appropriate metrics
            metrics = self._get_metrics_for_type(model_type)

            # Cross-validation evaluation
            cv_results = self._cross_validate_model(
                model, X_array, y_array, metrics, config
            )

            # Test set evaluation (using entire dataset as test for simplicity)
            test_results = self._evaluate_on_test_set(model, X_array, y_array, metrics)

            # Detailed metrics
            detailed_metrics = {}
            if config.detailed_metrics:
                detailed_metrics = self._calculate_detailed_metrics(
                    model, X_array, y_array, model_type
                )

            # Learning curves
            learning_curves = None
            if config.generate_learning_curves:
                learning_curves = self._generate_learning_curves(
                    model, X_array, y_array, config
                )

            # Create evaluation result
            evaluation = ModelEvaluation(
                model_name=model_name,
                model_type=model_type,
                cv_scores=cv_results["scores"],
                cv_means=cv_results["means"],
                cv_stds=cv_results["stds"],
                test_scores=test_results,
                detailed_metrics=detailed_metrics,
                learning_curves=learning_curves,
            )

            self.logger.info(f"Evaluated model '{model_name}' successfully")
            return evaluation

        except Exception as e:
            self.logger.error(f"Model evaluation failed for '{model_name}': {str(e)}")
            raise EvaluationError(f"Model evaluation failed: {str(e)}") from e

    def compare_models(
        self,
        models: Dict[str, BaseEstimator],
        X: Union[pd.DataFrame, np.ndarray],
        y: Union[pd.Series, np.ndarray],
        config: Optional[EvaluationConfig] = None,
        output_dir: Optional[Path] = None,
    ) -> ComparisonResults:
        """Compare multiple models.

        Args:
            models: Dictionary of model name to model instance.
            X: Feature matrix.
            y: Target vector.
            config: Evaluation configuration.
            output_dir: Directory to save results.

        Returns:
            Model comparison results.

        Raises:
            EvaluationError: If comparison fails.
        """
        config = config or EvaluationConfig()
        output_dir = output_dir or self.settings.experiments_dir

        try:
            # Evaluate each model
            evaluations = []
            for model_name, model in models.items():
                evaluation = self.evaluate_model(model, X, y, model_name, config)
                evaluations.append(evaluation)

            # Create rankings
            rankings = self._create_rankings(evaluations)

            # Statistical tests
            statistical_tests = {}
            if config.enable_statistical_tests and len(evaluations) > 1:
                statistical_tests = self._perform_statistical_tests(evaluations, config)

            # Identify best models
            best_models = self._identify_best_models(evaluations)

            # Create summary table
            summary_table = self._create_summary_table(evaluations)

            # Create comparison results
            comparison = ComparisonResults(
                evaluations=evaluations,
                rankings=rankings,
                statistical_tests=statistical_tests,
                best_models=best_models,
                summary_table=summary_table,
            )

            # Save results
            if config.save_results:
                self._save_comparison_results(comparison, output_dir)

            self.logger.info(f"Compared {len(models)} models successfully")
            return comparison

        except Exception as e:
            self.logger.error(f"Model comparison failed: {str(e)}")
            raise EvaluationError(f"Model comparison failed: {str(e)}") from e

    def _determine_model_type(self, model: BaseEstimator, y: np.ndarray) -> str:
        """Determine if model is for classification or regression."""
        # Check if model has classification-specific attributes
        if hasattr(model, "classes_"):
            return "classification"

        # Check y values
        unique_values = np.unique(y)
        if len(unique_values) <= max(10, len(y) // 20) and np.issubdtype(
            y.dtype, np.integer
        ):
            return "classification"
        else:
            return "regression"

    def _get_metrics_for_type(self, model_type: str) -> Dict[str, callable]:
        """Get appropriate metrics for model type."""
        if model_type == "classification":
            return self.CLASSIFICATION_METRICS
        else:
            return self.REGRESSION_METRICS

    def _cross_validate_model(
        self,
        model: BaseEstimator,
        X: np.ndarray,
        y: np.ndarray,
        metrics: Dict[str, callable],
        config: EvaluationConfig,
    ) -> Dict[str, Any]:
        """Perform cross-validation evaluation."""
        # Use sklearn's cross_validate for built-in scoring
        scoring = list(metrics.keys())

        try:
            cv_results = cross_validate(
                model,
                X,
                y,
                cv=config.cv_folds,
                scoring=scoring,
                return_train_score=False,
            )

            # Extract results
            scores = {}
            means = {}
            stds = {}

            for metric in scoring:
                test_key = f"test_{metric}"
                if test_key in cv_results:
                    scores[metric] = cv_results[test_key].tolist()
                    means[metric] = np.mean(cv_results[test_key])
                    stds[metric] = np.std(cv_results[test_key])

            return {"scores": scores, "means": means, "stds": stds}

        except Exception as e:
            self.logger.warning(
                f"Cross-validation failed, using manual evaluation: {e}"
            )

            # Fallback to manual cross-validation
            from sklearn.model_selection import KFold, StratifiedKFold

            # Choose appropriate CV splitter
            if self._determine_model_type(model, y) == "classification":
                cv_splitter = StratifiedKFold(
                    n_splits=config.cv_folds, shuffle=True, random_state=42
                )
            else:
                cv_splitter = KFold(
                    n_splits=config.cv_folds, shuffle=True, random_state=42
                )

            scores = {metric: [] for metric in metrics.keys()}

            for train_idx, val_idx in cv_splitter.split(X, y):
                X_train, X_val = X[train_idx], X[val_idx]
                y_train, y_val = y[train_idx], y[val_idx]

                # Fit and predict
                model.fit(X_train, y_train)
                y_pred = model.predict(X_val)

                # Calculate metrics
                for metric_name, metric_func in metrics.items():
                    try:
                        score = metric_func(y_val, y_pred)
                        scores[metric_name].append(score)
                    except Exception:
                        scores[metric_name].append(0.0)

            # Calculate means and stds
            means = {metric: np.mean(scores[metric]) for metric in scores}
            stds = {metric: np.std(scores[metric]) for metric in scores}

            return {"scores": scores, "means": means, "stds": stds}

    def _evaluate_on_test_set(
        self,
        model: BaseEstimator,
        X: np.ndarray,
        y: np.ndarray,
        metrics: Dict[str, callable],
    ) -> Dict[str, float]:
        """Evaluate model on test set."""
        try:
            # Make predictions
            y_pred = model.predict(X)

            # Calculate metrics
            test_scores = {}
            for metric_name, metric_func in metrics.items():
                try:
                    score = metric_func(y, y_pred)
                    test_scores[metric_name] = float(score)
                except Exception as e:
                    self.logger.warning(f"Could not calculate {metric_name}: {e}")
                    test_scores[metric_name] = 0.0

            return test_scores

        except Exception as e:
            self.logger.warning(f"Test set evaluation failed: {e}")
            return {}

    def _calculate_detailed_metrics(
        self,
        model: BaseEstimator,
        X: np.ndarray,
        y: np.ndarray,
        model_type: str,
    ) -> Dict[str, Any]:
        """Calculate detailed metrics."""
        detailed = {}

        try:
            y_pred = model.predict(X)

            if model_type == "classification":
                # Classification report
                try:
                    detailed["classification_report"] = classification_report(
                        y, y_pred, output_dict=True, zero_division=0
                    )
                except Exception:
                    pass

                # Confusion matrix
                try:
                    detailed["confusion_matrix"] = confusion_matrix(y, y_pred).tolist()
                except Exception:
                    pass

                # ROC AUC (for binary classification)
                try:
                    if len(np.unique(y)) == 2 and hasattr(model, "predict_proba"):
                        y_proba = model.predict_proba(X)[:, 1]
                        detailed["roc_auc"] = roc_auc_score(y, y_proba)
                        detailed["average_precision"] = average_precision_score(
                            y, y_proba
                        )
                except Exception:
                    pass

            else:
                # Regression residuals analysis
                residuals = y - y_pred
                detailed.update(
                    {
                        "residuals_mean": float(np.mean(residuals)),
                        "residuals_std": float(np.std(residuals)),
                        "residuals_min": float(np.min(residuals)),
                        "residuals_max": float(np.max(residuals)),
                    }
                )

        except Exception as e:
            self.logger.warning(f"Could not calculate detailed metrics: {e}")

        return detailed

    def _generate_learning_curves(
        self,
        model: BaseEstimator,
        X: np.ndarray,
        y: np.ndarray,
        config: EvaluationConfig,
    ) -> Dict[str, Any]:
        """Generate learning curves."""
        try:
            train_sizes, train_scores, val_scores = learning_curve(
                model,
                X,
                y,
                train_sizes=config.learning_curve_train_sizes,
                cv=config.cv_folds,
                scoring=(
                    "accuracy"
                    if self._determine_model_type(model, y) == "classification"
                    else "r2"
                ),
            )

            return {
                "train_sizes": train_sizes.tolist(),
                "train_scores_mean": np.mean(train_scores, axis=1).tolist(),
                "train_scores_std": np.std(train_scores, axis=1).tolist(),
                "val_scores_mean": np.mean(val_scores, axis=1).tolist(),
                "val_scores_std": np.std(val_scores, axis=1).tolist(),
            }

        except Exception as e:
            self.logger.warning(f"Could not generate learning curves: {e}")
            return {}

    def _create_rankings(
        self, evaluations: List[ModelEvaluation]
    ) -> Dict[str, List[str]]:
        """Create rankings for each metric."""
        rankings = {}

        # Get all metrics
        all_metrics = set()
        for eval_result in evaluations:
            all_metrics.update(eval_result.cv_means.keys())

        # Rank models for each metric
        for metric in all_metrics:
            # Get scores for this metric
            scores = []
            for eval_result in evaluations:
                if metric in eval_result.cv_means:
                    scores.append(
                        (eval_result.model_name, eval_result.cv_means[metric])
                    )

            # Sort by score (descending for most metrics, ascending for error metrics)
            reverse = not metric.lower().endswith(("error", "mse", "mae", "rmse"))
            sorted_scores = sorted(scores, key=lambda x: x[1], reverse=reverse)

            rankings[metric] = [name for name, _ in sorted_scores]

        return rankings

    def _perform_statistical_tests(
        self, evaluations: List[ModelEvaluation], config: EvaluationConfig
    ) -> Dict[str, Any]:
        """Perform statistical significance tests."""
        tests = {}

        try:
            # Pairwise t-tests for each metric
            for metric in evaluations[0].cv_scores.keys():
                tests[metric] = {}

                for i, eval1 in enumerate(evaluations):
                    for j, eval2 in enumerate(evaluations[i + 1 :], i + 1):
                        scores1 = eval1.cv_scores[metric]
                        scores2 = eval2.cv_scores[metric]

                        # Paired t-test
                        if len(scores1) == len(scores2):
                            t_stat, p_value = stats.ttest_rel(scores1, scores2)

                            test_key = f"{eval1.model_name}_vs_{eval2.model_name}"
                            tests[metric][test_key] = {
                                "t_statistic": float(t_stat),
                                "p_value": float(p_value),
                                "significant": p_value < config.significance_level,
                            }

        except Exception as e:
            self.logger.warning(f"Statistical tests failed: {e}")

        return tests

    def _identify_best_models(
        self, evaluations: List[ModelEvaluation]
    ) -> Dict[str, str]:
        """Identify best model for each metric."""
        best_models = {}

        # Get all metrics
        all_metrics = set()
        for eval_result in evaluations:
            all_metrics.update(eval_result.cv_means.keys())

        # Find best model for each metric
        for metric in all_metrics:
            best_score = None
            best_model = None

            # Determine if higher or lower is better
            higher_is_better = not metric.lower().endswith(
                ("error", "mse", "mae", "rmse")
            )

            for eval_result in evaluations:
                if metric in eval_result.cv_means:
                    score = eval_result.cv_means[metric]

                    if best_score is None:
                        best_score = score
                        best_model = eval_result.model_name
                    elif (higher_is_better and score > best_score) or (
                        not higher_is_better and score < best_score
                    ):
                        best_score = score
                        best_model = eval_result.model_name

            if best_model:
                best_models[metric] = best_model

        return best_models

    def _create_summary_table(self, evaluations: List[ModelEvaluation]) -> pd.DataFrame:
        """Create summary table of results."""
        try:
            # Collect data for table
            data = []
            for eval_result in evaluations:
                row = {"model": eval_result.model_name, "type": eval_result.model_type}

                # Add CV means and stds
                for metric, mean_score in eval_result.cv_means.items():
                    row[f"{metric}_mean"] = mean_score
                    if metric in eval_result.cv_stds:
                        row[f"{metric}_std"] = eval_result.cv_stds[metric]

                data.append(row)

            return pd.DataFrame(data)

        except Exception as e:
            self.logger.warning(f"Could not create summary table: {e}")
            return pd.DataFrame()

    def _save_comparison_results(
        self, comparison: ComparisonResults, output_dir: Path
    ) -> None:
        """Save comparison results to files."""
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        timestamp = pd.Timestamp.now().strftime("%Y%m%d_%H%M%S")

        try:
            # Save summary table
            if (
                comparison.summary_table is not None
                and not comparison.summary_table.empty
            ):
                summary_path = output_dir / f"model_comparison_{timestamp}.csv"
                comparison.summary_table.to_csv(summary_path, index=False)
                self.logger.info(f"Summary table saved to {summary_path}")

            # Save detailed results
            results_data = {
                "rankings": comparison.rankings,
                "best_models": comparison.best_models,
                "statistical_tests": comparison.statistical_tests,
                "evaluations": [
                    {
                        "model_name": eval_result.model_name,
                        "model_type": eval_result.model_type,
                        "cv_means": eval_result.cv_means,
                        "cv_stds": eval_result.cv_stds,
                        "test_scores": eval_result.test_scores,
                    }
                    for eval_result in comparison.evaluations
                ],
            }

            results_path = output_dir / f"detailed_comparison_{timestamp}.json"
            with open(results_path, "w") as f:
                json.dump(results_data, f, indent=2, default=str)

            self.logger.info(f"Detailed results saved to {results_path}")

        except Exception as e:
            self.logger.warning(f"Could not save comparison results: {e}")

    def get_available_metrics(self, model_type: str = "all") -> Dict[str, List[str]]:
        """Get list of available metrics.

        Args:
            model_type: 'all', 'classification', or 'regression'.

        Returns:
            Dictionary of available metrics by type.
        """
        if model_type == "classification":
            return {"classification": list(self.CLASSIFICATION_METRICS.keys())}
        elif model_type == "regression":
            return {"regression": list(self.REGRESSION_METRICS.keys())}
        else:
            return {
                "classification": list(self.CLASSIFICATION_METRICS.keys()),
                "regression": list(self.REGRESSION_METRICS.keys()),
            }
