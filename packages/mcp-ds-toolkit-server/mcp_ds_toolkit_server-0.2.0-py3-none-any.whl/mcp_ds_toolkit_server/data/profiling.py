"""Data Profiling Module

This module provides comprehensive data profiling and statistical analysis capabilities
for understanding dataset characteristics, patterns, and relationships.
"""

import json
import logging
import warnings
from collections import Counter
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple, Union

import numpy as np
import pandas as pd
from scipy import stats
from sklearn.feature_selection import mutual_info_classif, mutual_info_regression
from sklearn.preprocessing import LabelEncoder

# Configure logging
logger = logging.getLogger(__name__)


class ProfileType(Enum):
    """Types of data profiling analysis."""
    BASIC = "basic"
    STATISTICAL = "statistical"
    CORRELATION = "correlation"
    FEATURE_IMPORTANCE = "feature_importance"
    COMPREHENSIVE = "comprehensive"


class DistributionType(Enum):
    """Statistical distribution types."""
    NORMAL = "normal"
    UNIFORM = "uniform"
    EXPONENTIAL = "exponential"
    SKEWED = "skewed"
    BIMODAL = "bimodal"
    UNKNOWN = "unknown"


@dataclass
class ColumnProfile:
    """Profile information for a single column."""
    name: str
    dtype: str
    null_count: int
    null_percentage: float
    unique_count: int
    unique_percentage: float
    most_frequent_value: Any
    most_frequent_count: int
    
    # Statistical measures (for numeric columns)
    mean: Optional[float] = None
    median: Optional[float] = None
    std: Optional[float] = None
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    q25: Optional[float] = None
    q75: Optional[float] = None
    skewness: Optional[float] = None
    kurtosis: Optional[float] = None
    distribution_type: Optional[DistributionType] = None
    
    # Categorical measures
    top_categories: Optional[Dict[str, int]] = None
    
    # Data quality indicators
    has_outliers: bool = False
    outlier_count: int = 0
    is_constant: bool = False
    has_high_cardinality: bool = False


@dataclass
class CorrelationAnalysis:
    """Correlation analysis results."""
    method: str
    correlation_matrix: pd.DataFrame
    strong_correlations: List[Tuple[str, str, float]]
    weak_correlations: List[Tuple[str, str, float]]
    highly_correlated_pairs: List[Tuple[str, str, float]]  # |correlation| > 0.8
    
    
@dataclass
class FeatureImportanceAnalysis:
    """Feature importance analysis results."""
    target_column: str
    feature_scores: Dict[str, float]
    top_features: List[Tuple[str, float]]
    low_importance_features: List[str]
    method: str


@dataclass
class DataProfile:
    """Comprehensive data profile."""
    dataset_name: str
    row_count: int
    column_count: int
    memory_usage: float
    duplicate_rows: int
    duplicate_percentage: float
    
    @property
    def shape(self) -> Tuple[int, int]:
        """Return the shape of the dataset (rows, columns)."""
        return (self.row_count, self.column_count)
    
    @property
    def quality_score(self) -> float:
        """Calculate overall data quality score (0-100)."""
        # Base score on completeness
        completeness_score = self.overall_completeness
        
        # Penalties for data quality issues
        penalties = 0
        
        # Duplicate rows penalty
        if self.duplicate_percentage > 0:
            penalties += min(self.duplicate_percentage, 20)  # Cap at 20% penalty
        
        # High cardinality columns penalty
        if self.high_cardinality_columns:
            penalties += min(len(self.high_cardinality_columns) * 5, 15)  # Cap at 15% penalty
        
        # Constant columns penalty
        if self.constant_columns:
            penalties += min(len(self.constant_columns) * 3, 10)  # Cap at 10% penalty
        
        # Outlier penalty
        if self.has_outliers:
            total_outliers = sum(profile.outlier_count for profile in self.column_profiles.values() 
                               if profile.outlier_count > 0)
            outlier_percentage = (total_outliers / self.row_count) * 100 if self.row_count > 0 else 0
            penalties += min(outlier_percentage, 10)  # Cap at 10% penalty
        
        return max(0, completeness_score - penalties)
    
    @property
    def has_outliers(self) -> bool:
        """Check if any column has outliers."""
        return any(profile.has_outliers for profile in self.column_profiles.values())
    
    # Column profiles
    column_profiles: Dict[str, ColumnProfile]
    
    # Type summaries
    numeric_columns: List[str]
    categorical_columns: List[str]
    datetime_columns: List[str]
    boolean_columns: List[str]
    
    # Statistical summaries
    correlation_analysis: Optional[CorrelationAnalysis] = None
    feature_importance: Optional[FeatureImportanceAnalysis] = None
    
    # Data quality summary
    overall_completeness: float = 0.0
    columns_with_missing: List[str] = None
    high_cardinality_columns: List[str] = None
    constant_columns: List[str] = None
    
    # Generated timestamp
    generated_at: str = None


