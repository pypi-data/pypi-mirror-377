"""Data Cleaning Module

This module provides comprehensive data cleaning capabilities with advanced missing data
handling, outlier detection, and integrated cleaning pipelines for machine learning workflows.
"""

import logging
import warnings
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import numpy as np
import pandas as pd
from scipy import stats
from sklearn.cluster import DBSCAN
from sklearn.ensemble import IsolationForest
from sklearn.experimental import enable_iterative_imputer
from sklearn.impute import IterativeImputer, KNNImputer, SimpleImputer
from sklearn.neighbors import LocalOutlierFactor
from sklearn.preprocessing import RobustScaler, StandardScaler

# Suppress scikit-learn warnings
warnings.filterwarnings("ignore", category=UserWarning, module='sklearn')

logger = logging.getLogger(__name__)


class MissingDataMethod(Enum):
    """Enumeration of available methods for handling missing data.
    
    This enum defines all supported strategies for dealing with missing values
    in datasets, ranging from simple removal to advanced imputation techniques.
    Each method has different characteristics and is suitable for different
    scenarios based on the data type, missing pattern, and analysis requirements.
    
    Attributes:
        DROP_ROWS (str): Remove rows containing any missing values.
            Best for: Small amounts of missing data, complete case analysis required.
        DROP_COLUMNS (str): Remove columns with missing values.
            Best for: Features with high missing percentages, non-critical columns.
        FILL_MEAN (str): Fill missing values with column mean.
            Best for: Numerical data with normal distribution, moderate missing data.
        FILL_MEDIAN (str): Fill missing values with column median.
            Best for: Numerical data with skewed distribution or outliers.
        FILL_MODE (str): Fill missing values with most frequent value.
            Best for: Categorical data, discrete numerical data.
        FILL_CONSTANT (str): Fill missing values with a specified constant.
            Best for: Domain-specific defaults, indicator variables.
        FILL_FORWARD (str): Forward fill (carry last observation forward).
            Best for: Time series data, sequential data with trends.
        FILL_BACKWARD (str): Backward fill (carry next observation backward).
            Best for: Time series data, reverse sequential imputation.
        FILL_INTERPOLATE (str): Interpolate missing values between known values.
            Best for: Time series data, smooth numerical sequences.
        FILL_KNN (str): Use K-Nearest Neighbors imputation.
            Best for: Complex patterns, mixed data types, multivariate relationships.
        FILL_ITERATIVE (str): Use iterative imputation (MICE algorithm).
            Best for: Missing at random data, complex multivariate patterns.
        LEAVE_AS_IS (str): Keep missing values as-is for downstream handling.
            Best for: Algorithms that handle missing data natively.
    
    Example:
        Selecting appropriate methods for different scenarios::
        
            # For time series data
            method = MissingDataMethod.FILL_FORWARD
            
            # For categorical data
            method = MissingDataMethod.FILL_MODE
            
            # For complex numerical relationships
            method = MissingDataMethod.FILL_KNN
            
            # For high-quality imputation
            method = MissingDataMethod.FILL_ITERATIVE
    
    Note:
        The choice of method significantly impacts data quality and downstream
        analysis results. Consider the missing data mechanism (MCAR, MAR, MNAR)
        and data characteristics when selecting a method.
    """
    DROP_ROWS = "drop_rows"
    DROP_COLUMNS = "drop_columns"
    FILL_MEAN = "fill_mean"
    FILL_MEDIAN = "fill_median"
    FILL_MODE = "fill_mode"
    FILL_CONSTANT = "fill_constant"
    FILL_FORWARD = "fill_forward"
    FILL_BACKWARD = "fill_backward"
    FILL_INTERPOLATE = "fill_interpolate"
    FILL_KNN = "fill_knn"
    FILL_ITERATIVE = "fill_iterative"
    LEAVE_AS_IS = "leave_as_is"


class OutlierMethod(Enum):
    """Enumeration of available methods for outlier detection.
    
    This enum defines various statistical and machine learning approaches for
    identifying outliers in datasets. Each method has different assumptions,
    strengths, and suitable use cases depending on data characteristics and
    the type of outliers expected.
    
    Attributes:
        Z_SCORE (str): Standard Z-score outlier detection.
            Best for: Normally distributed data, univariate outliers.
            Assumes: Normal distribution, identifies points > threshold standard deviations.
        MODIFIED_Z_SCORE (str): Modified Z-score using median absolute deviation.
            Best for: Non-normal data, robust to existing outliers.
            Assumes: Less sensitive to extreme values than standard Z-score.
        IQR (str): Interquartile Range method.
            Best for: Skewed distributions, quartile-based detection.
            Assumes: Outliers are beyond Q1 - 1.5*IQR or Q3 + 1.5*IQR.
        ISOLATION_FOREST (str): Isolation Forest algorithm.
            Best for: High-dimensional data, complex patterns, anomaly detection.
            Assumes: Outliers are easier to isolate than normal points.
        LOCAL_OUTLIER_FACTOR (str): Local Outlier Factor (LOF).
            Best for: Density-based outliers, local anomalies, varying densities.
            Assumes: Outliers have lower local density than neighbors.
        DBSCAN (str): Density-Based Spatial Clustering outlier detection.
            Best for: Clustering-based outliers, spatial data, noise detection.
            Assumes: Outliers are points in low-density regions.
        PERCENTILE (str): Percentile-based outlier detection.
            Best for: Simple threshold-based detection, robust to distribution.
            Assumes: Outliers are in extreme percentiles (e.g., <5th or >95th).
        STATISTICAL_DISTANCE (str): Statistical distance methods (Mahalanobis).
            Best for: Multivariate outliers, correlated features.
            Assumes: Multivariate normal distribution, considers feature correlations.
    
    Example:
        Selecting methods for different data characteristics::
        
            # For normally distributed numerical data
            method = OutlierMethod.Z_SCORE
            
            # For robust detection in skewed data
            method = OutlierMethod.IQR
            
            # For high-dimensional or complex patterns
            method = OutlierMethod.ISOLATION_FOREST
            
            # For multivariate outlier detection
            method = OutlierMethod.STATISTICAL_DISTANCE
    
    Note:
        No single method works optimally for all datasets. Consider data
        distribution, dimensionality, and expected outlier characteristics
        when selecting a detection method.
    """
    Z_SCORE = "z_score"
    MODIFIED_Z_SCORE = "modified_z_score"
    IQR = "iqr"
    ISOLATION_FOREST = "isolation_forest"
    LOCAL_OUTLIER_FACTOR = "local_outlier_factor"
    DBSCAN = "dbscan"
    PERCENTILE = "percentile"
    STATISTICAL_DISTANCE = "statistical_distance"


