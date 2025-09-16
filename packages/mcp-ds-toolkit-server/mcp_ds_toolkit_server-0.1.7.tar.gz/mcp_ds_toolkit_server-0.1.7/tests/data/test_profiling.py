"""
Tests for data profiling and statistical analysis module.
"""

import os
import tempfile
from unittest.mock import MagicMock, patch

import numpy as np
import pandas as pd
import pytest

from mcp_ds_toolkit_server.data.profiling import (
    ColumnProfile,
    CorrelationAnalysis,
    DataProfile,
    DataProfiler,
    DistributionType,
    FeatureImportanceAnalysis,
    ProfileType,
    compare_datasets,
    generate_profile_report,
    profile_dataset,
)


class TestDataProfiler:
    """Test DataProfiler class."""
    
    def test_init_default(self):
        """Test DataProfiler initialization with default parameters."""
        profiler = DataProfiler()
        assert profiler.high_cardinality_threshold == 0.95
        assert profiler.outlier_method == 'iqr'
        assert profiler.correlation_threshold == 0.5
    
    def test_init_custom(self):
        """Test DataProfiler initialization with custom parameters."""
        profiler = DataProfiler(
            high_cardinality_threshold=0.8,
            outlier_method='zscore',
            correlation_threshold=0.7
        )
        assert profiler.high_cardinality_threshold == 0.8
        assert profiler.outlier_method == 'zscore'
        assert profiler.correlation_threshold == 0.7
    
    def test_profile_empty_dataset(self):
        """Test profiling empty dataset."""
        profiler = DataProfiler()
        data = pd.DataFrame()
        profile = profiler.profile_dataset(data, "empty_dataset")
        
        assert profile.dataset_name == "empty_dataset"
        assert profile.row_count == 0
        assert profile.column_count == 0
        assert profile.duplicate_rows == 0
        assert profile.overall_completeness == 100.0
        assert len(profile.column_profiles) == 0
    
    def test_profile_basic_dataset(self):
        """Test profiling basic dataset."""
        profiler = DataProfiler()
        data = pd.DataFrame({
            'numeric': [1, 2, 3, 4, 5],
            'categorical': ['A', 'B', 'A', 'C', 'B'],
            'with_nulls': [1, 2, np.nan, 4, 5],
            'constant': [1, 1, 1, 1, 1]
        })
        
        profile = profiler.profile_dataset(data, "test_dataset")
        
        assert profile.dataset_name == "test_dataset"
        assert profile.row_count == 5
        assert profile.column_count == 4
        assert profile.duplicate_rows == 0
        assert len(profile.column_profiles) == 4
        assert len(profile.numeric_columns) == 3  # numeric, with_nulls, constant
        assert len(profile.categorical_columns) == 1  # categorical
        assert 'with_nulls' in profile.columns_with_missing
        assert 'constant' in profile.constant_columns
    
    def test_profile_column_numeric(self):
        """Test column profiling for numeric data."""
        profiler = DataProfiler()
        data = pd.DataFrame({'numeric': [1, 2, 3, 4, 5, 100]})  # 100 is an outlier
        
        column_profile = profiler._profile_column(data, 'numeric')
        
        assert column_profile.name == 'numeric'
        assert column_profile.dtype == 'int64'
        assert column_profile.null_count == 0
        assert column_profile.unique_count == 6
        assert column_profile.mean == pytest.approx(19.17, rel=1e-2)
        assert column_profile.median == 3.5
        assert column_profile.min_value == 1
        assert column_profile.max_value == 100
        assert column_profile.has_outliers == True
        assert column_profile.outlier_count > 0
    
    def test_profile_column_categorical(self):
        """Test column profiling for categorical data."""
        profiler = DataProfiler()
        data = pd.DataFrame({'categorical': ['A', 'B', 'A', 'C', 'B', 'A']})
        
        column_profile = profiler._profile_column(data, 'categorical')
        
        assert column_profile.name == 'categorical'
        assert column_profile.dtype == 'object'
        assert column_profile.null_count == 0
        assert column_profile.unique_count == 3
        assert column_profile.most_frequent_value == 'A'
        assert column_profile.most_frequent_count == 3
        assert column_profile.top_categories == {'A': 3, 'B': 2, 'C': 1}
    
    def test_profile_column_with_nulls(self):
        """Test column profiling with null values."""
        profiler = DataProfiler()
        data = pd.DataFrame({'with_nulls': [1, 2, np.nan, 4, np.nan]})
        
        column_profile = profiler._profile_column(data, 'with_nulls')
        
        assert column_profile.name == 'with_nulls'
        assert column_profile.null_count == 2
        assert column_profile.null_percentage == 40.0
        assert column_profile.unique_count == 3  # 1, 2, 4
    
    def test_profile_column_constant(self):
        """Test column profiling for constant values."""
        profiler = DataProfiler()
        data = pd.DataFrame({'constant': [5, 5, 5, 5, 5]})
        
        column_profile = profiler._profile_column(data, 'constant')
        
        assert column_profile.name == 'constant'
        assert column_profile.unique_count == 1
        assert column_profile.is_constant == True
        assert column_profile.most_frequent_value == 5
        assert column_profile.most_frequent_count == 5
    
    def test_profile_column_high_cardinality(self):
        """Test column profiling for high cardinality data."""
        profiler = DataProfiler()
        # Create data with high cardinality (each value unique)
        data = pd.DataFrame({'high_card': list(range(100))})
        
        column_profile = profiler._profile_column(data, 'high_card')
        
        assert column_profile.name == 'high_card'
        assert column_profile.unique_count == 100
        assert column_profile.unique_percentage == 100.0
        assert column_profile.has_high_cardinality == True
    
    def test_profile_column_empty(self):
        """Test column profiling for empty data."""
        profiler = DataProfiler()
        data = pd.DataFrame({'empty': []})
        
        column_profile = profiler._profile_column(data, 'empty')
        
        assert column_profile.name == 'empty'
        assert column_profile.unique_count == 0
        assert column_profile.is_constant == True
        assert column_profile.most_frequent_value is None
        assert column_profile.most_frequent_count == 0
    
    def test_analyze_distribution_normal(self):
        """Test distribution analysis for normal data."""
        profiler = DataProfiler()
        # Generate normal distribution
        np.random.seed(42)
        data = pd.Series(np.random.normal(0, 1, 1000))
        
        dist_type = profiler._analyze_distribution(data)
        # Note: with random data, this might not always be NORMAL
        assert dist_type in [DistributionType.NORMAL, DistributionType.UNKNOWN]
    
    def test_analyze_distribution_skewed(self):
        """Test distribution analysis for skewed data."""
        profiler = DataProfiler()
        # Generate skewed data
        data = pd.Series([1, 1, 1, 1, 1, 2, 2, 3, 10, 50])
        
        dist_type = profiler._analyze_distribution(data)
        assert dist_type == DistributionType.SKEWED
    
    def test_analyze_distribution_small_sample(self):
        """Test distribution analysis for small sample."""
        profiler = DataProfiler()
        data = pd.Series([1, 2])
        
        dist_type = profiler._analyze_distribution(data)
        assert dist_type == DistributionType.UNKNOWN
    
    def test_detect_outliers_iqr(self):
        """Test outlier detection using IQR method."""
        profiler = DataProfiler(outlier_method='iqr')
        data = pd.Series([1, 2, 3, 4, 5, 100])  # 100 is an outlier
        
        outliers = profiler._detect_outliers(data)
        assert len(outliers) > 0
    
    def test_detect_outliers_zscore(self):
        """Test outlier detection using Z-score method."""
        profiler = DataProfiler(outlier_method='zscore')
        data = pd.Series([1, 2, 3, 4, 5, 1000])  # 1000 is an extreme outlier
        
        outliers = profiler._detect_outliers(data)
        assert len(outliers) > 0
    
    def test_detect_outliers_empty(self):
        """Test outlier detection with empty data."""
        profiler = DataProfiler()
        data = pd.Series([])
        
        outliers = profiler._detect_outliers(data)
        assert len(outliers) == 0
    
    def test_analyze_correlations(self):
        """Test correlation analysis."""
        profiler = DataProfiler()
        # Create correlated data
        np.random.seed(42)
        x = np.random.normal(0, 1, 100)
        y = 2 * x + np.random.normal(0, 0.1, 100)  # Strong correlation
        z = np.random.normal(0, 1, 100)  # No correlation
        
        data = pd.DataFrame({'x': x, 'y': y, 'z': z})
        
        corr_analysis = profiler._analyze_correlations(data)
        
        assert corr_analysis.method == "pearson"
        assert corr_analysis.correlation_matrix.shape == (3, 3)
        assert len(corr_analysis.strong_correlations) > 0
        assert len(corr_analysis.highly_correlated_pairs) > 0
    
    def test_analyze_correlations_single_column(self):
        """Test correlation analysis with single column."""
        profiler = DataProfiler()
        data = pd.DataFrame({'x': [1, 2, 3, 4, 5]})
        
        corr_analysis = profiler._analyze_correlations(data)
        
        assert corr_analysis.method == "pearson"
        assert corr_analysis.correlation_matrix.empty
        assert len(corr_analysis.strong_correlations) == 0
    
    def test_analyze_feature_importance_classification(self):
        """Test feature importance analysis for classification."""
        profiler = DataProfiler()
        # Create classification data
        np.random.seed(42)
        x1 = np.random.normal(0, 1, 100)
        x2 = np.random.normal(0, 1, 100)
        y = (x1 + x2 > 0).astype(int)  # Binary classification
        
        data = pd.DataFrame({'x1': x1, 'x2': x2, 'target': y})
        
        fi_analysis = profiler._analyze_feature_importance(data, 'target')
        
        assert fi_analysis.target_column == 'target'
        assert fi_analysis.method == "mutual_info"
        assert len(fi_analysis.feature_scores) == 2
        assert len(fi_analysis.top_features) <= 2
    
    def test_analyze_feature_importance_regression(self):
        """Test feature importance analysis for regression."""
        profiler = DataProfiler()
        # Create regression data
        np.random.seed(42)
        x1 = np.random.normal(0, 1, 100)
        x2 = np.random.normal(0, 1, 100)
        y = 2 * x1 + 3 * x2 + np.random.normal(0, 0.1, 100)  # Continuous target
        
        data = pd.DataFrame({'x1': x1, 'x2': x2, 'target': y})
        
        fi_analysis = profiler._analyze_feature_importance(data, 'target')
        
        assert fi_analysis.target_column == 'target'
        assert fi_analysis.method == "mutual_info"
        assert len(fi_analysis.feature_scores) == 2
    
    def test_analyze_feature_importance_missing_target(self):
        """Test feature importance analysis with missing target."""
        profiler = DataProfiler()
        data = pd.DataFrame({'x1': [1, 2, 3], 'x2': [4, 5, 6]})
        
        with pytest.raises(ValueError, match="Target column 'missing' not found"):
            profiler._analyze_feature_importance(data, 'missing')
    
    def test_analyze_feature_importance_empty_data(self):
        """Test feature importance analysis with empty clean data."""
        profiler = DataProfiler()
        data = pd.DataFrame({
            'x1': [np.nan, np.nan, np.nan],
            'target': [np.nan, np.nan, np.nan]
        })
        
        fi_analysis = profiler._analyze_feature_importance(data, 'target')
        
        assert fi_analysis.target_column == 'target'
        assert len(fi_analysis.feature_scores) == 0
        assert len(fi_analysis.top_features) == 0
    
    def test_profile_dataset_comprehensive(self):
        """Test comprehensive dataset profiling."""
        profiler = DataProfiler()
        # Create comprehensive test data
        np.random.seed(42)
        data = pd.DataFrame({
            'numeric1': np.random.normal(0, 1, 100),
            'numeric2': np.random.normal(5, 2, 100),
            'categorical': np.random.choice(['A', 'B', 'C'], 100),
            'target': np.random.choice([0, 1], 100)
        })
        
        profile = profiler.profile_dataset(
            data, 
            "comprehensive_test",
            ProfileType.COMPREHENSIVE,
            'target'
        )
        
        assert profile.dataset_name == "comprehensive_test"
        assert profile.row_count == 100
        assert profile.column_count == 4
        assert profile.correlation_analysis is not None
        assert profile.feature_importance is not None
        assert len(profile.numeric_columns) == 3  # numeric1, numeric2, target
        assert len(profile.categorical_columns) == 1  # categorical
    
    def test_profile_dataset_basic_type(self):
        """Test basic dataset profiling."""
        profiler = DataProfiler()
        data = pd.DataFrame({'x': [1, 2, 3], 'y': [4, 5, 6]})
        
        profile = profiler.profile_dataset(data, "basic_test", ProfileType.BASIC)
        
        assert profile.dataset_name == "basic_test"
        assert profile.correlation_analysis is None
        assert profile.feature_importance is None
    
    def test_profile_dataset_correlation_type(self):
        """Test correlation-only dataset profiling."""
        profiler = DataProfiler()
        data = pd.DataFrame({'x': [1, 2, 3], 'y': [4, 5, 6]})
        
        profile = profiler.profile_dataset(data, "corr_test", ProfileType.CORRELATION)
        
        assert profile.dataset_name == "corr_test"
        assert profile.correlation_analysis is not None
        assert profile.feature_importance is None
    
    def test_generate_summary_report(self):
        """Test summary report generation."""
        profiler = DataProfiler()
        data = pd.DataFrame({
            'numeric': [1, 2, 3, 4, 5],
            'categorical': ['A', 'B', 'A', 'C', 'B'],
            'with_nulls': [1, 2, np.nan, 4, 5]
        })
        
        profile = profiler.profile_dataset(data, "report_test")
        report = profiler.generate_summary_report(profile)
        
        assert "📊 Data Profile Report: report_test" in report
        assert "Rows: 5" in report
        assert "Columns: 3" in report
        assert "Missing Values: 1 columns" in report
        assert "Numeric: 2 columns" in report
        assert "Categorical: 1 columns" in report