class DataProfiler:
    """Comprehensive data profiling and statistical analysis."""
    
    def __init__(self, 
                 high_cardinality_threshold: float = 0.95,
                 outlier_method: str = 'iqr',
                 correlation_threshold: float = 0.5):
        """
        Initialize DataProfiler.
        
        Args:
            high_cardinality_threshold: Threshold for high cardinality detection
            outlier_method: Method for outlier detection ('iqr', 'zscore', 'isolation')
            correlation_threshold: Threshold for correlation significance
        """
        self.high_cardinality_threshold = high_cardinality_threshold
        self.outlier_method = outlier_method
        self.correlation_threshold = correlation_threshold
        
    def profile_dataset(self, 
                       data: pd.DataFrame,
                       dataset_name: str = "dataset",
                       profile_type: ProfileType = ProfileType.COMPREHENSIVE,
                       target_column: Optional[str] = None) -> DataProfile:
        """
        Generate comprehensive data profile.
        
        Args:
            data: DataFrame to profile
            dataset_name: Name of the dataset
            profile_type: Type of profiling to perform
            target_column: Target column for supervised learning analysis
            
        Returns:
            DataProfile object with comprehensive analysis
        """
        logger.info(f"Profiling dataset '{dataset_name}' with {len(data)} rows and {len(data.columns)} columns")
        
        # Basic dataset information
        row_count = len(data)
        column_count = len(data.columns)
        memory_usage = data.memory_usage(deep=True).sum() / 1024 / 1024  # MB
        duplicate_rows = data.duplicated().sum()
        duplicate_percentage = (duplicate_rows / row_count) * 100 if row_count > 0 else 0
        
        # Column type classification
        numeric_columns = data.select_dtypes(include=[np.number]).columns.tolist()
        categorical_columns = data.select_dtypes(include=['object', 'category']).columns.tolist()
        datetime_columns = data.select_dtypes(include=['datetime64']).columns.tolist()
        boolean_columns = data.select_dtypes(include=['bool']).columns.tolist()
        
        # Generate column profiles
        column_profiles = {}
        for col in data.columns:
            column_profiles[col] = self._profile_column(data, col)
        
        # Calculate overall completeness
        total_cells = row_count * column_count
        missing_cells = data.isnull().sum().sum()
        overall_completeness = ((total_cells - missing_cells) / total_cells) * 100 if total_cells > 0 else 100.0
        
        # Identify problematic columns
        columns_with_missing = [col for col, profile in column_profiles.items() 
                              if profile.null_count > 0]
        high_cardinality_columns = [col for col, profile in column_profiles.items() 
                                  if profile.has_high_cardinality]
        constant_columns = [col for col, profile in column_profiles.items() 
                          if profile.is_constant]
        
        # Create base profile
        profile = DataProfile(
            dataset_name=dataset_name,
            row_count=row_count,
            column_count=column_count,
            memory_usage=memory_usage,
            duplicate_rows=duplicate_rows,
            duplicate_percentage=duplicate_percentage,
            column_profiles=column_profiles,
            numeric_columns=numeric_columns,
            categorical_columns=categorical_columns,
            datetime_columns=datetime_columns,
            boolean_columns=boolean_columns,
            overall_completeness=overall_completeness,
            columns_with_missing=columns_with_missing,
            high_cardinality_columns=high_cardinality_columns,
            constant_columns=constant_columns,
            generated_at=pd.Timestamp.now().isoformat()
        )
        
        # Add advanced analysis based on profile type
        if profile_type in [ProfileType.CORRELATION, ProfileType.COMPREHENSIVE]:
            if len(numeric_columns) > 1:
                profile.correlation_analysis = self._analyze_correlations(data[numeric_columns])
                
        if profile_type in [ProfileType.FEATURE_IMPORTANCE, ProfileType.COMPREHENSIVE]:
            if target_column and target_column in data.columns:
                profile.feature_importance = self._analyze_feature_importance(
                    data, target_column
                )
        
        return profile
    
    def _profile_column(self, data: pd.DataFrame, column: str) -> ColumnProfile:
        """Profile a single column."""
        series = data[column]
        dtype = str(series.dtype)
        null_count = series.isnull().sum()
        null_percentage = (null_count / len(series)) * 100 if len(series) > 0 else 0
        
        # Handle empty series
        if len(series) == 0:
            return ColumnProfile(
                name=column,
                dtype=dtype,
                null_count=null_count,
                null_percentage=null_percentage,
                unique_count=0,
                unique_percentage=0,
                most_frequent_value=None,
                most_frequent_count=0,
                is_constant=True
            )
        
        # Basic statistics
        unique_count = series.nunique()
        unique_percentage = (unique_count / len(series)) * 100 if len(series) > 0 else 0
        
        # Most frequent value
        value_counts = series.value_counts()
        most_frequent_value = value_counts.index[0] if len(value_counts) > 0 else None
        most_frequent_count = value_counts.iloc[0] if len(value_counts) > 0 else 0
        
        # Quality indicators
        is_constant = unique_count <= 1
        has_high_cardinality = unique_percentage > self.high_cardinality_threshold * 100
        
        profile = ColumnProfile(
            name=column,
            dtype=dtype,
            null_count=null_count,
            null_percentage=null_percentage,
            unique_count=unique_count,
            unique_percentage=unique_percentage,
            most_frequent_value=most_frequent_value,
            most_frequent_count=most_frequent_count,
            is_constant=is_constant,
            has_high_cardinality=has_high_cardinality
        )
        
        # Numeric column analysis
        if pd.api.types.is_numeric_dtype(series):
            numeric_data = series.dropna()
            if len(numeric_data) > 0:
                profile.mean = float(numeric_data.mean())
                profile.median = float(numeric_data.median())
                profile.std = float(numeric_data.std())
                profile.min_value = float(numeric_data.min())
                profile.max_value = float(numeric_data.max())
                profile.q25 = float(numeric_data.quantile(0.25))
                profile.q75 = float(numeric_data.quantile(0.75))
                profile.skewness = float(stats.skew(numeric_data))
                profile.kurtosis = float(stats.kurtosis(numeric_data))
                
                # Distribution analysis
                profile.distribution_type = self._analyze_distribution(numeric_data)
                
                # Outlier detection
                outliers = self._detect_outliers(numeric_data)
                profile.has_outliers = len(outliers) > 0
                profile.outlier_count = len(outliers)
        
        # Categorical column analysis
        elif pd.api.types.is_object_dtype(series) or pd.api.types.is_categorical_dtype(series):
            if len(value_counts) > 0:
                # Top categories (limit to top 10)
                top_categories = value_counts.head(10).to_dict()
                profile.top_categories = {str(k): int(v) for k, v in top_categories.items()}
        
        return profile
    
    def _analyze_distribution(self, data: pd.Series) -> DistributionType:
        """Analyze the distribution type of numeric data."""
        if len(data) < 3:
            return DistributionType.UNKNOWN
        
        # Normality test
        if len(data) >= 8:  # shapiro-wilk requires at least 8 samples
            try:
                _, p_value = stats.shapiro(data[:5000])  # Sample for large datasets
                if p_value > 0.05:
                    return DistributionType.NORMAL
            except:
                pass
        
        # Check for uniform distribution
        if abs(stats.skew(data)) < 0.5 and abs(stats.kurtosis(data)) < 0.5:
            return DistributionType.UNIFORM
        
        # Check for skewness
        skewness = stats.skew(data)
        if abs(skewness) > 1:
            return DistributionType.SKEWED
        
        # Check for bimodality (simplified)
        kurtosis = stats.kurtosis(data)
        if kurtosis < -1:
            return DistributionType.BIMODAL
        
        return DistributionType.UNKNOWN
    
    def _detect_outliers(self, data: pd.Series) -> List[int]:
        """Detect outliers using specified method."""
        if len(data) == 0:
            return []
        
        if self.outlier_method == 'iqr':
            Q1 = data.quantile(0.25)
            Q3 = data.quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            outliers = data[(data < lower_bound) | (data > upper_bound)]
            return outliers.index.tolist()
        
        elif self.outlier_method == 'zscore':
            z_scores = np.abs(stats.zscore(data))
            outliers = data[z_scores > 2]  # Use threshold of 2 instead of 3
            return outliers.index.tolist()
        
        return []
    
    def _analyze_correlations(self, data: pd.DataFrame) -> CorrelationAnalysis:
        """Analyze correlations between numeric columns."""
        if len(data.columns) < 2:
            return CorrelationAnalysis(
                method="pearson",
                correlation_matrix=pd.DataFrame(),
                strong_correlations=[],
                weak_correlations=[],
                highly_correlated_pairs=[]
            )
        
        # Calculate correlation matrix
        corr_matrix = data.corr()
        
        # Extract correlation pairs
        strong_correlations = []
        weak_correlations = []
        highly_correlated_pairs = []
        
        for i in range(len(corr_matrix.columns)):
            for j in range(i+1, len(corr_matrix.columns)):
                col1 = corr_matrix.columns[i]
                col2 = corr_matrix.columns[j]
                correlation = corr_matrix.iloc[i, j]
                
                if pd.notna(correlation):
                    abs_corr = abs(correlation)
                    
                    if abs_corr > 0.8:
                        highly_correlated_pairs.append((col1, col2, correlation))
                    
                    if abs_corr >= self.correlation_threshold:
                        strong_correlations.append((col1, col2, correlation))
                    elif abs_corr > 0.1:
                        weak_correlations.append((col1, col2, correlation))
        
        return CorrelationAnalysis(
            method="pearson",
            correlation_matrix=corr_matrix,
            strong_correlations=strong_correlations,
            weak_correlations=weak_correlations,
            highly_correlated_pairs=highly_correlated_pairs
        )
    
    def _analyze_feature_importance(self, data: pd.DataFrame, target_column: str) -> FeatureImportanceAnalysis:
        """Analyze feature importance with respect to target column."""
        if target_column not in data.columns:
            raise ValueError(f"Target column '{target_column}' not found in dataset")
        
        # Separate features and target
        features = data.drop(columns=[target_column])
        target = data[target_column]
        
        # Handle missing values by dropping rows
        mask = ~(features.isnull().any(axis=1) | target.isnull())
        features_clean = features[mask]
        target_clean = target[mask]
        
        if len(features_clean) == 0:
            return FeatureImportanceAnalysis(
                target_column=target_column,
                feature_scores={},
                top_features=[],
                low_importance_features=[],
                method="mutual_info"
            )
        
        # Prepare features for mutual information
        X = features_clean.copy()
        
        # Encode categorical variables
        categorical_cols = X.select_dtypes(include=['object', 'category']).columns
        for col in categorical_cols:
            le = LabelEncoder()
            X[col] = le.fit_transform(X[col].astype(str))
        
        # Determine if target is classification or regression
        is_classification = (target_clean.dtype == 'object' or 
                           target_clean.dtype == 'category' or 
                           target_clean.nunique() < 10)
        
        # Calculate mutual information
        if is_classification:
            # Encode target for classification
            if target_clean.dtype in ['object', 'category']:
                le_target = LabelEncoder()
                target_encoded = le_target.fit_transform(target_clean.astype(str))
            else:
                target_encoded = target_clean
            
            scores = mutual_info_classif(X, target_encoded, random_state=42)
        else:
            scores = mutual_info_regression(X, target_clean, random_state=42)
        
        # Create feature importance dictionary
        feature_scores = dict(zip(X.columns, scores))
        
        # Sort features by importance
        sorted_features = sorted(feature_scores.items(), key=lambda x: x[1], reverse=True)
        top_features = sorted_features[:10]  # Top 10 features
        
        # Identify low importance features (bottom 25% or score < 0.01)
        score_threshold = max(0.01, np.percentile(scores, 25))
        low_importance_features = [col for col, score in feature_scores.items() 
                                 if score < score_threshold]
        
        return FeatureImportanceAnalysis(
            target_column=target_column,
            feature_scores=feature_scores,
            top_features=top_features,
            low_importance_features=low_importance_features,
            method="mutual_info"
        )
    
    def generate_summary_report(self, profile: DataProfile) -> str:
        """Generate a human-readable summary report."""
        report = []
        report.append(f"📊 Data Profile Report: {profile.dataset_name}")
        report.append("=" * 60)
        report.append(f"📈 Dataset Overview:")
        report.append(f"  • Rows: {profile.row_count:,}")
        report.append(f"  • Columns: {profile.column_count}")
        report.append(f"  • Memory Usage: {profile.memory_usage:.2f} MB")
        report.append(f"  • Duplicate Rows: {profile.duplicate_rows:,} ({profile.duplicate_percentage:.1f}%)")
        report.append(f"  • Overall Completeness: {profile.overall_completeness:.1f}%")
        report.append("")
        
        # Column type summary
        report.append(f"🔢 Column Types:")
        report.append(f"  • Numeric: {len(profile.numeric_columns)} columns")
        report.append(f"  • Categorical: {len(profile.categorical_columns)} columns")
        report.append(f"  • DateTime: {len(profile.datetime_columns)} columns")
        report.append(f"  • Boolean: {len(profile.boolean_columns)} columns")
        report.append("")
        
        # Data quality issues
        if profile.columns_with_missing or profile.constant_columns or profile.high_cardinality_columns:
            report.append(f"⚠️  Data Quality Issues:")
            if profile.columns_with_missing:
                report.append(f"  • Missing Values: {len(profile.columns_with_missing)} columns")
            if profile.constant_columns:
                report.append(f"  • Constant Values: {len(profile.constant_columns)} columns")
            if profile.high_cardinality_columns:
                report.append(f"  • High Cardinality: {len(profile.high_cardinality_columns)} columns")
            report.append("")
        
        # Correlation analysis
        if profile.correlation_analysis:
            corr = profile.correlation_analysis
            report.append(f"🔗 Correlation Analysis:")
            report.append(f"  • Strong Correlations: {len(corr.strong_correlations)} pairs")
            report.append(f"  • Highly Correlated: {len(corr.highly_correlated_pairs)} pairs (|r| > 0.8)")
            if corr.highly_correlated_pairs:
                report.append(f"  • Top Correlations:")
                for col1, col2, corr_val in corr.highly_correlated_pairs[:5]:
                    report.append(f"    - {col1} ↔ {col2}: {corr_val:.3f}")
            report.append("")
        
        # Feature importance
        if profile.feature_importance:
            fi = profile.feature_importance
            report.append(f"🎯 Feature Importance (Target: {fi.target_column}):")
            report.append(f"  • Method: {fi.method}")
            report.append(f"  • Top Features:")
            for feature, score in fi.top_features[:5]:
                report.append(f"    - {feature}: {score:.4f}")
            if fi.low_importance_features:
                report.append(f"  • Low Importance: {len(fi.low_importance_features)} features")
            report.append("")
        
        return "\n".join(report)