class OutlierAction(Enum):
    """Enumeration of available actions for handling detected outliers.
    
    This enum defines the different strategies for dealing with outliers once
    they have been detected. Each action has different impacts on the dataset
    and downstream analysis, and should be chosen based on the analysis goals
    and data characteristics.
    
    Attributes:
        REMOVE (str): Remove outlier data points from the dataset.
            Best for: Clean training data required, outliers are clear errors.
            Impact: Reduces dataset size, may lose valuable information.
        CAP (str): Cap outliers at specified threshold values (winsorizing).
            Best for: Preserving dataset size, reducing extreme value impact.
            Impact: Maintains sample size, reduces variance, may bias distribution.
        TRANSFORM (str): Apply mathematical transformations to reduce outlier impact.
            Best for: Preserving information while reducing influence.
            Impact: Changes data distribution, may improve normality.
        FLAG (str): Add boolean columns indicating outlier status, keep original data.
            Best for: Preserving all information, allowing downstream decisions.
            Impact: Increases feature space, preserves original data integrity.
        LEAVE_AS_IS (str): Keep outliers unchanged for downstream handling.
            Best for: Algorithms robust to outliers, domain expertise required.
            Impact: No data modification, passes responsibility to next stage.
    
    Example:
        Selecting actions based on analysis requirements::
        
            # For training robust models
            action = OutlierAction.CAP
            
            # For exploratory analysis
            action = OutlierAction.FLAG
            
            # For data quality improvement
            action = OutlierAction.REMOVE
            
            # For preserving raw information
            action = OutlierAction.LEAVE_AS_IS
    
    Note:
        The choice of action significantly impacts the final analysis results.
        Consider the nature of outliers (errors vs. rare events) and analysis
        requirements when selecting an action strategy.
    """
    REMOVE = "remove"
    CAP = "cap"
    TRANSFORM = "transform"
    FLAG = "flag"
    LEAVE_AS_IS = "leave_as_is"


@dataclass
class MissingDataConfig:
    """Configuration parameters for missing data handling strategies.
    
    This dataclass encapsulates all parameters needed to configure missing data
    handling behavior. It provides sensible defaults while allowing fine-tuning
    of imputation strategies based on specific dataset characteristics and
    analysis requirements.
    
    Attributes:
        method (MissingDataMethod): The primary imputation strategy to use.
            Default is FILL_MEDIAN for robust central tendency imputation.
        constant_value (Any): Value to use when method is FILL_CONSTANT.
            Default is 0, can be set to any value appropriate for the data.
        drop_threshold (float): Proportion of missing values above which to drop
            columns or rows (depending on method). Range: 0.0 to 1.0.
            Default is 0.5 (50% missing data threshold).
        knn_neighbors (int): Number of neighbors for KNN imputation.
            Default is 5, should be tuned based on dataset size and density.
        max_iter (int): Maximum iterations for iterative imputation (MICE).
            Default is 10, may need more for complex patterns or convergence.
        random_state (int): Random seed for reproducible imputation results.
            Default is 42, ensures consistent results across runs.
    
    Example:
        Configure different imputation strategies::
        
            # Conservative median imputation
            config = MissingDataConfig(
                method=MissingDataMethod.FILL_MEDIAN,
                drop_threshold=0.3
            )
            
            # Advanced KNN imputation
            config = MissingDataConfig(
                method=MissingDataMethod.FILL_KNN,
                knn_neighbors=10,
                random_state=123
            )
            
            # Iterative imputation for complex patterns
            config = MissingDataConfig(
                method=MissingDataMethod.FILL_ITERATIVE,
                max_iter=20,
                random_state=42
            )
            
            # Constant fill for indicator variables
            config = MissingDataConfig(
                method=MissingDataMethod.FILL_CONSTANT,
                constant_value=-1
            )
    
    Note:
        The effectiveness of each method depends on the missing data mechanism
        (MCAR, MAR, MNAR) and dataset characteristics. Consider validating
        imputation quality using cross-validation or holdout testing.
    """
    method: MissingDataMethod = MissingDataMethod.FILL_MEDIAN
    constant_value: Any = 0
    drop_threshold: float = 0.5  # Drop columns/rows with more than 50% missing
    knn_neighbors: int = 5
    max_iter: int = 10  # For iterative imputation
    random_state: int = 42