class TestStandaloneFunctions:
    """Test standalone utility functions."""
    
    def test_profile_dataset_function(self):
        """Test profile_dataset standalone function."""
        data = pd.DataFrame({
            'x': [1, 2, 3, 4, 5],
            'y': ['A', 'B', 'A', 'C', 'B']
        })
        
        profile = profile_dataset(data, "function_test")
        
        assert profile.dataset_name == "function_test"
        assert profile.row_count == 5
        assert profile.column_count == 2
    
    def test_profile_dataset_function_with_target(self):
        """Test profile_dataset function with target column."""
        data = pd.DataFrame({
            'x': [1, 2, 3, 4, 5],
            'y': [0, 1, 0, 1, 0]
        })
        
        profile = profile_dataset(data, "function_target_test", 'y')
        
        assert profile.dataset_name == "function_target_test"
        assert profile.feature_importance is not None
        assert profile.feature_importance.target_column == 'y'
    
    def test_generate_profile_report_function(self):
        """Test generate_profile_report standalone function."""
        data = pd.DataFrame({
            'x': [1, 2, 3, 4, 5],
            'y': ['A', 'B', 'A', 'C', 'B']
        })
        
        report = generate_profile_report(data, "report_function_test")
        
        assert "📊 Data Profile Report: report_function_test" in report
        assert "Rows: 5" in report
        assert "Columns: 2" in report
    
    def test_compare_datasets_function(self):
        """Test compare_datasets standalone function."""
        data1 = pd.DataFrame({
            'x': [1, 2, 3],
            'y': ['A', 'B', 'C']
        })
        
        data2 = pd.DataFrame({
            'x': [4, 5, 6, 7],
            'y': ['A', 'B', 'C', 'D'],
            'z': [1, 2, 3, 4]
        })
        
        comparison = compare_datasets(data1, data2, "dataset1", "dataset2")
        
        assert comparison['dataset_names'] == ["dataset1", "dataset2"]
        assert comparison['shape_comparison']['dataset1'] == (3, 2)
        assert comparison['shape_comparison']['dataset2'] == (4, 3)
        assert set(comparison['column_differences']['common_columns']) == {'x', 'y'}
        assert comparison['column_differences']['unique_to_dataset2'] == ['z']
        assert comparison['column_differences']['unique_to_dataset1'] == []


