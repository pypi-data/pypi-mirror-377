"""
Unit tests for model evaluation functionality.
"""

from unittest.mock import Mock, patch

import numpy as np
import pandas as pd
import pytest
from sklearn.datasets import make_classification, make_regression
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.svm import SVC, SVR

from mcp_ds_toolkit_server.data.model_evaluation import (
    CrossValidationConfig,
    CrossValidationMethod,
    HyperparameterTuningConfig,
    HyperparameterTuningMethod,
    ModelEvaluator,
    ModelPerformanceReport,
    TaskType,
    get_default_param_grids,
    quick_model_comparison,
)


class TestModelEvaluator:
    """Test model evaluation functionality."""
    
    @pytest.fixture
    def classification_data(self):
        """Create sample classification data."""
        X, y = make_classification(
            n_samples=100, n_features=10, n_classes=3,
            n_informative=8, n_redundant=2, random_state=42
        )
        X_df = pd.DataFrame(X, columns=[f'feature_{i}' for i in range(10)])
        y_series = pd.Series(y, name='target')
        return X_df, y_series
    
    @pytest.fixture
    def regression_data(self):
        """Create sample regression data."""
        X, y = make_regression(
            n_samples=100, n_features=10, noise=0.1, random_state=42
        )
        X_df = pd.DataFrame(X, columns=[f'feature_{i}' for i in range(10)])
        y_series = pd.Series(y, name='target')
        return X_df, y_series
    
    def test_evaluator_initialization_classification(self):
        """Test ModelEvaluator initialization for classification."""
        evaluator = ModelEvaluator(TaskType.CLASSIFICATION)
        
        assert evaluator.task_type == TaskType.CLASSIFICATION
        assert 'random_forest' in evaluator.default_models
        assert isinstance(evaluator.default_models['random_forest'], RandomForestClassifier)
        assert 'accuracy' in evaluator.default_scoring
        
    def test_evaluator_initialization_regression(self):
        """Test ModelEvaluator initialization for regression."""
        evaluator = ModelEvaluator(TaskType.REGRESSION)
        
        assert evaluator.task_type == TaskType.REGRESSION
        assert 'random_forest' in evaluator.default_models
        assert isinstance(evaluator.default_models['random_forest'], RandomForestRegressor)
        assert 'neg_mean_squared_error' in evaluator.default_scoring
    
    def test_add_model(self):
        """Test adding custom models."""
        evaluator = ModelEvaluator(TaskType.CLASSIFICATION)
        custom_model = LogisticRegression(random_state=42)
        
        evaluator.add_model('custom_lr', custom_model)
        
        assert 'custom_lr' in evaluator.models
        assert evaluator.models['custom_lr'] == custom_model
    
    def test_cross_validate_model_classification(self, classification_data):
        """Test cross-validation for classification."""
        X, y = classification_data
        evaluator = ModelEvaluator(TaskType.CLASSIFICATION)
        model = RandomForestClassifier(random_state=42, n_estimators=10)
        
        config = CrossValidationConfig(
            method=CrossValidationMethod.STRATIFIED_K_FOLD,
            n_folds=3,
            scoring=['accuracy', 'f1_macro']
        )
        
        results = evaluator.cross_validate_model(model, X, y, config)
        
        assert 'test_accuracy' in results
        assert 'test_f1_macro' in results
        assert len(results['test_accuracy']) == 3
        assert all(0 <= score <= 1 for score in results['test_accuracy'])
    
    def test_cross_validate_model_regression(self, regression_data):
        """Test cross-validation for regression."""
        X, y = regression_data
        evaluator = ModelEvaluator(TaskType.REGRESSION)
        model = RandomForestRegressor(random_state=42, n_estimators=10)
        
        config = CrossValidationConfig(
            method=CrossValidationMethod.K_FOLD,
            n_folds=3,
            scoring=['neg_mean_squared_error', 'r2']
        )
        
        results = evaluator.cross_validate_model(model, X, y, config)
        
        assert 'test_neg_mean_squared_error' in results
        assert 'test_r2' in results
        assert len(results['test_neg_mean_squared_error']) == 3
    
    def test_tune_hyperparameters_grid_search(self, classification_data):
        """Test hyperparameter tuning with grid search."""
        X, y = classification_data
        evaluator = ModelEvaluator(TaskType.CLASSIFICATION)
        model = RandomForestClassifier(random_state=42)
        
        config = HyperparameterTuningConfig(
            method=HyperparameterTuningMethod.GRID_SEARCH,
            param_grid={'n_estimators': [5, 10], 'max_depth': [3, 5]},
            cv_folds=3,
            scoring='accuracy'
        )
        
        best_model, best_params = evaluator.tune_hyperparameters(model, X, y, config)
        
        assert best_params is not None
        assert 'n_estimators' in best_params
        assert 'max_depth' in best_params
        assert best_params['n_estimators'] in [5, 10]
        assert best_params['max_depth'] in [3, 5]
    
    def test_tune_hyperparameters_random_search(self, classification_data):
        """Test hyperparameter tuning with random search."""
        X, y = classification_data
        evaluator = ModelEvaluator(TaskType.CLASSIFICATION)
        model = RandomForestClassifier(random_state=42)
        
        config = HyperparameterTuningConfig(
            method=HyperparameterTuningMethod.RANDOM_SEARCH,
            param_grid={'n_estimators': [5, 10, 15], 'max_depth': [3, 5, 7]},
            n_iter=4,
            cv_folds=3,
            scoring='accuracy'
        )
        
        best_model, best_params = evaluator.tune_hyperparameters(model, X, y, config)
        
        assert best_params is not None
        assert 'n_estimators' in best_params
        assert 'max_depth' in best_params
    
    def test_evaluate_model_comprehensive(self, classification_data):
        """Test comprehensive model evaluation."""
        X, y = classification_data
        evaluator = ModelEvaluator(TaskType.CLASSIFICATION)
        model = RandomForestClassifier(random_state=42, n_estimators=10)
        
        cv_config = CrossValidationConfig(n_folds=3)
        tuning_config = HyperparameterTuningConfig(
            param_grid={'max_depth': [3, 5]},
            cv_folds=2
        )
        
        report = evaluator.evaluate_model(
            model=model,
            X=X,
            y=y,
            model_name='test_rf',
            cv_config=cv_config,
            tune_hyperparameters=True,
            tuning_config=tuning_config
        )
        
        assert isinstance(report, ModelPerformanceReport)
        assert report.model_name == 'test_rf'
        assert report.task_type == TaskType.CLASSIFICATION
        assert report.best_params is not None
        assert 'accuracy' in report.mean_scores
        assert report.feature_importance is not None
        assert len(report.feature_importance) == 10  # 10 features
    
    def test_compare_models_classification(self, classification_data):
        """Test model comparison for classification."""
        X, y = classification_data
        evaluator = ModelEvaluator(TaskType.CLASSIFICATION)
        
        models = {
            'rf': RandomForestClassifier(random_state=42, n_estimators=5),
            'lr': LogisticRegression(random_state=42, max_iter=100)
        }
        
        cv_config = CrossValidationConfig(n_folds=3)
        results = evaluator.compare_models(X, y, models, cv_config)
        
        assert len(results) == 2
        assert 'rf' in results
        assert 'lr' in results
        
        for name, report in results.items():
            assert isinstance(report, ModelPerformanceReport)
            assert report.model_name == name
            assert 'accuracy' in report.mean_scores
    
    def test_compare_models_default(self, classification_data):
        """Test model comparison with default models."""
        X, y = classification_data
        evaluator = ModelEvaluator(TaskType.CLASSIFICATION)
        
        cv_config = CrossValidationConfig(n_folds=2)  # Smaller for speed
        results = evaluator.compare_models(X, y, cv_config=cv_config)
        
        assert len(results) >= 2  # At least random_forest and logistic_regression
        
        # Results should be sorted by score
        scores = [report.best_score for report in results.values()]
        assert scores == sorted(scores, reverse=True)
    
    def test_generate_learning_curve(self, classification_data):
        """Test learning curve generation."""
        X, y = classification_data
        evaluator = ModelEvaluator(TaskType.CLASSIFICATION)
        model = RandomForestClassifier(random_state=42, n_estimators=5)
        
        train_sizes = np.array([0.3, 0.6, 1.0])
        curve_data = evaluator.generate_learning_curve(model, X, y, train_sizes)
        
        assert 'train_sizes' in curve_data
        assert 'train_scores' in curve_data
        assert 'val_scores' in curve_data
        assert 'train_mean' in curve_data
        assert 'train_std' in curve_data
        assert 'val_mean' in curve_data
        assert 'val_std' in curve_data
        
        assert len(curve_data['train_mean']) == 3
        assert len(curve_data['val_mean']) == 3