@dataclass
class OutlierConfig:
    """Configuration parameters for outlier detection and handling strategies.
    
    This dataclass provides comprehensive configuration options for outlier
    detection methods and subsequent actions. It includes parameters for all
    supported detection algorithms and allows fine-tuning based on specific
    dataset characteristics and analysis requirements.
    
    Attributes:
        method (OutlierMethod): The outlier detection algorithm to use.
            Default is IQR for robust quartile-based detection.
        action (OutlierAction): The action to take with detected outliers.
            Default is CAP to preserve dataset size while reducing impact.
        z_threshold (float): Threshold for Z-score based methods. Values beyond
            ±threshold standard deviations are considered outliers.
            Default is 3.0 (99.7% of normal distribution).
        iqr_multiplier (float): Multiplier for IQR method. Outliers are beyond
            Q1 - multiplier*IQR or Q3 + multiplier*IQR.
            Default is 1.5 (standard boxplot definition).
        contamination (float): Expected proportion of outliers in the dataset
            for Isolation Forest and LOF methods. Range: 0.0 to 0.5.
            Default is 0.1 (10% outliers expected).
        percentile_bounds (Tuple[float, float]): Lower and upper percentile
            bounds for percentile-based detection. Values outside these
            percentiles are considered outliers.
            Default is (5.0, 95.0) for 5th and 95th percentiles.
        dbscan_eps (float): Maximum distance between samples for DBSCAN
            clustering. Affects sensitivity to local density variations.
            Default is 0.5, should be tuned based on data scale.
        dbscan_min_samples (int): Minimum samples in a neighborhood for DBSCAN
            core points. Affects cluster formation and noise detection.
            Default is 5, should consider dataset size and dimensionality.
    
    Example:
        Configure different outlier detection strategies::
        
            # Conservative IQR-based detection
            config = OutlierConfig(
                method=OutlierMethod.IQR,
                action=OutlierAction.CAP,
                iqr_multiplier=2.0  # Less sensitive
            )
            
            # Isolation Forest for high-dimensional data
            config = OutlierConfig(
                method=OutlierMethod.ISOLATION_FOREST,
                action=OutlierAction.FLAG,
                contamination=0.05  # Expect 5% outliers
            )
            
            # Strict Z-score detection
            config = OutlierConfig(
                method=OutlierMethod.Z_SCORE,
                action=OutlierAction.REMOVE,
                z_threshold=2.5  # More sensitive
            )
            
            # DBSCAN clustering-based detection
            config = OutlierConfig(
                method=OutlierMethod.DBSCAN,
                action=OutlierAction.FLAG,
                dbscan_eps=0.3,
                dbscan_min_samples=10
            )
    
    Note:
        Parameter tuning significantly affects detection sensitivity and false
        positive rates. Consider validating detection quality using labeled
        data or domain expertise when available.
    """
    method: OutlierMethod = OutlierMethod.IQR
    action: OutlierAction = OutlierAction.CAP
    z_threshold: float = 3.0
    iqr_multiplier: float = 1.5
    contamination: float = 0.1  # For isolation forest and LOF
    percentile_bounds: Tuple[float, float] = (5.0, 95.0)
    dbscan_eps: float = 0.5
    dbscan_min_samples: int = 5


@dataclass
class CleaningConfig:
    """Combined configuration for data cleaning."""
    missing_data: MissingDataConfig = None
    outlier_detection: OutlierConfig = None
    handle_missing_first: bool = True
    preserve_original: bool = True
    
    def __post_init__(self):
        if self.missing_data is None:
            self.missing_data = MissingDataConfig()
        if self.outlier_detection is None:
            self.outlier_detection = OutlierConfig()


@dataclass
class MissingDataReport:
    """Report of missing data analysis."""
    total_missing: int
    missing_percentage: float
    missing_by_column: Dict[str, int]
    missing_percentage_by_column: Dict[str, float]
    columns_with_missing: List[str]
    missing_patterns: pd.DataFrame
    recommendations: List[str]


@dataclass
class OutlierReport:
    """Report of outlier detection results."""
    total_outliers: int
    outlier_percentage: float
    outliers_by_column: Dict[str, int]
    outlier_indices: List[int]
    method: str
    threshold_values: Dict[str, Any]
    recommendations: List[str]


@dataclass
class CleaningReport:
    """Comprehensive data cleaning report."""
    original_shape: Tuple[int, int]
    final_shape: Tuple[int, int]
    missing_data_report: MissingDataReport
    outlier_report: OutlierReport
    actions_taken: List[str]
    columns_dropped: List[str]
    rows_dropped: int
    cleaning_config: CleaningConfig