def profile_dataset(data: pd.DataFrame, 
                   dataset_name: str = "dataset",
                   target_column: Optional[str] = None,
                   profile_type: ProfileType = ProfileType.COMPREHENSIVE) -> DataProfile:
    """
    Quick function to profile a dataset.
    
    Args:
        data: DataFrame to profile
        dataset_name: Name of the dataset
        target_column: Target column for supervised learning analysis
        profile_type: Type of profiling to perform
        
    Returns:
        DataProfile object with analysis results
    """
    profiler = DataProfiler()
    return profiler.profile_dataset(data, dataset_name, profile_type, target_column)


def generate_profile_report(data: pd.DataFrame, 
                          dataset_name: str = "dataset",
                          target_column: Optional[str] = None) -> str:
    """
    Generate a comprehensive profile report.
    
    Args:
        data: DataFrame to profile
        dataset_name: Name of the dataset
        target_column: Target column for supervised learning analysis
        
    Returns:
        Human-readable profile report
    """
    profile = profile_dataset(data, dataset_name, target_column)
    profiler = DataProfiler()
    return profiler.generate_summary_report(profile)


def compare_datasets(data1: pd.DataFrame, 
                    data2: pd.DataFrame,
                    dataset1_name: str = "dataset1",
                    dataset2_name: str = "dataset2") -> Dict[str, Any]:
    """
    Compare two datasets and highlight differences.
    
    Args:
        data1: First dataset
        data2: Second dataset
        dataset1_name: Name of first dataset
        dataset2_name: Name of second dataset
        
    Returns:
        Dictionary with comparison results
    """
    profile1 = profile_dataset(data1, dataset1_name)
    profile2 = profile_dataset(data2, dataset2_name)
    
    comparison = {
        "dataset_names": [dataset1_name, dataset2_name],
        "shape_comparison": {
            dataset1_name: (profile1.row_count, profile1.column_count),
            dataset2_name: (profile2.row_count, profile2.column_count)
        },
        "column_differences": {
            "common_columns": list(set(data1.columns) & set(data2.columns)),
            "unique_to_dataset1": list(set(data1.columns) - set(data2.columns)),
            "unique_to_dataset2": list(set(data2.columns) - set(data1.columns))
        },
        "completeness_comparison": {
            dataset1_name: profile1.overall_completeness,
            dataset2_name: profile2.overall_completeness
        },
        "type_distribution": {
            dataset1_name: {
                "numeric": len(profile1.numeric_columns),
                "categorical": len(profile1.categorical_columns)
            },
            dataset2_name: {
                "numeric": len(profile2.numeric_columns),
                "categorical": len(profile2.categorical_columns)
            }
        }
    }
    
    return comparison 