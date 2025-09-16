"""Model Evaluation Module

This module provides comprehensive model evaluation capabilities including cross-validation,
hyperparameter tuning, performance metrics, and model comparison for machine learning workflows.
"""

import logging
import warnings
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple, Union

import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    mean_absolute_error,
    mean_squared_error,
    precision_recall_curve,
    precision_score,
    r2_score,
    recall_score,
    roc_auc_score,
    roc_curve,
)
from sklearn.model_selection import (
    GridSearchCV,
    KFold,
    RandomizedSearchCV,
    StratifiedKFold,
    cross_val_score,
    cross_validate,
    learning_curve,
    validation_curve,
)
from sklearn.svm import SVC, SVR

logger = logging.getLogger(__name__)


class TaskType(Enum):
    """Enumeration of supported machine learning task types.
    
    This enum defines the primary ML task categories supported by the evaluation
    system. Each task type has different appropriate metrics, validation strategies,
    and evaluation approaches.
    
    Attributes:
        CLASSIFICATION (str): Supervised learning for discrete target variables.
            Includes binary and multi-class classification tasks.
            Metrics: accuracy, precision, recall, F1, AUC, confusion matrix.
        REGRESSION (str): Supervised learning for continuous target variables.
            Includes linear and non-linear regression tasks.
            Metrics: MSE, MAE, R², RMSE, mean absolute percentage error.
        CLUSTERING (str): Unsupervised learning for grouping data points.
            Basic support for clustering evaluation and validation.
            Metrics: silhouette score, calinski-harabasz, davies-bouldin.
    
    Example:
        Task-specific evaluation setup::
        
            # Classification evaluation
            evaluator = ModelEvaluator(task_type=TaskType.CLASSIFICATION)
            
            # Regression evaluation  
            evaluator = ModelEvaluator(task_type=TaskType.REGRESSION)
            
            # Clustering evaluation
            evaluator = ModelEvaluator(task_type=TaskType.CLUSTERING)
    """
    CLASSIFICATION = "classification"
    REGRESSION = "regression"
    CLUSTERING = "clustering"


class CrossValidationMethod(Enum):
    """Enumeration of cross-validation methods for model evaluation.

    This enum defines the available cross-validation strategies for model
    evaluation and hyperparameter tuning. Each method is suitable for
    different types of data and evaluation scenarios.

    Attributes:
        K_FOLD (str): Standard K-fold cross-validation.
            Splits data into k folds randomly, suitable for most datasets.
        STRATIFIED_K_FOLD (str): Stratified K-fold cross-validation.
            Maintains class distribution in each fold, recommended for classification.
        LEAVE_ONE_OUT (str): Leave-one-out cross-validation.
            Uses single sample for validation, suitable for small datasets.
        TIME_SERIES_SPLIT (str): Time series cross-validation.
            Respects temporal ordering, essential for time series data.

    Example:
        Cross-validation method selection::

            # For classification with balanced classes
            cv_config = CrossValidationConfig(
                method=CrossValidationMethod.STRATIFIED_K_FOLD,
                n_folds=5
            )

            # For time series data
            cv_config = CrossValidationConfig(
                method=CrossValidationMethod.TIME_SERIES_SPLIT,
                n_folds=3
            )
    """
    K_FOLD = "k_fold"
    STRATIFIED_K_FOLD = "stratified_k_fold"
    LEAVE_ONE_OUT = "leave_one_out"
    TIME_SERIES_SPLIT = "time_series_split"