class TestDataClasses:
    """Test data classes and enums."""
    
    def test_profile_type_enum(self):
        """Test ProfileType enum."""
        assert ProfileType.BASIC.value == "basic"
        assert ProfileType.STATISTICAL.value == "statistical"
        assert ProfileType.CORRELATION.value == "correlation"
        assert ProfileType.FEATURE_IMPORTANCE.value == "feature_importance"
        assert ProfileType.COMPREHENSIVE.value == "comprehensive"
    
    def test_distribution_type_enum(self):
        """Test DistributionType enum."""
        assert DistributionType.NORMAL.value == "normal"
        assert DistributionType.UNIFORM.value == "uniform"
        assert DistributionType.EXPONENTIAL.value == "exponential"
        assert DistributionType.SKEWED.value == "skewed"
        assert DistributionType.BIMODAL.value == "bimodal"
        assert DistributionType.UNKNOWN.value == "unknown"
    
    def test_column_profile_dataclass(self):
        """Test ColumnProfile dataclass."""
        profile = ColumnProfile(
            name="test_column",
            dtype="int64",
            null_count=5,
            null_percentage=10.0,
            unique_count=50,
            unique_percentage=90.0,
            most_frequent_value=42,
            most_frequent_count=3
        )
        
        assert profile.name == "test_column"
        assert profile.dtype == "int64"
        assert profile.null_count == 5
        assert profile.null_percentage == 10.0
        assert profile.unique_count == 50
        assert profile.unique_percentage == 90.0
        assert profile.most_frequent_value == 42
        assert profile.most_frequent_count == 3
        assert profile.mean is None  # Default value
        assert profile.has_outliers is False  # Default value
    
    def test_correlation_analysis_dataclass(self):
        """Test CorrelationAnalysis dataclass."""
        corr_matrix = pd.DataFrame([[1.0, 0.8], [0.8, 1.0]], 
                                  columns=['x', 'y'], 
                                  index=['x', 'y'])
        
        analysis = CorrelationAnalysis(
            method="pearson",
            correlation_matrix=corr_matrix,
            strong_correlations=[('x', 'y', 0.8)],
            weak_correlations=[],
            highly_correlated_pairs=[('x', 'y', 0.8)]
        )
        
        assert analysis.method == "pearson"
        assert analysis.correlation_matrix.shape == (2, 2)
        assert len(analysis.strong_correlations) == 1
        assert len(analysis.highly_correlated_pairs) == 1
    
    def test_feature_importance_analysis_dataclass(self):
        """Test FeatureImportanceAnalysis dataclass."""
        analysis = FeatureImportanceAnalysis(
            target_column="target",
            feature_scores={"x": 0.8, "y": 0.6},
            top_features=[("x", 0.8), ("y", 0.6)],
            low_importance_features=[],
            method="mutual_info"
        )
        
        assert analysis.target_column == "target"
        assert analysis.feature_scores == {"x": 0.8, "y": 0.6}
        assert analysis.top_features == [("x", 0.8), ("y", 0.6)]
        assert analysis.low_importance_features == []
        assert analysis.method == "mutual_info"
    
    def test_data_profile_dataclass(self):
        """Test DataProfile dataclass."""
        profile = DataProfile(
            dataset_name="test",
            row_count=100,
            column_count=5,
            memory_usage=1.5,
            duplicate_rows=2,
            duplicate_percentage=2.0,
            column_profiles={},
            numeric_columns=["x", "y"],
            categorical_columns=["z"],
            datetime_columns=[],
            boolean_columns=[]
        )
        
        assert profile.dataset_name == "test"
        assert profile.row_count == 100
        assert profile.column_count == 5
        assert profile.memory_usage == 1.5
        assert profile.duplicate_rows == 2
        assert profile.duplicate_percentage == 2.0
        assert profile.numeric_columns == ["x", "y"]
        assert profile.categorical_columns == ["z"]
        assert profile.overall_completeness == 0.0  # Default value
        assert profile.columns_with_missing is None  # Default value