class TestCrossValidationConfig:
    """Test cross-validation configuration."""
    
    def test_default_config(self):
        """Test default configuration."""
        config = CrossValidationConfig()
        
        assert config.method == CrossValidationMethod.STRATIFIED_K_FOLD
        assert config.n_folds == 5
        assert config.random_state == 42
        assert config.shuffle is True
        assert config.scoring == "accuracy"
    
    def test_custom_config(self):
        """Test custom configuration."""
        config = CrossValidationConfig(
            method=CrossValidationMethod.K_FOLD,
            n_folds=10,
            random_state=123,
            scoring=['precision', 'recall']
        )
        
        assert config.method == CrossValidationMethod.K_FOLD
        assert config.n_folds == 10
        assert config.random_state == 123
        assert config.scoring == ['precision', 'recall']
    
    def test_invalid_n_folds(self):
        """Test validation of n_folds."""
        with pytest.raises(ValueError, match="n_folds must be at least 2"):
            CrossValidationConfig(n_folds=1)


class TestHyperparameterTuningConfig:
    """Test hyperparameter tuning configuration."""
    
    def test_default_config(self):
        """Test default configuration."""
        config = HyperparameterTuningConfig()
        
        assert config.method == HyperparameterTuningMethod.GRID_SEARCH
        assert config.param_grid == {}
        assert config.n_iter == 100
        assert config.cv_folds == 5
        assert config.scoring == "accuracy"
        assert config.n_jobs == -1
        assert config.random_state == 42
    
    def test_custom_config(self):
        """Test custom configuration."""
        param_grid = {'C': [0.1, 1.0], 'kernel': ['rbf', 'linear']}
        config = HyperparameterTuningConfig(
            method=HyperparameterTuningMethod.RANDOM_SEARCH,
            param_grid=param_grid,
            n_iter=50,
            scoring='f1_macro'
        )
        
        assert config.method == HyperparameterTuningMethod.RANDOM_SEARCH
        assert config.param_grid == param_grid
        assert config.n_iter == 50
        assert config.scoring == 'f1_macro'