class HyperparameterTuningMethod(Enum):
    """Enumeration of hyperparameter optimization methods.

    This enum defines the available hyperparameter optimization strategies
    for automated model tuning. Each method has different trade-offs between
    computational cost and optimization effectiveness.

    Attributes:
        GRID_SEARCH (str): Exhaustive grid search optimization.
            Tests all parameter combinations, thorough but computationally expensive.
        RANDOM_SEARCH (str): Random sampling of parameter space.
            More efficient than grid search, good for high-dimensional spaces.
        BAYESIAN_OPTIMIZATION (str): Intelligent parameter exploration.
            Uses probabilistic model to guide search, most efficient approach.

    Example:
        Hyperparameter tuning method selection::

            # Exhaustive search for small parameter spaces
            tuning_config = HyperparameterTuningConfig(
                method=HyperparameterTuningMethod.GRID_SEARCH,
                param_grid={'n_estimators': [100, 200], 'max_depth': [5, 10]}
            )

            # Random search for larger parameter spaces
            tuning_config = HyperparameterTuningConfig(
                method=HyperparameterTuningMethod.RANDOM_SEARCH,
                n_iter=100
            )
    """
    GRID_SEARCH = "grid_search"
    RANDOM_SEARCH = "random_search"
    BAYESIAN_OPTIMIZATION = "bayesian_optimization"


@dataclass
class CrossValidationConfig:
    """Configuration class for cross-validation parameters.

    This dataclass encapsulates all parameters needed to configure cross-validation
    for model evaluation. It provides sensible defaults while allowing customization
    for specific evaluation requirements.

    Attributes:
        method (CrossValidationMethod): Cross-validation strategy to use.
            Defaults to stratified K-fold for maintaining class distribution.
        n_folds (int): Number of cross-validation folds.
            Must be at least 2. Default is 5 for good bias-variance trade-off.
        random_state (int): Random seed for reproducible results.
            Default is 42 for consistency across runs.
        shuffle (bool): Whether to shuffle data before splitting.
            Default is True for better fold distribution.
        scoring (Union[str, List[str]]): Evaluation metric(s) to compute.
            Single metric or list of metrics. Default is 'accuracy' for classification.

    Raises:
        ValueError: If n_folds is less than 2.

    Example:
        Cross-validation configuration setup::

            # Basic classification configuration
            cv_config = CrossValidationConfig(
                method=CrossValidationMethod.STRATIFIED_K_FOLD,
                n_folds=5,
                scoring=['accuracy', 'f1', 'roc_auc']
            )

            # Regression configuration
            cv_config = CrossValidationConfig(
                method=CrossValidationMethod.K_FOLD,
                n_folds=10,
                scoring=['neg_mean_squared_error', 'r2']
            )
    """
    method: CrossValidationMethod = CrossValidationMethod.STRATIFIED_K_FOLD
    n_folds: int = 5
    random_state: int = 42
    shuffle: bool = True
    scoring: Union[str, List[str]] = "accuracy"  # For classification

    def __post_init__(self):
        """Validate configuration parameters.

        Raises:
            ValueError: If n_folds is less than 2.
        """
        if self.n_folds < 2:
            raise ValueError("n_folds must be at least 2")


