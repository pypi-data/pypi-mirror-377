"""Data Preprocessing Module

This module provides comprehensive preprocessing capabilities including feature scaling,
encoding, selection, and custom transformations for machine learning workflows.
"""

import json
import logging
import warnings
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple, Union

import joblib
import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.compose import ColumnTransformer
from sklearn.decomposition import PCA, TruncatedSVD
from sklearn.feature_selection import (
    RFE,
    SelectFromModel,
    SelectKBest,
    SelectPercentile,
    VarianceThreshold,
    chi2,
    f_classif,
    f_regression,
    mutual_info_classif,
    mutual_info_regression,
)
from sklearn.impute import KNNImputer, SimpleImputer
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import (
    LabelEncoder,
    MaxAbsScaler,
    MinMaxScaler,
    OneHotEncoder,
    OrdinalEncoder,
    PolynomialFeatures,
    PowerTransformer,
    QuantileTransformer,
    RobustScaler,
    StandardScaler,
    TargetEncoder,
)

# Configure logging
logger = logging.getLogger(__name__)


class ScalingMethod(Enum):
    """Feature scaling methods."""
    STANDARD = "standard"
    MINMAX = "minmax"
    ROBUST = "robust"
    MAXABS = "maxabs"
    QUANTILE_UNIFORM = "quantile_uniform"
    QUANTILE_NORMAL = "quantile_normal"
    POWER_YEOJONSON = "power_yeojonson"
    POWER_BOXCOX = "power_boxcox"
    NONE = "none"


class EncodingMethod(Enum):
    """Categorical encoding methods."""
    ONEHOT = "onehot"
    ORDINAL = "ordinal"
    LABEL = "label"
    TARGET = "target"
    FREQUENCY = "frequency"
    BINARY = "binary"
    NONE = "none"


class SelectionMethod(Enum):
    """Feature selection methods."""
    VARIANCE_THRESHOLD = "variance_threshold"
    UNIVARIATE_KBEST = "univariate_kbest"
    UNIVARIATE_PERCENTILE = "univariate_percentile"
    MODEL_BASED = "model_based"
    RECURSIVE_ELIMINATION = "recursive_elimination"
    PCA = "pca"
    TRUNCATED_SVD = "truncated_svd"
    NONE = "none"


class ImputationMethod(Enum):
    """Missing value imputation methods."""
    MEAN = "mean"
    MEDIAN = "median"
    MODE = "mode"
    CONSTANT = "constant"
    FORWARD_FILL = "forward_fill"
    BACKWARD_FILL = "backward_fill"
    KNN = "knn"
    ITERATIVE = "iterative"
    DROP = "drop"
    NONE = "none"


@dataclass
class PreprocessingConfig:
    """Configuration for preprocessing pipeline."""
    # Scaling configuration - Conservative defaults for better UX
    numeric_scaling: ScalingMethod = ScalingMethod.NONE
    
    # Encoding configuration - Conservative defaults for better UX  
    categorical_encoding: EncodingMethod = EncodingMethod.NONE
    handle_unknown_categories: str = "ignore"
    
    # Imputation configuration
    numeric_imputation: ImputationMethod = ImputationMethod.MEDIAN
    categorical_imputation: ImputationMethod = ImputationMethod.MODE
    imputation_constant: Any = 0
    
    # Feature selection configuration
    feature_selection: SelectionMethod = SelectionMethod.NONE
    selection_k: int = 10
    selection_percentile: float = 50.0
    variance_threshold: float = 0.0
    
    # Feature engineering configuration
    create_polynomial_features: bool = False
    polynomial_degree: int = 2
    polynomial_include_bias: bool = False
    
    # General configuration
    drop_first_dummy: bool = True
    sparse_output: bool = False
    random_state: int = 42