class MissingDataHandler:
    """Advanced missing data detection, analysis, and handling system.
    
    This class provides comprehensive missing data analysis and imputation
    capabilities. It can detect missing data patterns, analyze their impact,
    and apply various imputation strategies while maintaining detailed records
    of all operations performed.
    
    The handler supports multiple imputation strategies from simple statistical
    measures to advanced machine learning approaches like KNN and iterative
    imputation (MICE algorithm).
    
    Attributes:
        config (MissingDataConfig): Configuration parameters for imputation strategy
        imputer: The fitted imputation model (varies by method)
        fitted_values (Dict): Stored values from fitting process for reuse
    
    Example:
        Basic missing data handling workflow::
        
            from mcp_ds_toolkit_server.data import (
                MissingDataHandler, MissingDataConfig, MissingDataMethod
            )
            
            # Configure advanced imputation
            config = MissingDataConfig(
                method=MissingDataMethod.FILL_KNN,
                knn_neighbors=5,
                drop_threshold=0.8
            )
            
            # Initialize handler and analyze data
            handler = MissingDataHandler(config)
            report = handler.analyze_missing_data(df)
            
            # Apply imputation
            cleaned_df = handler.handle_missing_data(df)
            
            # Review results
            print(f"Missing values before: {report.total_missing}")
            print(f"Missing values after: {cleaned_df.isnull().sum().sum()}")
    
    Note:
        The handler maintains state for consistent imputation across train/test
        splits. Use fit_transform for training data and transform for test data
        to ensure consistent imputation parameters.
    """
    
    def __init__(self, config: MissingDataConfig = None):
        """Initialize the missing data handler with configuration.
        
        Args:
            config (Optional[MissingDataConfig]): Configuration for missing data
                handling. If None, uses default configuration with median imputation.
        """
        self.config = config or MissingDataConfig()
        self.imputer = None
        self.fitted_values = {}
    
    def analyze_missing_data(self, df: pd.DataFrame) -> MissingDataReport:
        """
        Analyze missing data patterns in the dataset.
        
        Args:
            df: Input DataFrame
            
        Returns:
            MissingDataReport with detailed analysis
        """
        logger.info(f"Analyzing missing data patterns in dataset with shape {df.shape}")
        
        # Calculate missing data statistics
        total_missing = df.isnull().sum().sum()
        total_cells = df.shape[0] * df.shape[1]
        missing_percentage = (total_missing / total_cells) * 100 if total_cells > 0 else 0.0
        
        # Missing data by column
        missing_by_column = df.isnull().sum().to_dict()
        missing_percentage_by_column = {
            col: (missing_count / len(df)) * 100 if len(df) > 0 else 0.0
            for col, missing_count in missing_by_column.items()
        }
        
        # Columns with missing data
        columns_with_missing = [col for col, count in missing_by_column.items() if count > 0]
        
        # Missing data patterns
        if len(df) > 0 and len(df.columns) > 0:
            missing_patterns = df.isnull().groupby(list(df.columns)).size().reset_index(name='count')
            missing_patterns = missing_patterns.sort_values('count', ascending=False)
        else:
            missing_patterns = pd.DataFrame(columns=['count'])
        
        # Generate recommendations
        recommendations = self._generate_missing_data_recommendations(
            df, missing_percentage_by_column
        )
        
        return MissingDataReport(
            total_missing=total_missing,
            missing_percentage=missing_percentage,
            missing_by_column=missing_by_column,
            missing_percentage_by_column=missing_percentage_by_column,
            columns_with_missing=columns_with_missing,
            missing_patterns=missing_patterns,
            recommendations=recommendations
        )
    
    def handle_missing_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Handle missing data based on the configured method.
        
        Args:
            df: Input DataFrame
            
        Returns:
            DataFrame with missing data handled
        """
        logger.info(f"Handling missing data using method: {self.config.method.value}")
        
        if self.config.method == MissingDataMethod.DROP_ROWS:
            return self._drop_rows_with_missing(df)
        elif self.config.method == MissingDataMethod.DROP_COLUMNS:
            return self._drop_columns_with_missing(df)
        elif self.config.method == MissingDataMethod.FILL_MEAN:
            return self._fill_with_mean(df)
        elif self.config.method == MissingDataMethod.FILL_MEDIAN:
            return self._fill_with_median(df)
        elif self.config.method == MissingDataMethod.FILL_MODE:
            return self._fill_with_mode(df)
        elif self.config.method == MissingDataMethod.FILL_CONSTANT:
            return self._fill_with_constant(df)
        elif self.config.method == MissingDataMethod.FILL_FORWARD:
            return df.fillna(method='ffill')
        elif self.config.method == MissingDataMethod.FILL_BACKWARD:
            return df.fillna(method='bfill')
        elif self.config.method == MissingDataMethod.FILL_INTERPOLATE:
            return self._fill_with_interpolation(df)
        elif self.config.method == MissingDataMethod.FILL_KNN:
            return self._fill_with_knn(df)
        elif self.config.method == MissingDataMethod.FILL_ITERATIVE:
            return self._fill_with_iterative(df)
        else:
            return df.copy()
    
    def _drop_rows_with_missing(self, df: pd.DataFrame) -> pd.DataFrame:
        """Drop rows with missing values based on threshold."""
        threshold = int(df.shape[1] * (1 - self.config.drop_threshold))
        return df.dropna(thresh=threshold)
    
    def _drop_columns_with_missing(self, df: pd.DataFrame) -> pd.DataFrame:
        """Drop columns with missing values based on threshold."""
        threshold = int(df.shape[0] * (1 - self.config.drop_threshold))
        return df.dropna(axis=1, thresh=threshold)
    
    def _fill_with_mean(self, df: pd.DataFrame) -> pd.DataFrame:
        """Fill missing values with mean (numeric columns only)."""
        df_filled = df.copy()
        numeric_columns = df.select_dtypes(include=[np.number]).columns
        
        for col in numeric_columns:
            if col not in self.fitted_values:
                self.fitted_values[col] = df[col].mean()
            df_filled[col] = df_filled[col].fillna(self.fitted_values[col])
        
        return df_filled
    
    def _fill_with_median(self, df: pd.DataFrame) -> pd.DataFrame:
        """Fill missing values with median (numeric columns only)."""
        df_filled = df.copy()
        numeric_columns = df.select_dtypes(include=[np.number]).columns
        
        for col in numeric_columns:
            if col not in self.fitted_values:
                self.fitted_values[col] = df[col].median()
            df_filled[col] = df_filled[col].fillna(self.fitted_values[col])
        
        return df_filled
    
    def _fill_with_mode(self, df: pd.DataFrame) -> pd.DataFrame:
        """Fill missing values with mode."""
        df_filled = df.copy()
        
        for col in df.columns:
            if col not in self.fitted_values:
                mode_value = df[col].mode()
                self.fitted_values[col] = mode_value[0] if len(mode_value) > 0 else df[col].iloc[0]
            df_filled[col] = df_filled[col].fillna(self.fitted_values[col])
        
        return df_filled
    
    def _fill_with_constant(self, df: pd.DataFrame) -> pd.DataFrame:
        """Fill missing values with constant value."""
        return df.fillna(self.config.constant_value)
    
    def _fill_with_interpolation(self, df: pd.DataFrame) -> pd.DataFrame:
        """Fill missing values using interpolation."""
        df_filled = df.copy()
        numeric_columns = df.select_dtypes(include=[np.number]).columns
        
        for col in numeric_columns:
            df_filled[col] = df_filled[col].interpolate()
        
        return df_filled
    
    def _fill_with_knn(self, df: pd.DataFrame) -> pd.DataFrame:
        """Fill missing values using KNN imputation."""
        if self.imputer is None:
            self.imputer = KNNImputer(n_neighbors=self.config.knn_neighbors)
        
        # Separate numeric and categorical columns
        numeric_columns = df.select_dtypes(include=[np.number]).columns
        categorical_columns = df.select_dtypes(exclude=[np.number]).columns
        
        df_filled = df.copy()
        
        # Apply KNN imputation to numeric columns
        if len(numeric_columns) > 0:
            numeric_data = df[numeric_columns]
            imputed_numeric = self.imputer.fit_transform(numeric_data)
            df_filled[numeric_columns] = imputed_numeric
        
        # Fill categorical columns with mode
        for col in categorical_columns:
            if col not in self.fitted_values:
                mode_value = df[col].mode()
                self.fitted_values[col] = mode_value[0] if len(mode_value) > 0 else 'Unknown'
            df_filled[col] = df_filled[col].fillna(self.fitted_values[col])
        
        return df_filled
    
    def _fill_with_iterative(self, df: pd.DataFrame) -> pd.DataFrame:
        """Fill missing values using iterative imputation."""
        if self.imputer is None:
            self.imputer = IterativeImputer(
                max_iter=self.config.max_iter,
                random_state=self.config.random_state
            )
        
        # Separate numeric and categorical columns
        numeric_columns = df.select_dtypes(include=[np.number]).columns
        categorical_columns = df.select_dtypes(exclude=[np.number]).columns
        
        df_filled = df.copy()
        
        # Apply iterative imputation to numeric columns
        if len(numeric_columns) > 0:
            numeric_data = df[numeric_columns]
            imputed_numeric = self.imputer.fit_transform(numeric_data)
            df_filled[numeric_columns] = imputed_numeric
        
        # Fill categorical columns with mode
        for col in categorical_columns:
            if col not in self.fitted_values:
                mode_value = df[col].mode()
                self.fitted_values[col] = mode_value[0] if len(mode_value) > 0 else 'Unknown'
            df_filled[col] = df_filled[col].fillna(self.fitted_values[col])
        
        return df_filled
    
    def _generate_missing_data_recommendations(
        self, 
        df: pd.DataFrame, 
        missing_percentage_by_column: Dict[str, float]
    ) -> List[str]:
        """Generate recommendations for handling missing data."""
        recommendations = []
        
        # Overall missing data percentage
        total_missing_pct = (df.isnull().sum().sum() / (df.shape[0] * df.shape[1])) * 100
        
        if total_missing_pct > 20:
            recommendations.append("High missing data percentage (>20%) - consider data collection improvements")
        
        # Column-specific recommendations
        for col, missing_pct in missing_percentage_by_column.items():
            if missing_pct > 50:
                recommendations.append(f"Column '{col}' has >50% missing data - consider dropping")
            elif missing_pct > 20:
                recommendations.append(f"Column '{col}' has significant missing data - investigate patterns")
        
        # Method recommendations
        if total_missing_pct < 5:
            recommendations.append("Low missing data - simple imputation methods should work well")
        elif total_missing_pct < 15:
            recommendations.append("Moderate missing data - consider advanced imputation (KNN, Iterative)")
        else:
            recommendations.append("High missing data - consider domain expertise for handling strategy")
        
        return recommendations


class OutlierDetector:
    """Advanced outlier detection and handling."""
    
    def __init__(self, config: OutlierConfig = None):
        self.config = config or OutlierConfig()
        self.fitted_params = {}
        self.scaler = None
    
    def detect_outliers(self, df: pd.DataFrame, columns: List[str] = None) -> OutlierReport:
        """
        Detect outliers in the dataset using the configured method.
        
        Args:
            df: Input DataFrame
            columns: Columns to analyze (None for all numeric columns)
            
        Returns:
            OutlierReport with detailed analysis
        """
        if columns is None:
            columns = df.select_dtypes(include=[np.number]).columns.tolist()
        
        logger.info(f"Detecting outliers using method: {self.config.method.value}")
        
        if self.config.method == OutlierMethod.Z_SCORE:
            return self._detect_outliers_z_score(df, columns)
        elif self.config.method == OutlierMethod.MODIFIED_Z_SCORE:
            return self._detect_outliers_modified_z_score(df, columns)
        elif self.config.method == OutlierMethod.IQR:
            return self._detect_outliers_iqr(df, columns)
        elif self.config.method == OutlierMethod.ISOLATION_FOREST:
            return self._detect_outliers_isolation_forest(df, columns)
        elif self.config.method == OutlierMethod.LOCAL_OUTLIER_FACTOR:
            return self._detect_outliers_lof(df, columns)
        elif self.config.method == OutlierMethod.DBSCAN:
            return self._detect_outliers_dbscan(df, columns)
        elif self.config.method == OutlierMethod.PERCENTILE:
            return self._detect_outliers_percentile(df, columns)
        else:
            return self._detect_outliers_statistical_distance(df, columns)
    
    def handle_outliers(self, df: pd.DataFrame, outlier_indices: List[int]) -> pd.DataFrame:
        """
        Handle detected outliers based on the configured action.
        
        Args:
            df: Input DataFrame
            outlier_indices: Indices of detected outliers
            
        Returns:
            DataFrame with outliers handled
        """
        logger.info(f"Handling outliers using action: {self.config.action.value}")
        
        if self.config.action == OutlierAction.REMOVE:
            return df.drop(index=outlier_indices)
        elif self.config.action == OutlierAction.CAP:
            return self._cap_outliers(df, outlier_indices)
        elif self.config.action == OutlierAction.TRANSFORM:
            return self._transform_outliers(df)
        elif self.config.action == OutlierAction.FLAG:
            return self._flag_outliers(df, outlier_indices)
        else:
            return df.copy()
    
    def _detect_outliers_z_score(self, df: pd.DataFrame, columns: List[str]) -> OutlierReport:
        """Detect outliers using Z-score method."""
        outlier_indices = set()
        outliers_by_column = {}
        threshold_values = {'z_threshold': self.config.z_threshold}
        
        for col in columns:
            if col in df.columns:
                z_scores = np.abs(stats.zscore(df[col].dropna()))
                outlier_mask = z_scores > self.config.z_threshold
                col_outliers = df.index[df[col].notna()][outlier_mask].tolist()
                outlier_indices.update(col_outliers)
                outliers_by_column[col] = len(col_outliers)
                
                # Store bounds for capping - use percentile bounds as fallback
                mean_val = df[col].mean()
                std_val = df[col].std()
                lower_bound = mean_val - self.config.z_threshold * std_val
                upper_bound = mean_val + self.config.z_threshold * std_val
                self.fitted_params[col] = {
                    'lower_bound': lower_bound,
                    'upper_bound': upper_bound
                }
        
        return self._create_outlier_report(df, list(outlier_indices), outliers_by_column, threshold_values)
    
    def _detect_outliers_modified_z_score(self, df: pd.DataFrame, columns: List[str]) -> OutlierReport:
        """Detect outliers using Modified Z-score method."""
        outlier_indices = set()
        outliers_by_column = {}
        threshold_values = {'z_threshold': self.config.z_threshold}
        
        for col in columns:
            if col in df.columns:
                median = df[col].median()
                mad = stats.median_abs_deviation(df[col].dropna())
                modified_z_scores = 0.6745 * (df[col] - median) / mad
                outlier_mask = np.abs(modified_z_scores) > self.config.z_threshold
                col_outliers = df.index[outlier_mask].tolist()
                outlier_indices.update(col_outliers)
                outliers_by_column[col] = len(col_outliers)
                
                # Store bounds for capping
                lower_bound = median - self.config.z_threshold * mad / 0.6745
                upper_bound = median + self.config.z_threshold * mad / 0.6745
                self.fitted_params[col] = {
                    'lower_bound': lower_bound,
                    'upper_bound': upper_bound
                }
        
        return self._create_outlier_report(df, list(outlier_indices), outliers_by_column, threshold_values)
    
    def _detect_outliers_iqr(self, df: pd.DataFrame, columns: List[str]) -> OutlierReport:
        """Detect outliers using Interquartile Range (IQR) method."""
        outlier_indices = set()
        outliers_by_column = {}
        threshold_values = {'iqr_multiplier': self.config.iqr_multiplier}
        
        for col in columns:
            if col in df.columns:
                Q1 = df[col].quantile(0.25)
                Q3 = df[col].quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - self.config.iqr_multiplier * IQR
                upper_bound = Q3 + self.config.iqr_multiplier * IQR
                
                col_outliers = df.index[(df[col] < lower_bound) | (df[col] > upper_bound)].tolist()
                outlier_indices.update(col_outliers)
                outliers_by_column[col] = len(col_outliers)
                
                # Store bounds for capping
                self.fitted_params[col] = {'lower_bound': lower_bound, 'upper_bound': upper_bound}
        
        return self._create_outlier_report(df, list(outlier_indices), outliers_by_column, threshold_values)
    
    def _detect_outliers_isolation_forest(self, df: pd.DataFrame, columns: List[str]) -> OutlierReport:
        """Detect outliers using Isolation Forest."""
        data = df[columns].dropna()
        
        if len(data) == 0:
            return self._create_empty_outlier_report()
        
        isolation_forest = IsolationForest(
            contamination=self.config.contamination,
            random_state=42
        )
        
        outlier_labels = isolation_forest.fit_predict(data)
        outlier_indices = data.index[outlier_labels == -1].tolist()
        
        outliers_by_column = {col: 0 for col in columns}
        # Note: Isolation Forest provides global outlier detection
        
        threshold_values = {'contamination': self.config.contamination}
        
        return self._create_outlier_report(df, outlier_indices, outliers_by_column, threshold_values)
    
    def _detect_outliers_lof(self, df: pd.DataFrame, columns: List[str]) -> OutlierReport:
        """Detect outliers using Local Outlier Factor."""
        data = df[columns].dropna()
        
        if len(data) == 0:
            return self._create_empty_outlier_report()
        
        lof = LocalOutlierFactor(
            n_neighbors=20,
            contamination=self.config.contamination
        )
        
        outlier_labels = lof.fit_predict(data)
        outlier_indices = data.index[outlier_labels == -1].tolist()
        
        outliers_by_column = {col: 0 for col in columns}
        threshold_values = {'contamination': self.config.contamination}
        
        return self._create_outlier_report(df, outlier_indices, outliers_by_column, threshold_values)
    
    def _detect_outliers_dbscan(self, df: pd.DataFrame, columns: List[str]) -> OutlierReport:
        """Detect outliers using DBSCAN clustering."""
        data = df[columns].dropna()
        
        if len(data) == 0:
            return self._create_empty_outlier_report()
        
        # Standardize data for DBSCAN
        if self.scaler is None:
            self.scaler = StandardScaler()
        
        scaled_data = self.scaler.fit_transform(data)
        
        dbscan = DBSCAN(
            eps=self.config.dbscan_eps,
            min_samples=self.config.dbscan_min_samples
        )
        
        cluster_labels = dbscan.fit_predict(scaled_data)
        outlier_indices = data.index[cluster_labels == -1].tolist()
        
        outliers_by_column = {col: 0 for col in columns}
        threshold_values = {
            'eps': self.config.dbscan_eps,
            'min_samples': self.config.dbscan_min_samples
        }
        
        return self._create_outlier_report(df, outlier_indices, outliers_by_column, threshold_values)
    
    def _detect_outliers_percentile(self, df: pd.DataFrame, columns: List[str]) -> OutlierReport:
        """Detect outliers using percentile bounds."""
        outlier_indices = set()
        outliers_by_column = {}
        threshold_values = {'percentile_bounds': self.config.percentile_bounds}
        
        for col in columns:
            if col in df.columns:
                lower_percentile = df[col].quantile(self.config.percentile_bounds[0] / 100)
                upper_percentile = df[col].quantile(self.config.percentile_bounds[1] / 100)
                
                col_outliers = df.index[
                    (df[col] < lower_percentile) | (df[col] > upper_percentile)
                ].tolist()
                outlier_indices.update(col_outliers)
                outliers_by_column[col] = len(col_outliers)
                
                # Store bounds for capping
                self.fitted_params[col] = {
                    'lower_bound': lower_percentile,
                    'upper_bound': upper_percentile
                }
        
        return self._create_outlier_report(df, list(outlier_indices), outliers_by_column, threshold_values)
    
    def _detect_outliers_statistical_distance(self, df: pd.DataFrame, columns: List[str]) -> OutlierReport:
        """Detect outliers using statistical distance (Mahalanobis distance)."""
        data = df[columns].dropna()
        
        if len(data) == 0:
            return self._create_empty_outlier_report()
        
        try:
            # Calculate Mahalanobis distance
            mean = data.mean()
            cov = data.cov()
            inv_cov = np.linalg.inv(cov)
            
            distances = []
            for _, row in data.iterrows():
                diff = row - mean
                distance = np.sqrt(diff.T @ inv_cov @ diff)
                distances.append(distance)
            
            # Use threshold based on chi-square distribution
            threshold = np.sqrt(stats.chi2.ppf(0.95, df=len(columns)))
            outlier_indices = data.index[np.array(distances) > threshold].tolist()
            
            outliers_by_column = {col: 0 for col in columns}
            threshold_values = {'mahalanobis_threshold': threshold}
            
            return self._create_outlier_report(df, outlier_indices, outliers_by_column, threshold_values)
        
        except np.linalg.LinAlgError:
            logger.warning("Singular covariance matrix, falling back to Z-score method")
            return self._detect_outliers_z_score(df, columns)
    
    def _cap_outliers(self, df: pd.DataFrame, outlier_indices: List[int]) -> pd.DataFrame:
        """Cap outliers using fitted parameters."""
        df_capped = df.copy()
        
        for col, params in self.fitted_params.items():
            if col in df.columns and 'lower_bound' in params and 'upper_bound' in params:
                df_capped[col] = df_capped[col].clip(
                    lower=params['lower_bound'],
                    upper=params['upper_bound']
                )
        
        return df_capped
    
    def _transform_outliers(self, df: pd.DataFrame) -> pd.DataFrame:
        """Transform outliers using log transformation."""
        df_transformed = df.copy()
        numeric_columns = df.select_dtypes(include=[np.number]).columns
        
        for col in numeric_columns:
            if col in df.columns:
                # Apply log transformation (add 1 to handle zeros)
                df_transformed[col] = np.log1p(df_transformed[col])
        
        return df_transformed
    
    def _flag_outliers(self, df: pd.DataFrame, outlier_indices: List[int]) -> pd.DataFrame:
        """Flag outliers with a new column."""
        df_flagged = df.copy()
        df_flagged['is_outlier'] = False
        df_flagged.loc[outlier_indices, 'is_outlier'] = True
        
        return df_flagged
    
    def _create_outlier_report(
        self,
        df: pd.DataFrame,
        outlier_indices: List[int],
        outliers_by_column: Dict[str, int],
        threshold_values: Dict[str, Any]
    ) -> OutlierReport:
        """Create outlier report from detection results."""
        total_outliers = len(outlier_indices)
        outlier_percentage = (total_outliers / len(df)) * 100 if len(df) > 0 else 0.0
        
        return OutlierReport(
            total_outliers=total_outliers,
            outlier_percentage=outlier_percentage,
            outliers_by_column=outliers_by_column,
            outlier_indices=outlier_indices,
            method=self.config.method.value,
            threshold_values=threshold_values,
            recommendations=self._generate_outlier_recommendations(
                total_outliers, outlier_percentage, outliers_by_column
            )
        )
    
    def _create_empty_outlier_report(self) -> OutlierReport:
        """Create empty outlier report for edge cases."""
        return OutlierReport(
            total_outliers=0,
            outlier_percentage=0.0,
            outliers_by_column={},
            outlier_indices=[],
            method=self.config.method.value,
            threshold_values={},
            recommendations=["No data available for outlier detection"]
        )
    
    def _generate_outlier_recommendations(
        self,
        total_outliers: int,
        outlier_percentage: float,
        outliers_by_column: Dict[str, int]
    ) -> List[str]:
        """Generate recommendations for handling outliers."""
        recommendations = []
        
        if outlier_percentage > 15:
            recommendations.append("High outlier percentage (>15%) - investigate data quality")
        elif outlier_percentage > 5:
            recommendations.append("Moderate outlier percentage - consider domain expertise")
        elif outlier_percentage < 1:
            recommendations.append("Low outlier percentage - standard handling should work")
        
        for col, count in outliers_by_column.items():
            if count > 20:
                recommendations.append(f"Column '{col}' has many outliers - investigate data source")
        
        return recommendations


class DataCleaner:
    """Integrated data cleaning pipeline."""
    
    def __init__(self, config: CleaningConfig = None):
        self.config = config or CleaningConfig()
        self.missing_handler = MissingDataHandler(self.config.missing_data)
        self.outlier_detector = OutlierDetector(self.config.outlier_detection)
        self.original_data = None
    
    def clean_data(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, CleaningReport]:
        """
        Perform comprehensive data cleaning.
        
        Args:
            df: Input DataFrame
            
        Returns:
            Tuple of (cleaned_df, cleaning_report)
        """
        logger.info(f"Starting data cleaning on dataset with shape {df.shape}")
        
        if self.config.preserve_original:
            self.original_data = df.copy()
        
        # Track actions taken
        actions_taken = []
        columns_dropped = []
        rows_dropped = 0
        
        # Initial shape
        original_shape = df.shape
        current_df = df.copy()
        
        # Step 1: Analyze missing data
        missing_report = self.missing_handler.analyze_missing_data(current_df)
        
        # Step 2: Handle missing data (if configured to do so first)
        if self.config.handle_missing_first:
            original_rows = len(current_df)
            current_df = self.missing_handler.handle_missing_data(current_df)
            rows_dropped += original_rows - len(current_df)
            
            # Check for dropped columns
            dropped_cols = set(df.columns) - set(current_df.columns)
            columns_dropped.extend(list(dropped_cols))
            
            actions_taken.append(f"Applied missing data handling: {self.config.missing_data.method.value}")
        
        # Step 3: Detect outliers
        outlier_report = self.outlier_detector.detect_outliers(current_df)
        
        # Step 4: Handle outliers
        if outlier_report.total_outliers > 0:
            original_rows = len(current_df)
            current_df = self.outlier_detector.handle_outliers(current_df, outlier_report.outlier_indices)
            rows_dropped += original_rows - len(current_df)
            actions_taken.append(f"Applied outlier handling: {self.config.outlier_detection.action.value}")
        
        # Step 5: Handle missing data (if configured to do so after outliers)
        if not self.config.handle_missing_first:
            original_rows = len(current_df)
            current_df = self.missing_handler.handle_missing_data(current_df)
            rows_dropped += original_rows - len(current_df)
            
            # Check for dropped columns
            dropped_cols = set(df.columns) - set(current_df.columns)
            columns_dropped.extend(list(dropped_cols))
            
            actions_taken.append(f"Applied missing data handling: {self.config.missing_data.method.value}")
        
        # Final shape
        final_shape = current_df.shape
        
        # Create comprehensive report
        cleaning_report = CleaningReport(
            original_shape=original_shape,
            final_shape=final_shape,
            missing_data_report=missing_report,
            outlier_report=outlier_report,
            actions_taken=actions_taken,
            columns_dropped=columns_dropped,
            rows_dropped=rows_dropped,
            cleaning_config=self.config
        )
        
        logger.info(f"Data cleaning completed. Shape: {original_shape} -> {final_shape}")
        
        return current_df, cleaning_report
    
    def get_original_data(self) -> Optional[pd.DataFrame]:
        """Get original data if preserved."""
        return self.original_data


# Utility functions
def analyze_missing_data(df: pd.DataFrame) -> MissingDataReport:
    """
    Quick missing data analysis.
    
    Args:
        df: Input DataFrame
        
    Returns:
        MissingDataReport
    """
    handler = MissingDataHandler()
    return handler.analyze_missing_data(df)


def detect_outliers(
    df: pd.DataFrame,
    method: Union[str, OutlierMethod] = OutlierMethod.IQR,
    **kwargs
) -> OutlierReport:
    """
    Quick outlier detection.
    
    Args:
        df: Input DataFrame
        method: Outlier detection method
        **kwargs: Additional parameters for outlier detection
        
    Returns:
        OutlierReport
    """
    if isinstance(method, str):
        method = OutlierMethod(method)
    
    config = OutlierConfig(method=method, **kwargs)
    detector = OutlierDetector(config)
    return detector.detect_outliers(df)


def clean_dataset(
    df: pd.DataFrame,
    missing_method: Union[str, MissingDataMethod] = MissingDataMethod.FILL_MEDIAN,
    outlier_method: Union[str, OutlierMethod] = OutlierMethod.IQR,
    outlier_action: Union[str, OutlierAction] = OutlierAction.CAP,
    **kwargs
) -> Tuple[pd.DataFrame, CleaningReport]:
    """
    Quick data cleaning with default parameters.
    
    Args:
        df: Input DataFrame
        missing_method: Method for handling missing data
        outlier_method: Method for detecting outliers
        outlier_action: Action to take with outliers
        **kwargs: Additional configuration parameters
        
    Returns:
        Tuple of (cleaned_df, cleaning_report)
    """
    # Convert string parameters to enums
    if isinstance(missing_method, str):
        missing_method = MissingDataMethod(missing_method)
    if isinstance(outlier_method, str):
        outlier_method = OutlierMethod(outlier_method)
    if isinstance(outlier_action, str):
        outlier_action = OutlierAction(outlier_action)
    
    # Separate kwargs for missing data and outlier detection
    missing_kwargs = {}
    outlier_kwargs = {}
    
    # Missing data specific kwargs
    for key in ['constant_value', 'drop_threshold', 'knn_neighbors', 'max_iter', 'random_state']:
        if key in kwargs:
            missing_kwargs[key] = kwargs[key]
    
    # Outlier detection specific kwargs
    for key in ['z_threshold', 'iqr_multiplier', 'contamination', 'percentile_bounds', 'dbscan_eps', 'dbscan_min_samples']:
        if key in kwargs:
            outlier_kwargs[key] = kwargs[key]
    
    # Other kwargs go to overall config
    other_kwargs = {k: v for k, v in kwargs.items() 
                   if k not in missing_kwargs and k not in outlier_kwargs}
    
    # Create configuration
    missing_config = MissingDataConfig(method=missing_method, **missing_kwargs)
    outlier_config = OutlierConfig(method=outlier_method, action=outlier_action, **outlier_kwargs)
    cleaning_config = CleaningConfig(
        missing_data=missing_config,
        outlier_detection=outlier_config,
        **other_kwargs
    )
    
    # Create cleaner and clean data
    cleaner = DataCleaner(cleaning_config)
    return cleaner.clean_data(df) 