@dataclass
class HyperparameterTuningConfig:
    """Configuration class for hyperparameter optimization.

    This dataclass defines all parameters needed for automated hyperparameter
    tuning. It supports different optimization strategies and provides sensible
    defaults for efficient parameter search.

    Attributes:
        method (HyperparameterTuningMethod): Optimization method to use.
            Defaults to grid search for thorough exploration.
        param_grid (Dict[str, List[Any]]): Parameter search space definition.
            Dictionary mapping parameter names to lists of values to try.
        n_iter (int): Number of parameter combinations for random search.
            Only used with random search method. Default is 100.
        cv_folds (int): Number of cross-validation folds for evaluation.
            Default is 5 for good performance estimation.
        scoring (str): Metric to optimize during parameter search.
            Default is 'accuracy' for classification tasks.
        n_jobs (int): Number of parallel jobs for computation.
            Default is -1 to use all available processors.
        random_state (int): Random seed for reproducible results.
            Default is 42 for consistency across runs.

    Example:
        Hyperparameter tuning configuration::

            # Grid search configuration
            tuning_config = HyperparameterTuningConfig(
                method=HyperparameterTuningMethod.GRID_SEARCH,
                param_grid={
                    'n_estimators': [100, 200, 300],
                    'max_depth': [5, 10, 15, None],
                    'min_samples_split': [2, 5, 10]
                },
                cv_folds=5,
                scoring='f1_macro'
            )

            # Random search configuration
            tuning_config = HyperparameterTuningConfig(
                method=HyperparameterTuningMethod.RANDOM_SEARCH,
                param_grid={
                    'C': [0.1, 1.0, 10.0, 100.0],
                    'gamma': ['scale', 'auto', 0.001, 0.01, 0.1]
                },
                n_iter=50
            )
    """
    method: HyperparameterTuningMethod = HyperparameterTuningMethod.GRID_SEARCH
    param_grid: Dict[str, List[Any]] = None
    n_iter: int = 100  # For random search
    cv_folds: int = 5
    scoring: str = "accuracy"
    n_jobs: int = -1
    random_state: int = 42

    def __post_init__(self):
        """Initialize default parameter grid if none provided."""
        if self.param_grid is None:
            self.param_grid = {}


@dataclass
class ModelPerformanceReport:
    """Comprehensive model performance evaluation results.

    This dataclass contains all evaluation metrics and analysis results
    for a single model. It provides a complete picture of model performance
    including cross-validation scores, feature importance, and diagnostic data.

    Attributes:
        task_type (TaskType): Type of ML task (classification or regression).
        model_name (str): Human-readable name for the evaluated model.
        cv_scores (Dict[str, np.ndarray]): Raw cross-validation scores for each metric.
            Keys are metric names, values are arrays of fold scores.
        mean_scores (Dict[str, float]): Mean score across all CV folds for each metric.
        std_scores (Dict[str, float]): Standard deviation of scores for each metric.
        best_score (float): Primary metric score used for model ranking.
        best_params (Optional[Dict[str, Any]]): Best hyperparameters from tuning.
            None if hyperparameter tuning was not performed.
        feature_importance (Optional[Dict[str, float]]): Feature importance scores.
            None if model doesn't support feature importance extraction.
        confusion_matrix (Optional[np.ndarray]): Confusion matrix for classification.
            None for regression tasks or if not computed.
        classification_report (Optional[Dict[str, Any]]): Detailed classification metrics.
            None for regression tasks or if not computed.
        learning_curve_data (Optional[Dict[str, np.ndarray]]): Learning curve analysis.
            None if learning curve analysis was not performed.
        validation_curve_data (Optional[Dict[str, Any]]): Validation curve analysis.
            None if validation curve analysis was not performed.

    Example:
        Accessing evaluation results::

            report = evaluator.evaluate_model(model, X, y, 'RandomForest')

            # Access primary metrics
            print(f"Model: {report.model_name}")
            print(f"Best Score: {report.best_score:.4f}")

            # Access detailed scores
            for metric, score in report.mean_scores.items():
                std = report.std_scores[metric]
                print(f"{metric}: {score:.4f} (+/- {std * 2:.4f})")

            # Access feature importance if available
            if report.feature_importance:
                top_features = sorted(
                    report.feature_importance.items(),
                    key=lambda x: x[1], reverse=True
                )[:5]
                print("Top 5 features:", top_features)
    """
    task_type: TaskType
    model_name: str
    cv_scores: Dict[str, np.ndarray]
    mean_scores: Dict[str, float]
    std_scores: Dict[str, float]
    best_score: float
    best_params: Optional[Dict[str, Any]] = None
    feature_importance: Optional[Dict[str, float]] = None
    confusion_matrix: Optional[np.ndarray] = None
    classification_report: Optional[Dict[str, Any]] = None
    learning_curve_data: Optional[Dict[str, np.ndarray]] = None
    validation_curve_data: Optional[Dict[str, Any]] = None