@dataclass
class PreprocessingReport:
    """Report of preprocessing operations performed."""
    original_shape: Tuple[int, int]
    final_shape: Tuple[int, int]
    
    # Columns information
    original_columns: List[str]
    final_columns: List[str]
    numeric_columns: List[str]
    categorical_columns: List[str]
    
    # Operations performed
    scaling_applied: bool
    encoding_applied: bool
    imputation_applied: bool
    feature_selection_applied: bool
    feature_engineering_applied: bool
    
    # Detailed information
    dropped_columns: List[str]
    imputed_columns: List[str]
    scaled_columns: List[str]
    encoded_columns: List[str]
    selected_features: List[str]
    
    # Statistics
    missing_values_before: int
    missing_values_after: int
    
    # Configuration used
    config: PreprocessingConfig
    
    def __post_init__(self):
        """Calculate additional metrics."""
        self.dimensionality_change = self.final_shape[1] - self.original_shape[1]
        self.feature_reduction_ratio = (
            (self.original_shape[1] - self.final_shape[1]) / self.original_shape[1]
            if self.original_shape[1] > 0 else 0
        )


class CustomTransformer(BaseEstimator, TransformerMixin):
    """Custom transformer for specific preprocessing needs."""
    
    def __init__(self, transform_func=None, feature_names=None):
        """
        Initialize custom transformer.
        
        Args:
            transform_func: Function to apply to data
            feature_names: Names for output features
        """
        self.transform_func = transform_func
        self.feature_names = feature_names
        
    def fit(self, X, y=None):
        """Fit the transformer."""
        return self
        
    def transform(self, X):
        """Transform the data."""
        if self.transform_func:
            return self.transform_func(X)
        return X
        
    def get_feature_names_out(self, input_features=None):
        """Get output feature names."""
        if self.feature_names:
            return self.feature_names
        return input_features