class TestUtilityFunctions:
    """Test utility functions."""
    
    def test_get_default_param_grids(self):
        """Test default parameter grids."""
        param_grids = get_default_param_grids()
        
        assert isinstance(param_grids, dict)
        assert 'random_forest_classifier' in param_grids
        assert 'random_forest_regressor' in param_grids
        assert 'logistic_regression' in param_grids
        assert 'svm_classifier' in param_grids
        assert 'svm_regressor' in param_grids
        
        # Check structure of random forest grid
        rf_grid = param_grids['random_forest_classifier']
        assert 'n_estimators' in rf_grid
        assert 'max_depth' in rf_grid
        assert isinstance(rf_grid['n_estimators'], list)
    
    def test_quick_model_comparison_classification(self):
        """Test quick model comparison for classification."""
        X, y = make_classification(n_samples=50, n_features=5, n_classes=2, random_state=42)
        X_df = pd.DataFrame(X)
        y_series = pd.Series(y)
        
        scores = quick_model_comparison(X_df, y_series, TaskType.CLASSIFICATION, cv_folds=3)
        
        assert isinstance(scores, dict)
        assert len(scores) >= 2
        
        for model_name, score in scores.items():
            assert isinstance(score, (int, float))
            assert 0 <= score <= 1  # Accuracy should be between 0 and 1
    
    def test_quick_model_comparison_regression(self):
        """Test quick model comparison for regression."""
        X, y = make_regression(n_samples=50, n_features=5, random_state=42)
        X_df = pd.DataFrame(X)
        y_series = pd.Series(y)
        
        scores = quick_model_comparison(X_df, y_series, TaskType.REGRESSION, cv_folds=3)
        
        assert isinstance(scores, dict)
        assert len(scores) >= 2
        
        for model_name, score in scores.items():
            assert isinstance(score, (int, float))
            # For regression, scores are typically negative (neg_mean_squared_error)
            # or between 0 and 1 (r2_score)


class TestModelPerformanceReport:
    """Test model performance report structure."""
    
    def test_report_creation(self):
        """Test creating a performance report."""
        cv_scores = {
            'test_accuracy': np.array([0.9, 0.85, 0.95]),
            'test_f1_macro': np.array([0.88, 0.82, 0.92])
        }
        mean_scores = {'accuracy': 0.9, 'f1_macro': 0.87}
        std_scores = {'accuracy': 0.04, 'f1_macro': 0.04}
        feature_importance = {'feature_0': 0.3, 'feature_1': 0.7}
        
        report = ModelPerformanceReport(
            task_type=TaskType.CLASSIFICATION,
            model_name='test_model',
            cv_scores=cv_scores,
            mean_scores=mean_scores,
            std_scores=std_scores,
            best_score=0.9,
            feature_importance=feature_importance
        )
        
        assert report.task_type == TaskType.CLASSIFICATION
        assert report.model_name == 'test_model'
        assert report.best_score == 0.9
        assert len(report.feature_importance) == 2


if __name__ == '__main__':
    pytest.main([__file__])