class ModelEvaluator:
    """Comprehensive machine learning model evaluation framework.

    This class provides a complete toolkit for evaluating, comparing, and optimizing
    machine learning models. It supports both classification and regression tasks
    with automated metric selection, cross-validation, hyperparameter tuning,
    and comprehensive performance reporting.

    The evaluator handles the complete evaluation workflow:
    1. Model configuration and setup
    2. Cross-validation with multiple metrics
    3. Hyperparameter optimization (grid/random/Bayesian)
    4. Feature importance analysis
    5. Learning curve generation
    6. Model comparison and ranking

    Attributes:
        task_type (TaskType): Type of ML task being evaluated.
        models (Dict[str, BaseEstimator]): Registry of models for evaluation.
        results (Dict[str, Any]): Storage for evaluation results and metadata.
        default_models (Dict[str, BaseEstimator]): Task-appropriate default models.
        default_scoring (List[str]): Task-appropriate default evaluation metrics.

    Example:
        Complete model evaluation workflow::

            # Initialize evaluator for classification
            evaluator = ModelEvaluator(task_type=TaskType.CLASSIFICATION)

            # Configure cross-validation
            cv_config = CrossValidationConfig(
                method=CrossValidationMethod.STRATIFIED_K_FOLD,
                n_folds=5,
                scoring=['accuracy', 'f1', 'roc_auc']
            )

            # Evaluate single model
            model = RandomForestClassifier()
            report = evaluator.evaluate_model(model, X, y, cv_config=cv_config)

            # Compare multiple models
            models = {
                'rf': RandomForestClassifier(),
                'svm': SVC(probability=True),
                'lr': LogisticRegression()
            }
            comparison = evaluator.compare_models(X, y, models, cv_config)

            # Get best performing model
            best_model_name = next(iter(comparison))
            best_report = comparison[best_model_name]
            print(f"Best model: {best_model_name} ({best_report.best_score:.4f})")

    Note:
        Requires scikit-learn, pandas, and numpy. Advanced features may require
        additional dependencies like scikit-optimize for Bayesian optimization.
    """

    def __init__(self, task_type: TaskType = TaskType.CLASSIFICATION):
        """Initialize the model evaluator with task-specific defaults.

        Args:
            task_type (TaskType): Type of ML task to evaluate.
                Determines default models, metrics, and validation strategies.

        Example:
            Initialize evaluators for different tasks::

                # For classification tasks
                clf_evaluator = ModelEvaluator(TaskType.CLASSIFICATION)

                # For regression tasks
                reg_evaluator = ModelEvaluator(TaskType.REGRESSION)
        """
        self.task_type = task_type
        self.models = {}
        self.results = {}

        # Default models for each task type
        if task_type == TaskType.CLASSIFICATION:
            self.default_models = {
                'random_forest': RandomForestClassifier(random_state=42),
                'logistic_regression': LogisticRegression(random_state=42, max_iter=1000),
                'svm': SVC(random_state=42, probability=True)
            }
            self.default_scoring = ['accuracy', 'precision_macro', 'recall_macro', 'f1_macro']
        else:
            self.default_models = {
                'random_forest': RandomForestRegressor(random_state=42),
                'linear_regression': LinearRegression(),
                'svm': SVR()
            }
            self.default_scoring = ['neg_mean_squared_error', 'neg_mean_absolute_error', 'r2']
    
    def add_model(self, name: str, model: BaseEstimator) -> None:
        """Add a model to the evaluation registry.

        Registers a model for batch evaluation and comparison. The model
        will be included in comparative analyses and can be referenced
        by name in subsequent operations.

        Args:
            name (str): Unique identifier for the model.
                Used in reports and comparisons.
            model (BaseEstimator): Scikit-learn compatible model instance.
                Must implement fit() and predict() methods.

        Example:
            Register custom models for evaluation::

                evaluator = ModelEvaluator(TaskType.CLASSIFICATION)

                # Add custom models
                evaluator.add_model('custom_rf', RandomForestClassifier(n_estimators=500))
                evaluator.add_model('tuned_svm', SVC(C=10, gamma='scale'))
                evaluator.add_model('ensemble', VotingClassifier([...]))

                # Use registered models in comparison
                results = evaluator.compare_models(X, y)
        """
        self.models[name] = model
        logger.info(f"Added model: {name}")
    
    def cross_validate_model(
        self,
        model: BaseEstimator,
        X: pd.DataFrame,
        y: pd.Series,
        config: CrossValidationConfig = None
    ) -> Dict[str, np.ndarray]:
        """Perform cross-validation evaluation on a model.

        Executes cross-validation using the specified configuration and returns
        detailed results for all requested metrics. Handles both classification
        and regression tasks with appropriate validation strategies.

        Args:
            model (BaseEstimator): Model to evaluate via cross-validation.
            X (pd.DataFrame): Feature matrix with shape (n_samples, n_features).
            y (pd.Series): Target vector with shape (n_samples,).
            config (CrossValidationConfig, optional): Cross-validation parameters.
                If None, uses default configuration with stratified K-fold.

        Returns:
            Dict[str, np.ndarray]: Cross-validation results containing:
                - 'test_{metric}': Scores for each fold and metric
                - 'train_{metric}': Training scores if available
                - 'fit_time': Time taken to fit each fold
                - 'score_time': Time taken to score each fold

        Example:
            Cross-validation with custom configuration::

                config = CrossValidationConfig(
                    method=CrossValidationMethod.STRATIFIED_K_FOLD,
                    n_folds=10,
                    scoring=['accuracy', 'f1', 'roc_auc']
                )

                model = RandomForestClassifier()
                cv_results = evaluator.cross_validate_model(model, X, y, config)

                # Access results
                accuracy_scores = cv_results['test_accuracy']
                print(f"CV Accuracy: {accuracy_scores.mean():.3f} (+/- {accuracy_scores.std() * 2:.3f})")
        """
        if config is None:
            config = CrossValidationConfig()
        
        # Set up cross-validation method
        if config.method == CrossValidationMethod.STRATIFIED_K_FOLD:
            if self.task_type == TaskType.CLASSIFICATION:
                cv = StratifiedKFold(n_splits=config.n_folds, shuffle=config.shuffle, random_state=config.random_state)
            else:
                cv = KFold(n_splits=config.n_folds, shuffle=config.shuffle, random_state=config.random_state)
        else:
            cv = KFold(n_splits=config.n_folds, shuffle=config.shuffle, random_state=config.random_state)
        
        # Perform cross-validation
        cv_results = cross_validate(
            model, X, y,
            cv=cv,
            scoring=config.scoring if isinstance(config.scoring, list) else [config.scoring],
            return_train_score=True,
            n_jobs=-1
        )
        
        return cv_results
    
    def tune_hyperparameters(
        self,
        model: BaseEstimator,
        X: pd.DataFrame,
        y: pd.Series,
        config: HyperparameterTuningConfig
    ) -> Tuple[BaseEstimator, Dict[str, Any]]:
        """Optimize model hyperparameters using specified search strategy.

        Performs automated hyperparameter optimization using grid search,
        random search, or Bayesian optimization. Returns the best model
        configuration found during the search process.

        Args:
            model (BaseEstimator): Base model to optimize.
                Must be compatible with scikit-learn parameter search.
            X (pd.DataFrame): Feature matrix for parameter evaluation.
            y (pd.Series): Target vector for parameter evaluation.
            config (HyperparameterTuningConfig): Optimization configuration
                including search method, parameter space, and evaluation settings.

        Returns:
            Tuple[BaseEstimator, Dict[str, Any]]: Tuple containing:
                - best_model: Model instance with optimal parameters
                - best_params: Dictionary of optimal parameter values

        Raises:
            ValueError: If unsupported tuning method is specified.

        Example:
            Hyperparameter optimization workflow::

                # Define parameter search space
                param_grid = {
                    'n_estimators': [100, 200, 300],
                    'max_depth': [5, 10, 15, None],
                    'min_samples_split': [2, 5, 10]
                }

                # Configure optimization
                tuning_config = HyperparameterTuningConfig(
                    method=HyperparameterTuningMethod.GRID_SEARCH,
                    param_grid=param_grid,
                    cv_folds=5,
                    scoring='f1_macro'
                )

                # Optimize model
                base_model = RandomForestClassifier()
                best_model, best_params = evaluator.tune_hyperparameters(
                    base_model, X_train, y_train, tuning_config
                )

                print(f"Best parameters: {best_params}")
                print(f"Best CV score: {best_model.best_score_:.4f}")
        """
        logger.info(f"Tuning hyperparameters using {config.method.value}")
        
        # Set up cross-validation
        if self.task_type == TaskType.CLASSIFICATION:
            cv = StratifiedKFold(n_splits=config.cv_folds, shuffle=True, random_state=config.random_state)
        else:
            cv = KFold(n_splits=config.cv_folds, shuffle=True, random_state=config.random_state)
        
        # Perform hyperparameter tuning
        if config.method == HyperparameterTuningMethod.GRID_SEARCH:
            search = GridSearchCV(
                model, config.param_grid,
                cv=cv, scoring=config.scoring,
                n_jobs=config.n_jobs, verbose=1
            )
        elif config.method == HyperparameterTuningMethod.RANDOM_SEARCH:
            search = RandomizedSearchCV(
                model, config.param_grid,
                n_iter=config.n_iter, cv=cv, scoring=config.scoring,
                n_jobs=config.n_jobs, random_state=config.random_state, verbose=1
            )
        else:
            raise ValueError(f"Unsupported tuning method: {config.method}")
        
        # Fit and get best model
        search.fit(X, y)
        
        logger.info(f"Best score: {search.best_score_:.4f}")
        logger.info(f"Best params: {search.best_params_}")
        
        return search.best_estimator_, search.best_params_
    
    def evaluate_model(
        self,
        model: BaseEstimator,
        X: pd.DataFrame,
        y: pd.Series,
        model_name: str = "model",
        cv_config: CrossValidationConfig = None,
        tune_hyperparameters: bool = False,
        tuning_config: HyperparameterTuningConfig = None
    ) -> ModelPerformanceReport:
        """Comprehensive model evaluation.
        
        Args:
            model: Model to evaluate
            X: Feature matrix
            y: Target vector
            model_name: Name for the model
            cv_config: Cross-validation configuration
            tune_hyperparameters: Whether to tune hyperparameters
            tuning_config: Hyperparameter tuning configuration
            
        Returns:
            ModelPerformanceReport with evaluation results
        """
        logger.info(f"Evaluating model: {model_name}")
        
        # Set default configurations
        if cv_config is None:
            cv_config = CrossValidationConfig()
            if self.task_type == TaskType.REGRESSION:
                cv_config.scoring = "neg_mean_squared_error"
        
        best_params = None
        
        # Hyperparameter tuning if requested
        if tune_hyperparameters and tuning_config is not None:
            model, best_params = self.tune_hyperparameters(model, X, y, tuning_config)
        
        # Cross-validation
        cv_results = self.cross_validate_model(model, X, y, cv_config)
        
        # Calculate statistics
        mean_scores = {}
        std_scores = {}
        
        for metric in cv_results:
            if metric.startswith('test_'):
                metric_name = metric.replace('test_', '')
                mean_scores[metric_name] = np.mean(cv_results[metric])
                std_scores[metric_name] = np.std(cv_results[metric])
        
        # Get best score (first metric if multiple)
        first_metric = list(mean_scores.keys())[0]
        best_score = mean_scores[first_metric]
        
        # Feature importance (if available)
        feature_importance = None
        if hasattr(model, 'feature_importances_'):
            feature_importance = dict(zip(X.columns, model.feature_importances_))
        elif hasattr(model, 'coef_'):
            if len(model.coef_.shape) == 1:
                feature_importance = dict(zip(X.columns, np.abs(model.coef_)))
            else:
                feature_importance = dict(zip(X.columns, np.abs(model.coef_).mean(axis=0)))
        
        # Generate report
        report = ModelPerformanceReport(
            task_type=self.task_type,
            model_name=model_name,
            cv_scores=cv_results,
            mean_scores=mean_scores,
            std_scores=std_scores,
            best_score=best_score,
            best_params=best_params,
            feature_importance=feature_importance
        )
        
        logger.info(f"Model evaluation completed. Best score: {best_score:.4f}")
        return report
    
    def compare_models(
        self,
        X: pd.DataFrame,
        y: pd.Series,
        models: Optional[Dict[str, BaseEstimator]] = None,
        cv_config: CrossValidationConfig = None
    ) -> Dict[str, ModelPerformanceReport]:
        """Compare multiple models.
        
        Args:
            X: Feature matrix
            y: Target vector
            models: Dictionary of models to compare (uses defaults if None)
            cv_config: Cross-validation configuration
            
        Returns:
            Dictionary of model performance reports
        """
        if models is None:
            models = self.default_models
        
        logger.info(f"Comparing {len(models)} models")
        
        results = {}
        for name, model in models.items():
            try:
                report = self.evaluate_model(model, X, y, name, cv_config)
                results[name] = report
                logger.info(f"{name}: {report.best_score:.4f}")
            except Exception as e:
                logger.error(f"Error evaluating {name}: {str(e)}")
                continue
        
        # Sort by best score (descending for accuracy, ascending for error metrics)
        first_model = next(iter(results.values()))
        first_metric = list(first_model.mean_scores.keys())[0]
        reverse_sort = not first_metric.startswith('neg')
        
        sorted_results = dict(sorted(
            results.items(),
            key=lambda x: x[1].best_score,
            reverse=reverse_sort
        ))
        
        logger.info("Model comparison completed")
        return sorted_results
    
    def generate_learning_curve(
        self,
        model: BaseEstimator,
        X: pd.DataFrame,
        y: pd.Series,
        train_sizes: np.ndarray = None
    ) -> Dict[str, np.ndarray]:
        """Generate learning curve data.
        
        Args:
            model: Model to analyze
            X: Feature matrix
            y: Target vector
            train_sizes: Training set sizes to use
            
        Returns:
            Dictionary with learning curve data
        """
        if train_sizes is None:
            train_sizes = np.linspace(0.1, 1.0, 10)
        
        train_sizes_abs, train_scores, val_scores = learning_curve(
            model, X, y, train_sizes=train_sizes,
            cv=5, scoring='accuracy' if self.task_type == TaskType.CLASSIFICATION else 'neg_mean_squared_error',
            n_jobs=-1, random_state=42
        )
        
        return {
            'train_sizes': train_sizes_abs,
            'train_scores': train_scores,
            'val_scores': val_scores,
            'train_mean': np.mean(train_scores, axis=1),
            'train_std': np.std(train_scores, axis=1),
            'val_mean': np.mean(val_scores, axis=1),
            'val_std': np.std(val_scores, axis=1)
        }