class PreprocessingPipeline:
    """Comprehensive preprocessing pipeline for ML workflows."""
    
    def __init__(self, config: PreprocessingConfig = None):
        """
        Initialize preprocessing pipeline.
        
        Args:
            config: Preprocessing configuration
        """
        self.config = config or PreprocessingConfig()
        self.pipeline = None
        self.column_transformer = None
        self.feature_selector = None
        self.is_fitted = False
        
        # Store column information
        self.numeric_columns = []
        self.categorical_columns = []
        self.original_columns = []
        
        # Store preprocessing components
        self.scalers = {}
        self.encoders = {}
        self.imputers = {}
        
        logger.info(f"Initialized preprocessing pipeline with config: {self.config}")
    
    def fit(self, X: pd.DataFrame, y: Optional[pd.Series] = None) -> 'PreprocessingPipeline':
        """
        Fit the preprocessing pipeline.
        
        Args:
            X: Input features
            y: Target variable (optional)
            
        Returns:
            Self for method chaining
        """
        # Check for empty DataFrame
        if X.empty:
            raise ValueError("Cannot fit preprocessing pipeline on empty DataFrame")
        
        logger.info(f"Fitting preprocessing pipeline on data with shape {X.shape}")
        
        # Store original column information
        self.original_columns = X.columns.tolist()
        self.numeric_columns = X.select_dtypes(include=[np.number]).columns.tolist()
        self.categorical_columns = X.select_dtypes(include=['object', 'category']).columns.tolist()
        
        # Build preprocessing pipeline
        self._build_pipeline(X, y)
        
        # Fit the pipeline
        self.pipeline.fit(X, y)
        self.is_fitted = True
        
        logger.info("Preprocessing pipeline fitted successfully")
        return self
    
    def transform(self, X: pd.DataFrame) -> pd.DataFrame:
        """
        Transform data using fitted pipeline.
        
        Args:
            X: Input features
            
        Returns:
            Transformed DataFrame
        """
        if not self.is_fitted:
            raise ValueError("Pipeline must be fitted before transform")
        
        # Transform data
        X_transformed = self.pipeline.transform(X)
        
        # Convert to DataFrame with appropriate column names
        if isinstance(X_transformed, np.ndarray):
            # Generate column names based on actual output shape
            n_features = X_transformed.shape[1]
            feature_names = [f"feature_{i}" for i in range(n_features)]
            X_transformed = pd.DataFrame(X_transformed, columns=feature_names, index=X.index)
        
        return X_transformed
    
    def fit_transform(self, X: pd.DataFrame, y: Optional[pd.Series] = None) -> pd.DataFrame:
        """
        Fit and transform data in one step.
        
        Args:
            X: Input features
            y: Target variable (optional)
            
        Returns:
            Transformed DataFrame
        """
        return self.fit(X, y).transform(X)
    
    def _build_pipeline(self, X: pd.DataFrame, y: Optional[pd.Series] = None) -> None:
        """Build the preprocessing pipeline."""
        steps = []
        
        # Step 1: Imputation
        if self.config.numeric_imputation != ImputationMethod.NONE or \
           self.config.categorical_imputation != ImputationMethod.NONE:
            imputer = self._build_imputer()
            steps.append(('imputer', imputer))
        
        # Step 2: Scaling and Encoding
        column_transformer = self._build_column_transformer()
        steps.append(('column_transformer', column_transformer))
        
        # Step 3: Feature Engineering
        if self.config.create_polynomial_features:
            # Check if we have categorical columns with no encoding
            if (self.categorical_columns and 
                self.config.categorical_encoding == EncodingMethod.NONE):
                logger.warning("Polynomial features work best with numeric data. "
                              "Consider setting categorical_encoding to ONEHOT or ORDINAL "
                              "for optimal polynomial feature generation.")
            
            poly_features = PolynomialFeatures(
                degree=self.config.polynomial_degree,
                include_bias=self.config.polynomial_include_bias
            )
            steps.append(('polynomial_features', poly_features))
        
        # Step 4: Feature Selection
        if self.config.feature_selection != SelectionMethod.NONE:
            selector = self._build_feature_selector(X, y)
            if selector is not None:  # Only add if selector was created
                steps.append(('feature_selector', selector))
        
        # Create pipeline
        self.pipeline = Pipeline(steps)
    
    def _build_imputer(self) -> ColumnTransformer:
        """Build imputation transformer."""
        transformers = []
        
        # Get column indices instead of names
        numeric_indices = [i for i, col in enumerate(self.original_columns) if col in self.numeric_columns]
        categorical_indices = [i for i, col in enumerate(self.original_columns) if col in self.categorical_columns]
        
        # Numeric imputation
        if numeric_indices and self.config.numeric_imputation != ImputationMethod.NONE:
            numeric_imputer = self._get_imputer(self.config.numeric_imputation, 'numeric')
            transformers.append(('numeric_imputer', numeric_imputer, numeric_indices))
        
        # Categorical imputation
        if categorical_indices and self.config.categorical_imputation != ImputationMethod.NONE:
            categorical_imputer = self._get_imputer(self.config.categorical_imputation, 'categorical')
            transformers.append(('categorical_imputer', categorical_imputer, categorical_indices))
        
        return ColumnTransformer(transformers, remainder='passthrough')
    
    def _build_column_transformer(self) -> ColumnTransformer:
        """Build column transformer for scaling and encoding."""
        transformers = []
        
        # Get column indices instead of names
        numeric_indices = [i for i, col in enumerate(self.original_columns) if col in self.numeric_columns]
        categorical_indices = [i for i, col in enumerate(self.original_columns) if col in self.categorical_columns]
        
        # Numeric scaling
        if numeric_indices and self.config.numeric_scaling != ScalingMethod.NONE:
            scaler = self._get_scaler(self.config.numeric_scaling)
            transformers.append(('numeric_scaler', scaler, numeric_indices))
        elif numeric_indices:
            transformers.append(('numeric_passthrough', 'passthrough', numeric_indices))
        
        # Categorical encoding
        if categorical_indices and self.config.categorical_encoding != EncodingMethod.NONE:
            encoder = self._get_encoder(self.config.categorical_encoding)
            transformers.append(('categorical_encoder', encoder, categorical_indices))
        elif categorical_indices:
            transformers.append(('categorical_passthrough', 'passthrough', categorical_indices))
        
        return ColumnTransformer(transformers, remainder='passthrough')
    
    def _build_feature_selector(self, X: pd.DataFrame, y: Optional[pd.Series] = None):
        """Build feature selector."""
        if self.config.feature_selection == SelectionMethod.VARIANCE_THRESHOLD:
            return VarianceThreshold(threshold=self.config.variance_threshold)
        
        elif self.config.feature_selection == SelectionMethod.UNIVARIATE_KBEST:
            # Skip univariate feature selection if no target is provided
            if y is None:
                logger.warning("Skipping univariate feature selection: no target provided")
                return None
                
            # Check if we have categorical columns with no encoding
            if (self.categorical_columns and 
                self.config.categorical_encoding == EncodingMethod.NONE):
                logger.warning("Skipping univariate feature selection: categorical columns present but no encoding configured. "
                              "Consider setting categorical_encoding to ONEHOT or ORDINAL for feature selection to work.")
                return None
                
            score_func = self._get_score_function(y)
            return SelectKBest(score_func=score_func, k=self.config.selection_k)
        
        elif self.config.feature_selection == SelectionMethod.UNIVARIATE_PERCENTILE:
            # Skip univariate feature selection if no target is provided
            if y is None:
                logger.warning("Skipping univariate feature selection: no target provided")
                return None
                
            # Check if we have categorical columns with no encoding
            if (self.categorical_columns and 
                self.config.categorical_encoding == EncodingMethod.NONE):
                logger.warning("Skipping univariate feature selection: categorical columns present but no encoding configured. "
                              "Consider setting categorical_encoding to ONEHOT or ORDINAL for feature selection to work.")
                return None
                
            score_func = self._get_score_function(y)
            return SelectPercentile(score_func=score_func, percentile=self.config.selection_percentile)
        
        elif self.config.feature_selection == SelectionMethod.PCA:
            return PCA(n_components=self.config.selection_k)
        
        elif self.config.feature_selection == SelectionMethod.TRUNCATED_SVD:
            return TruncatedSVD(n_components=self.config.selection_k)
        
        else:
            return None
    
    def _get_imputer(self, method: ImputationMethod, column_type: str):
        """Get imputer based on method and column type."""
        if method == ImputationMethod.MEAN:
            return SimpleImputer(strategy='mean')
        elif method == ImputationMethod.MEDIAN:
            return SimpleImputer(strategy='median')
        elif method == ImputationMethod.MODE:
            return SimpleImputer(strategy='most_frequent')
        elif method == ImputationMethod.CONSTANT:
            return SimpleImputer(strategy='constant', fill_value=self.config.imputation_constant)
        elif method == ImputationMethod.KNN:
            return KNNImputer(n_neighbors=5)
        else:
            return SimpleImputer(strategy='median' if column_type == 'numeric' else 'most_frequent')
    
    def _get_scaler(self, method: ScalingMethod):
        """Get scaler based on method."""
        if method == ScalingMethod.STANDARD:
            return StandardScaler()
        elif method == ScalingMethod.MINMAX:
            return MinMaxScaler()
        elif method == ScalingMethod.ROBUST:
            return RobustScaler()
        elif method == ScalingMethod.MAXABS:
            return MaxAbsScaler()
        elif method == ScalingMethod.QUANTILE_UNIFORM:
            return QuantileTransformer(output_distribution='uniform')
        elif method == ScalingMethod.QUANTILE_NORMAL:
            return QuantileTransformer(output_distribution='normal')
        elif method == ScalingMethod.POWER_YEOJONSON:
            return PowerTransformer(method='yeo-johnson')
        elif method == ScalingMethod.POWER_BOXCOX:
            return PowerTransformer(method='box-cox')
        else:
            return StandardScaler()
    
    def _get_encoder(self, method: EncodingMethod):
        """Get encoder based on method."""
        if method == EncodingMethod.ONEHOT:
            return OneHotEncoder(
                handle_unknown=self.config.handle_unknown_categories,
                drop='first' if self.config.drop_first_dummy else None,
                sparse_output=self.config.sparse_output
            )
        elif method == EncodingMethod.ORDINAL:
            return OrdinalEncoder(handle_unknown='use_encoded_value', unknown_value=-1)
        elif method == EncodingMethod.LABEL:
            # Note: LabelEncoder can't be used in ColumnTransformer for multiple columns
            # Fall back to OrdinalEncoder for compatibility
            return OrdinalEncoder(handle_unknown='use_encoded_value', unknown_value=-1)
        else:
            return OneHotEncoder(
                handle_unknown=self.config.handle_unknown_categories,
                drop='first' if self.config.drop_first_dummy else None,
                sparse_output=self.config.sparse_output
            )
    
    def _get_score_function(self, y: Optional[Union[pd.Series, np.ndarray]] = None):
        """Get score function for feature selection."""
        if y is None:
            return f_classif
        
        # Convert to pandas Series if it's a numpy array
        if isinstance(y, np.ndarray):
            y = pd.Series(y)
        
        # Check if it's a classification or regression task
        if y.dtype == 'object' or pd.api.types.is_string_dtype(y) or y.nunique() < 10:
            return f_classif  # Classification
        else:
            return f_regression  # Regression
    
    def _get_feature_names(self) -> List[str]:
        """Get feature names after transformation."""
        if not self.is_fitted:
            return self.original_columns
        
        try:
            # Try to get feature names from pipeline
            if hasattr(self.pipeline, 'get_feature_names_out'):
                return self.pipeline.get_feature_names_out().tolist()
            
            # Fallback: generate generic feature names based on output shape
            # This is a simplified approach that works for testing
            return [f"feature_{i}" for i in range(len(self.original_columns))]
            
        except Exception as e:
            logger.warning(f"Could not get feature names: {e}")
            return [f"feature_{i}" for i in range(len(self.original_columns))]
    
    def generate_report(self, X_original: pd.DataFrame, X_transformed: pd.DataFrame) -> PreprocessingReport:
        """
        Generate comprehensive preprocessing report.
        
        Args:
            X_original: Original data before preprocessing
            X_transformed: Data after preprocessing
            
        Returns:
            PreprocessingReport with detailed information
        """
        # Calculate missing values
        missing_before = X_original.isnull().sum().sum()
        missing_after = X_transformed.isnull().sum().sum()
        
        # Identify operations performed
        scaling_applied = self.config.numeric_scaling != ScalingMethod.NONE
        encoding_applied = self.config.categorical_encoding != EncodingMethod.NONE
        imputation_applied = (self.config.numeric_imputation != ImputationMethod.NONE or 
                            self.config.categorical_imputation != ImputationMethod.NONE)
        feature_selection_applied = self.config.feature_selection != SelectionMethod.NONE
        feature_engineering_applied = self.config.create_polynomial_features
        
        # Identify affected columns
        scaled_columns = self.numeric_columns if scaling_applied else []
        encoded_columns = self.categorical_columns if encoding_applied else []
        imputed_columns = [col for col in X_original.columns if X_original[col].isnull().sum() > 0]
        
        # Calculate selected features
        selected_features = X_transformed.columns.tolist()
        # For transformed data, we can't directly compare column names, so we just note the difference
        dropped_columns = []
        if len(X_original.columns) > len(X_transformed.columns):
            dropped_columns = ["transformed_features"]
        
        return PreprocessingReport(
            original_shape=X_original.shape,
            final_shape=X_transformed.shape,
            original_columns=X_original.columns.tolist(),
            final_columns=X_transformed.columns.tolist(),
            numeric_columns=self.numeric_columns,
            categorical_columns=self.categorical_columns,
            scaling_applied=scaling_applied,
            encoding_applied=encoding_applied,
            imputation_applied=imputation_applied,
            feature_selection_applied=feature_selection_applied,
            feature_engineering_applied=feature_engineering_applied,
            dropped_columns=dropped_columns,
            imputed_columns=imputed_columns,
            scaled_columns=scaled_columns,
            encoded_columns=encoded_columns,
            selected_features=selected_features,
            missing_values_before=missing_before,
            missing_values_after=missing_after,
            config=self.config
        )
    
    def save_pipeline(self, filepath: str) -> None:
        """Save fitted pipeline to file."""
        if not self.is_fitted:
            raise ValueError("Pipeline must be fitted before saving")
        
        joblib.dump({
            'pipeline': self.pipeline,
            'config': self.config,
            'numeric_columns': self.numeric_columns,
            'categorical_columns': self.categorical_columns,
            'original_columns': self.original_columns
        }, filepath)
        
        logger.info(f"Pipeline saved to {filepath}")
    
    @classmethod
    def load_pipeline(cls, filepath: str) -> 'PreprocessingPipeline':
        """Load fitted pipeline from file."""
        data = joblib.load(filepath)
        
        pipeline_obj = cls(config=data['config'])
        pipeline_obj.pipeline = data['pipeline']
        pipeline_obj.numeric_columns = data['numeric_columns']
        pipeline_obj.categorical_columns = data['categorical_columns']
        pipeline_obj.original_columns = data['original_columns']
        pipeline_obj.is_fitted = True
        
        logger.info(f"Pipeline loaded from {filepath}")
        return pipeline_obj