class TestEdgeCases:
    """Test edge cases and error conditions."""
    
    def test_profile_single_row_dataset(self):
        """Test profiling dataset with single row."""
        profiler = DataProfiler()
        data = pd.DataFrame({'x': [1], 'y': ['A']})
        
        profile = profiler.profile_dataset(data, "single_row")
        
        assert profile.row_count == 1
        assert profile.column_count == 2
        assert profile.duplicate_rows == 0
    
    def test_profile_all_null_column(self):
        """Test profiling column with all null values."""
        profiler = DataProfiler()
        data = pd.DataFrame({'all_null': [np.nan, np.nan, np.nan]})
        
        profile = profiler.profile_dataset(data, "all_null_test")
        
        column_profile = profile.column_profiles['all_null']
        assert column_profile.null_count == 3
        assert column_profile.null_percentage == 100.0
        assert column_profile.unique_count == 0
    
    def test_profile_mixed_types_column(self):
        """Test profiling column with mixed data types."""
        profiler = DataProfiler()
        data = pd.DataFrame({'mixed': [1, 'A', 2.5, 'B', None]})
        
        profile = profiler.profile_dataset(data, "mixed_types")
        
        column_profile = profile.column_profiles['mixed']
        assert column_profile.dtype == 'object'
        assert column_profile.null_count == 1
        assert column_profile.unique_count == 4
    
    def test_profile_very_large_dataset_simulation(self):
        """Test profiling simulation of large dataset."""
        profiler = DataProfiler()
        # Simulate large dataset characteristics
        np.random.seed(42)
        data = pd.DataFrame({
            'x': np.random.normal(0, 1, 10000),
            'y': np.random.choice(['A', 'B', 'C'], 10000)
        })
        
        profile = profiler.profile_dataset(data, "large_dataset")
        
        assert profile.row_count == 10000
        assert profile.column_count == 2
        assert profile.memory_usage > 0
        assert len(profile.column_profiles) == 2
    
    def test_correlation_with_nan_values(self):
        """Test correlation analysis with NaN values."""
        profiler = DataProfiler()
        data = pd.DataFrame({
            'x': [1, 2, np.nan, 4, 5],
            'y': [2, 4, 6, np.nan, 10]
        })
        
        corr_analysis = profiler._analyze_correlations(data)
        
        assert corr_analysis.method == "pearson"
        assert corr_analysis.correlation_matrix.shape == (2, 2)
        # Should handle NaN values gracefully
    
    def test_feature_importance_with_categorical_features(self):
        """Test feature importance with categorical features."""
        profiler = DataProfiler()
        data = pd.DataFrame({
            'numeric': [1, 2, 3, 4, 5],
            'categorical': ['A', 'B', 'A', 'B', 'C'],
            'target': [0, 1, 0, 1, 0]
        })
        
        fi_analysis = profiler._analyze_feature_importance(data, 'target')
        
        assert fi_analysis.target_column == 'target'
        assert len(fi_analysis.feature_scores) == 2
        assert 'numeric' in fi_analysis.feature_scores
        assert 'categorical' in fi_analysis.feature_scores 