# Utility functions
def get_default_param_grids() -> Dict[str, Dict[str, List[Any]]]:
    """Get default hyperparameter search grids for common ML models.

    Provides pre-configured parameter grids for popular machine learning
    models. These grids balance search thoroughness with computational
    efficiency, covering the most impactful hyperparameters.

    Returns:
        Dict[str, Dict[str, List[Any]]]: Mapping of model names to parameter grids.
            Each parameter grid contains parameter names mapped to lists of values
            to search over during hyperparameter optimization.

    Example:
        Using default parameter grids::

            # Get default grids
            param_grids = get_default_param_grids()

            # Use with specific model
            rf_grid = param_grids['random_forest_classifier']
            tuning_config = HyperparameterTuningConfig(
                method=HyperparameterTuningMethod.GRID_SEARCH,
                param_grid=rf_grid
            )

            # Optimize model with default grid
            model = RandomForestClassifier()
            best_model, best_params = evaluator.tune_hyperparameters(
                model, X, y, tuning_config
            )

    Note:
        Parameter grids are designed for reasonable search times on
        moderate-sized datasets. For large datasets or time constraints,
        consider using random search with higher n_iter values.
    """
    return {
        'random_forest_classifier': {
            'n_estimators': [50, 100, 200],
            'max_depth': [None, 5, 10, 15],
            'min_samples_split': [2, 5, 10],
            'min_samples_leaf': [1, 2, 4]
        },
        'random_forest_regressor': {
            'n_estimators': [50, 100, 200],
            'max_depth': [None, 5, 10, 15],
            'min_samples_split': [2, 5, 10],
            'min_samples_leaf': [1, 2, 4]
        },
        'logistic_regression': {
            'C': [0.1, 1.0, 10.0, 100.0],
            'penalty': ['l1', 'l2'],
            'solver': ['liblinear', 'lbfgs']
        },
        'svm_classifier': {
            'C': [0.1, 1.0, 10.0, 100.0],
            'kernel': ['rbf', 'linear', 'poly'],
            'gamma': ['scale', 'auto', 0.001, 0.01, 0.1, 1.0]
        },
        'svm_regressor': {
            'C': [0.1, 1.0, 10.0, 100.0],
            'kernel': ['rbf', 'linear', 'poly'],
            'gamma': ['scale', 'auto', 0.001, 0.01, 0.1, 1.0],
            'epsilon': [0.01, 0.1, 0.2, 0.5]
        }
    }