# Utility functions
def create_preprocessing_pipeline(
    scaling_method: Union[str, ScalingMethod] = ScalingMethod.NONE,
    encoding_method: Union[str, EncodingMethod] = EncodingMethod.NONE,
    imputation_method: Union[str, ImputationMethod] = ImputationMethod.MEDIAN,
    feature_selection: Union[str, SelectionMethod] = SelectionMethod.NONE,
    **kwargs
) -> PreprocessingPipeline:
    """
    Create a preprocessing pipeline with specified methods.
    
    Args:
        scaling_method: Method for numeric feature scaling
        encoding_method: Method for categorical feature encoding
        imputation_method: Method for missing value imputation
        feature_selection: Method for feature selection
        **kwargs: Additional configuration parameters
        
    Returns:
        PreprocessingPipeline instance
    """
    # Convert string parameters to enums
    if isinstance(scaling_method, str):
        scaling_method = ScalingMethod(scaling_method)
    if isinstance(encoding_method, str):
        encoding_method = EncodingMethod(encoding_method)
    if isinstance(imputation_method, str):
        imputation_method = ImputationMethod(imputation_method)
    if isinstance(feature_selection, str):
        feature_selection = SelectionMethod(feature_selection)
    
    # Use appropriate imputation methods for different column types
    # Allow MODE for numeric columns too (though not typical, it's valid)
    numeric_imputation = imputation_method if imputation_method in [ImputationMethod.MEAN, ImputationMethod.MEDIAN, ImputationMethod.MODE, ImputationMethod.KNN, ImputationMethod.CONSTANT] else ImputationMethod.MEDIAN
    categorical_imputation = imputation_method if imputation_method in [ImputationMethod.MODE, ImputationMethod.CONSTANT] else ImputationMethod.MODE
    
    config = PreprocessingConfig(
        numeric_scaling=scaling_method,
        categorical_encoding=encoding_method,
        numeric_imputation=numeric_imputation,
        categorical_imputation=categorical_imputation,
        feature_selection=feature_selection,
        **kwargs
    )
    
    return PreprocessingPipeline(config)


def quick_preprocess(
    X: pd.DataFrame,
    y: Optional[pd.Series] = None,
    test_size: float = 0.2,
    random_state: int = 42
) -> Tuple[pd.DataFrame, pd.DataFrame, Optional[pd.Series], Optional[pd.Series]]:
    """
    Quick preprocessing with train-test split.
    
    Args:
        X: Input features
        y: Target variable (optional)
        test_size: Proportion of test set
        random_state: Random state for reproducibility
        
    Returns:
        Tuple of (X_train, X_test, y_train, y_test)
    """
    # Create default preprocessing pipeline
    pipeline = create_preprocessing_pipeline()
    
    # Split data first
    if y is not None:
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=random_state
        )
    else:
        X_train, X_test = train_test_split(
            X, test_size=test_size, random_state=random_state
        )
        y_train, y_test = None, None
    
    # Fit on training data and transform both sets
    X_train_processed = pipeline.fit_transform(X_train, y_train)
    X_test_processed = pipeline.transform(X_test)
    
    return X_train_processed, X_test_processed, y_train, y_test


def preprocess_for_ml(
    X: pd.DataFrame,
    y: Optional[pd.Series] = None,
    task_type: str = 'classification',
    test_size: float = 0.2,
    validation_size: float = 0.2,
    random_state: int = 42
) -> Dict[str, Any]:
    """
    Comprehensive preprocessing for ML workflows.
    
    Args:
        X: Input features
        y: Target variable (optional)
        task_type: 'classification' or 'regression'
        test_size: Proportion of test set
        validation_size: Proportion of validation set
        random_state: Random state for reproducibility
        
    Returns:
        Dictionary with processed datasets and pipeline
    """
    # Create ML-optimized preprocessing pipeline 
    # For ML workflows, we need to handle mixed data types properly
    config = PreprocessingConfig(
        numeric_scaling=ScalingMethod.STANDARD,  # Standard scaling is appropriate for ML
        categorical_encoding=EncodingMethod.ORDINAL,  # Ordinal encoding for ML compatibility
        numeric_imputation=ImputationMethod.MEDIAN,
        categorical_imputation=ImputationMethod.MODE,
        feature_selection=SelectionMethod.NONE,  # Conservative: no automatic feature selection
        selection_k=min(50, X.shape[1]),  # Select top 50 features or all if fewer
        create_polynomial_features=False,  # Can be enabled for specific use cases
        drop_first_dummy=True,
        random_state=random_state
    )
    
    pipeline = PreprocessingPipeline(config)
    
    # Split data into train/validation/test
    if y is not None:
        X_train, X_temp, y_train, y_temp = train_test_split(
            X, y, test_size=test_size + validation_size, random_state=random_state
        )
        
        X_val, X_test, y_val, y_test = train_test_split(
            X_temp, y_temp, 
            test_size=test_size / (test_size + validation_size), 
            random_state=random_state
        )
    else:
        X_train, X_temp = train_test_split(
            X, test_size=test_size + validation_size, random_state=random_state
        )
        
        X_val, X_test = train_test_split(
            X_temp, 
            test_size=test_size / (test_size + validation_size), 
            random_state=random_state
        )
        y_train, y_val, y_test = None, None, None
    
    # Fit pipeline on training data
    pipeline.fit(X_train, y_train)
    
    # Transform all datasets
    X_train_processed = pipeline.transform(X_train)
    X_val_processed = pipeline.transform(X_val)
    X_test_processed = pipeline.transform(X_test)
    
    # Generate preprocessing report
    report = pipeline.generate_report(X_train, X_train_processed)
    
    return {
        'X_train': X_train_processed,
        'X_val': X_val_processed,
        'X_test': X_test_processed,
        'y_train': y_train,
        'y_val': y_val,
        'y_test': y_test,
        'pipeline': pipeline,
        'report': report,
        'original_shapes': {
            'train': X_train.shape,
            'val': X_val.shape,
            'test': X_test.shape
        }
    } 