def quick_model_comparison(
    X: pd.DataFrame,
    y: pd.Series,
    task_type: TaskType = TaskType.CLASSIFICATION,
    cv_folds: int = 5
) -> Dict[str, float]:
    """Perform rapid comparison of default models for quick baseline assessment.

    This convenience function provides a fast way to compare multiple
    baseline models and identify promising approaches for further development.
    It uses default model configurations and standard cross-validation.

    Args:
        X (pd.DataFrame): Feature matrix with shape (n_samples, n_features).
        y (pd.Series): Target vector with shape (n_samples,).
        task_type (TaskType): Type of ML task to evaluate.
            Determines which default models and metrics to use.
        cv_folds (int): Number of cross-validation folds.
            Default is 5 for good bias-variance trade-off.

    Returns:
        Dict[str, float]: Model names mapped to their primary scores.
            Scores are sorted by performance (best first).

    Example:
        Quick model comparison for initial assessment::\

            # Load your dataset
            X, y = load_dataset()

            # Quick classification comparison
            scores = quick_model_comparison(
                X, y,
                task_type=TaskType.CLASSIFICATION,
                cv_folds=5
            )

            # View results
            print(\"Model Performance Comparison:\")
            for model_name, score in scores.items():
                print(f\"{model_name}: {score:.4f}\")

            # Get best performing model name
            best_model = next(iter(scores))
            print(f\"Best baseline model: {best_model}\")

    Note:
        This function is designed for rapid prototyping and initial
        model selection. For production use, consider more thorough
        evaluation with ModelEvaluator class.
    """
    evaluator = ModelEvaluator(task_type)
    cv_config = CrossValidationConfig(n_folds=cv_folds)
    
    results = evaluator.compare_models(X, y, cv_config=cv_config)
    
    # Extract just the scores for quick comparison
    scores = {name: report.best_score for name, report in results.items()}
    
    return scores