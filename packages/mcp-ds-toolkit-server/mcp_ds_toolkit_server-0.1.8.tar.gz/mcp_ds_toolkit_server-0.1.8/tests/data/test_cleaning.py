"""
Tests for the data cleaning module.
"""

from unittest.mock import MagicMock, patch

import numpy as np
import pandas as pd
import pytest

from mcp_ds_toolkit_server.data.cleaning import (
    CleaningConfig,
    DataCleaner,
    MissingDataConfig,
    MissingDataHandler,
    MissingDataMethod,
    OutlierAction,
    OutlierConfig,
    OutlierDetector,
    OutlierMethod,
    analyze_missing_data,
    clean_dataset,
    detect_outliers,
)


class TestMissingDataHandler:
    """Test cases for MissingDataHandler."""
    
    def test_missing_data_handler_initialization(self):
        """Test MissingDataHandler initialization."""
        handler = MissingDataHandler()
        assert handler.config.method == MissingDataMethod.FILL_MEDIAN
        assert handler.config.drop_threshold == 0.5
        assert handler.config.knn_neighbors == 5
        assert handler.imputer is None
        assert handler.fitted_values == {}
    
    def test_missing_data_handler_custom_config(self):
        """Test MissingDataHandler with custom configuration."""
        config = MissingDataConfig(
            method=MissingDataMethod.FILL_MEAN,
            drop_threshold=0.3,
            knn_neighbors=7
        )
        handler = MissingDataHandler(config)
        assert handler.config.method == MissingDataMethod.FILL_MEAN
        assert handler.config.drop_threshold == 0.3
        assert handler.config.knn_neighbors == 7
    
    def test_analyze_missing_data_no_missing(self):
        """Test analyze_missing_data with no missing values."""
        df = pd.DataFrame({
            'a': [1, 2, 3, 4, 5],
            'b': [6, 7, 8, 9, 10],
            'c': ['x', 'y', 'z', 'w', 'v']
        })
        
        handler = MissingDataHandler()
        report = handler.analyze_missing_data(df)
        
        assert report.total_missing == 0
        assert report.missing_percentage == 0.0
        assert report.missing_by_column == {'a': 0, 'b': 0, 'c': 0}
        assert report.missing_percentage_by_column == {'a': 0.0, 'b': 0.0, 'c': 0.0}
        assert report.columns_with_missing == []
        assert len(report.recommendations) > 0
    
    def test_analyze_missing_data_with_missing(self):
        """Test analyze_missing_data with missing values."""
        df = pd.DataFrame({
            'a': [1, 2, np.nan, 4, 5],
            'b': [6, np.nan, 8, np.nan, 10],
            'c': ['x', 'y', None, 'w', 'v']
        })
        
        handler = MissingDataHandler()
        report = handler.analyze_missing_data(df)
        
        assert report.total_missing == 4
        assert report.missing_percentage == (4 / 15) * 100
        assert report.missing_by_column == {'a': 1, 'b': 2, 'c': 1}
        assert report.columns_with_missing == ['a', 'b', 'c']
        assert len(report.recommendations) > 0
    
    def test_handle_missing_data_drop_rows(self):
        """Test handling missing data by dropping rows."""
        df = pd.DataFrame({
            'a': [1, 2, np.nan, 4, 5],
            'b': [6, np.nan, 8, np.nan, 10],
            'c': ['x', 'y', 'z', 'w', 'v']
        })
        
        config = MissingDataConfig(
            method=MissingDataMethod.DROP_ROWS,
            drop_threshold=0.3  # Drop rows with more than 30% missing
        )
        handler = MissingDataHandler(config)
        
        result = handler.handle_missing_data(df)
        
        # Should have fewer rows due to dropping
        assert len(result) <= len(df)
        assert result.isnull().sum().sum() <= df.isnull().sum().sum()
    
    def test_handle_missing_data_drop_columns(self):
        """Test handling missing data by dropping columns."""
        df = pd.DataFrame({
            'a': [1, 2, np.nan, 4, 5],
            'b': [np.nan, np.nan, np.nan, np.nan, 10],  # High missing percentage
            'c': ['x', 'y', 'z', 'w', 'v']
        })
        
        config = MissingDataConfig(
            method=MissingDataMethod.DROP_COLUMNS,
            drop_threshold=0.5  # Drop columns with more than 50% missing
        )
        handler = MissingDataHandler(config)
        
        result = handler.handle_missing_data(df)
        
        # Should have fewer columns due to dropping
        assert len(result.columns) <= len(df.columns)
        # Column 'b' should be dropped
        assert 'b' not in result.columns
    
    def test_handle_missing_data_fill_mean(self):
        """Test handling missing data by filling with mean."""
        df = pd.DataFrame({
            'a': [1, 2, np.nan, 4, 5],
            'b': [6, np.nan, 8, np.nan, 10],
            'c': ['x', 'y', None, 'w', 'v']
        })
        
        config = MissingDataConfig(method=MissingDataMethod.FILL_MEAN)
        handler = MissingDataHandler(config)
        
        result = handler.handle_missing_data(df)
        
        # Numeric columns should have no missing values
        assert result['a'].isnull().sum() == 0
        assert result['b'].isnull().sum() == 0
        # String column should still have missing values
        assert result['c'].isnull().sum() == 1
    
    def test_handle_missing_data_fill_median(self):
        """Test handling missing data by filling with median."""
        df = pd.DataFrame({
            'a': [1, 2, np.nan, 4, 5],
            'b': [6, np.nan, 8, np.nan, 10],
            'c': ['x', 'y', None, 'w', 'v']
        })
        
        config = MissingDataConfig(method=MissingDataMethod.FILL_MEDIAN)
        handler = MissingDataHandler(config)
        
        result = handler.handle_missing_data(df)
        
        # Numeric columns should have no missing values
        assert result['a'].isnull().sum() == 0
        assert result['b'].isnull().sum() == 0
        # String column should still have missing values
        assert result['c'].isnull().sum() == 1
    
    def test_handle_missing_data_fill_mode(self):
        """Test handling missing data by filling with mode."""
        df = pd.DataFrame({
            'a': [1, 2, np.nan, 2, 2],
            'b': [6, np.nan, 8, np.nan, 8],
            'c': ['x', 'y', None, 'x', 'x']
        })
        
        config = MissingDataConfig(method=MissingDataMethod.FILL_MODE)
        handler = MissingDataHandler(config)
        
        result = handler.handle_missing_data(df)
        
        # All columns should have no missing values
        assert result.isnull().sum().sum() == 0
        # Filled values should be modes
        assert result.loc[2, 'a'] == 2  # mode of 'a'
        assert result.loc[2, 'c'] == 'x'  # mode of 'c'
    
    def test_handle_missing_data_fill_constant(self):
        """Test handling missing data by filling with constant."""
        df = pd.DataFrame({
            'a': [1, 2, np.nan, 4, 5],
            'b': [6, np.nan, 8, np.nan, 10],
            'c': ['x', 'y', None, 'w', 'v']
        })
        
        config = MissingDataConfig(
            method=MissingDataMethod.FILL_CONSTANT,
            constant_value=-999
        )
        handler = MissingDataHandler(config)
        
        result = handler.handle_missing_data(df)
        
        # All missing values should be replaced with constant
        assert result.isnull().sum().sum() == 0
        assert result.loc[2, 'a'] == -999
        assert result.loc[2, 'c'] == -999
    
    def test_handle_missing_data_fill_forward(self):
        """Test handling missing data by forward fill."""
        df = pd.DataFrame({
            'a': [1, 2, np.nan, 4, 5],
            'b': [6, np.nan, 8, np.nan, 10],
            'c': ['x', 'y', None, 'w', 'v']
        })
        
        config = MissingDataConfig(method=MissingDataMethod.FILL_FORWARD)
        handler = MissingDataHandler(config)
        
        result = handler.handle_missing_data(df)
        
        # Forward fill should reduce missing values
        assert result.isnull().sum().sum() <= df.isnull().sum().sum()
    
    def test_handle_missing_data_fill_backward(self):
        """Test handling missing data by backward fill."""
        df = pd.DataFrame({
            'a': [1, 2, np.nan, 4, 5],
            'b': [6, np.nan, 8, np.nan, 10],
            'c': ['x', 'y', None, 'w', 'v']
        })
        
        config = MissingDataConfig(method=MissingDataMethod.FILL_BACKWARD)
        handler = MissingDataHandler(config)
        
        result = handler.handle_missing_data(df)
        
        # Backward fill should reduce missing values
        assert result.isnull().sum().sum() <= df.isnull().sum().sum()
    
    def test_handle_missing_data_interpolate(self):
        """Test handling missing data by interpolation."""
        df = pd.DataFrame({
            'a': [1, 2, np.nan, 4, 5],
            'b': [6, np.nan, 8, np.nan, 10],
            'c': ['x', 'y', None, 'w', 'v']
        })
        
        config = MissingDataConfig(method=MissingDataMethod.FILL_INTERPOLATE)
        handler = MissingDataHandler(config)
        
        result = handler.handle_missing_data(df)
        
        # Numeric columns should have no missing values
        assert result['a'].isnull().sum() == 0
        assert result['b'].isnull().sum() == 0
        # String column should still have missing values
        assert result['c'].isnull().sum() == 1
    
    def test_handle_missing_data_knn(self):
        """Test handling missing data by KNN imputation."""
        df = pd.DataFrame({
            'a': [1, 2, np.nan, 4, 5],
            'b': [6, np.nan, 8, np.nan, 10],
            'c': ['x', 'y', None, 'w', 'v']
        })
        
        config = MissingDataConfig(method=MissingDataMethod.FILL_KNN)
        handler = MissingDataHandler(config)
        
        result = handler.handle_missing_data(df)
        
        # All columns should have no missing values
        assert result.isnull().sum().sum() == 0
    
    def test_handle_missing_data_iterative(self):
        """Test handling missing data by iterative imputation."""
        df = pd.DataFrame({
            'a': [1, 2, np.nan, 4, 5],
            'b': [6, np.nan, 8, np.nan, 10],
            'c': ['x', 'y', None, 'w', 'v']
        })
        
        config = MissingDataConfig(method=MissingDataMethod.FILL_ITERATIVE)
        handler = MissingDataHandler(config)
        
        result = handler.handle_missing_data(df)
        
        # All columns should have no missing values
        assert result.isnull().sum().sum() == 0
    
    def test_handle_missing_data_leave_as_is(self):
        """Test handling missing data by leaving as is."""
        df = pd.DataFrame({
            'a': [1, 2, np.nan, 4, 5],
            'b': [6, np.nan, 8, np.nan, 10],
            'c': ['x', 'y', None, 'w', 'v']
        })
        
        config = MissingDataConfig(method=MissingDataMethod.LEAVE_AS_IS)
        handler = MissingDataHandler(config)
        
        result = handler.handle_missing_data(df)
        
        # Should be identical to original
        pd.testing.assert_frame_equal(result, df)


class TestOutlierDetector:
    """Test cases for OutlierDetector."""
    
    def test_outlier_detector_initialization(self):
        """Test OutlierDetector initialization."""
        detector = OutlierDetector()
        assert detector.config.method == OutlierMethod.IQR
        assert detector.config.action == OutlierAction.CAP
        assert detector.config.z_threshold == 3.0
        assert detector.config.iqr_multiplier == 1.5
        assert detector.fitted_params == {}
        assert detector.scaler is None
    
    def test_outlier_detector_custom_config(self):
        """Test OutlierDetector with custom configuration."""
        config = OutlierConfig(
            method=OutlierMethod.Z_SCORE,
            action=OutlierAction.REMOVE,
            z_threshold=2.5,
            iqr_multiplier=2.0
        )
        detector = OutlierDetector(config)
        assert detector.config.method == OutlierMethod.Z_SCORE
        assert detector.config.action == OutlierAction.REMOVE
        assert detector.config.z_threshold == 2.5
        assert detector.config.iqr_multiplier == 2.0
    
    def test_detect_outliers_z_score(self):
        """Test outlier detection using Z-score method."""
        # Create data with outliers
        df = pd.DataFrame({
            'a': [1, 2, 3, 4, 5, 100],  # 100 is an outlier
            'b': [6, 7, 8, 9, 10, 11],
            'c': ['x', 'y', 'z', 'w', 'v', 'u']
        })
        
        config = OutlierConfig(method=OutlierMethod.Z_SCORE, z_threshold=2.0)
        detector = OutlierDetector(config)
        
        report = detector.detect_outliers(df)
        
        assert report.total_outliers > 0
        assert report.method == "z_score"
        assert "z_threshold" in report.threshold_values
        assert len(report.recommendations) > 0
    
    def test_detect_outliers_modified_z_score(self):
        """Test outlier detection using Modified Z-score method."""
        df = pd.DataFrame({
            'a': [1, 2, 3, 4, 5, 100],  # 100 is an outlier
            'b': [6, 7, 8, 9, 10, 11],
        })
        
        config = OutlierConfig(method=OutlierMethod.MODIFIED_Z_SCORE, z_threshold=2.0)
        detector = OutlierDetector(config)
        
        report = detector.detect_outliers(df)
        
        assert report.method == "modified_z_score"
        assert report.total_outliers >= 0
        assert len(report.recommendations) > 0
    
    def test_detect_outliers_iqr(self):
        """Test outlier detection using IQR method."""
        df = pd.DataFrame({
            'a': [1, 2, 3, 4, 5, 100],  # 100 is an outlier
            'b': [6, 7, 8, 9, 10, 11],
        })
        
        config = OutlierConfig(method=OutlierMethod.IQR, iqr_multiplier=1.5)
        detector = OutlierDetector(config)
        
        report = detector.detect_outliers(df)
        
        assert report.method == "iqr"
        assert report.total_outliers > 0
        assert len(report.recommendations) > 0
    
    def test_detect_outliers_isolation_forest(self):
        """Test outlier detection using Isolation Forest."""
        df = pd.DataFrame({
            'a': [1, 2, 3, 4, 5, 100],
            'b': [6, 7, 8, 9, 10, 11],
        })
        
        config = OutlierConfig(method=OutlierMethod.ISOLATION_FOREST, contamination=0.1)
        detector = OutlierDetector(config)
        
        report = detector.detect_outliers(df)
        
        assert report.method == "isolation_forest"
        assert report.total_outliers >= 0
        assert len(report.recommendations) > 0
    
    def test_detect_outliers_local_outlier_factor(self):
        """Test outlier detection using Local Outlier Factor."""
        df = pd.DataFrame({
            'a': [1, 2, 3, 4, 5, 100],
            'b': [6, 7, 8, 9, 10, 11],
        })
        
        config = OutlierConfig(method=OutlierMethod.LOCAL_OUTLIER_FACTOR, contamination=0.1)
        detector = OutlierDetector(config)
        
        report = detector.detect_outliers(df)
        
        assert report.method == "local_outlier_factor"
        assert report.total_outliers >= 0
        assert len(report.recommendations) > 0
    
    def test_detect_outliers_dbscan(self):
        """Test outlier detection using DBSCAN."""
        df = pd.DataFrame({
            'a': [1, 2, 3, 4, 5, 100],
            'b': [6, 7, 8, 9, 10, 11],
        })
        
        config = OutlierConfig(
            method=OutlierMethod.DBSCAN,
            dbscan_eps=0.5,
            dbscan_min_samples=3
        )
        detector = OutlierDetector(config)
        
        report = detector.detect_outliers(df)
        
        assert report.method == "dbscan"
        assert report.total_outliers >= 0
        assert len(report.recommendations) > 0
    
    def test_detect_outliers_percentile(self):
        """Test outlier detection using percentile bounds."""
        df = pd.DataFrame({
            'a': [1, 2, 3, 4, 5, 100],
            'b': [6, 7, 8, 9, 10, 11],
        })
        
        config = OutlierConfig(
            method=OutlierMethod.PERCENTILE,
            percentile_bounds=(10.0, 90.0)
        )
        detector = OutlierDetector(config)
        
        report = detector.detect_outliers(df)
        
        assert report.method == "percentile"
        assert report.total_outliers > 0
        assert len(report.recommendations) > 0
    
    def test_detect_outliers_statistical_distance(self):
        """Test outlier detection using statistical distance."""
        df = pd.DataFrame({
            'a': [1, 2, 3, 4, 5, 100],
            'b': [6, 7, 8, 9, 10, 11],
        })
        
        config = OutlierConfig(method=OutlierMethod.STATISTICAL_DISTANCE)
        detector = OutlierDetector(config)
        
        report = detector.detect_outliers(df)
        
        assert report.method == "statistical_distance"
        assert report.total_outliers >= 0
        assert len(report.recommendations) > 0
    
    def test_detect_outliers_empty_dataframe(self):
        """Test outlier detection with empty dataframe."""
        df = pd.DataFrame()
        
        detector = OutlierDetector()
        report = detector.detect_outliers(df)
        
        assert report.total_outliers == 0
        assert report.outlier_percentage == 0.0
        assert len(report.outlier_indices) == 0
        assert len(report.recommendations) > 0
    
    def test_handle_outliers_remove(self):
        """Test handling outliers by removing them."""
        df = pd.DataFrame({
            'a': [1, 2, 3, 4, 5, 100],
            'b': [6, 7, 8, 9, 10, 11],
        })
        
        config = OutlierConfig(action=OutlierAction.REMOVE)
        detector = OutlierDetector(config)
        
        outlier_indices = [5]
        result = detector.handle_outliers(df, outlier_indices)
        
        assert len(result) == len(df) - 1
        assert 100 not in result['a'].values
    
    def test_handle_outliers_cap(self):
        """Test handling outliers by capping them."""
        df = pd.DataFrame({
            'a': [1, 2, 3, 4, 5, 100],
            'b': [6, 7, 8, 9, 10, 11],
        })
        
        config = OutlierConfig(action=OutlierAction.CAP)
        detector = OutlierDetector(config)
        
        # First detect outliers to get the proper bounds
        outlier_report = detector.detect_outliers(df)
        
        # Then handle outliers using the detected indices
        result = detector.handle_outliers(df, outlier_report.outlier_indices)
        
        assert len(result) == len(df)
        # Check that the outlier was capped (should be less than original)
        if len(outlier_report.outlier_indices) > 0:
            outlier_idx = outlier_report.outlier_indices[0]
            assert result['a'].iloc[outlier_idx] <= df['a'].iloc[outlier_idx]
    
    def test_handle_outliers_transform(self):
        """Test handling outliers by transforming them."""
        df = pd.DataFrame({
            'a': [1, 2, 3, 4, 5, 100],
            'b': [6, 7, 8, 9, 10, 11],
        })
        
        config = OutlierConfig(action=OutlierAction.TRANSFORM)
        detector = OutlierDetector(config)
        
        outlier_indices = [5]
        result = detector.handle_outliers(df, outlier_indices)
        
        assert len(result) == len(df)
        # After log transformation, all values should be positive
        assert all(result['a'] > 0)
    
    def test_handle_outliers_flag(self):
        """Test handling outliers by flagging them."""
        df = pd.DataFrame({
            'a': [1, 2, 3, 4, 5, 100],
            'b': [6, 7, 8, 9, 10, 11],
        })
        
        config = OutlierConfig(action=OutlierAction.FLAG)
        detector = OutlierDetector(config)
        
        outlier_indices = [5]
        result = detector.handle_outliers(df, outlier_indices)
        
        assert len(result) == len(df)
        assert 'is_outlier' in result.columns
        assert result['is_outlier'].iloc[5] == True
        assert result['is_outlier'].iloc[0] == False
    
    def test_handle_outliers_leave_as_is(self):
        """Test handling outliers by leaving them as is."""
        df = pd.DataFrame({
            'a': [1, 2, 3, 4, 5, 100],
            'b': [6, 7, 8, 9, 10, 11],
        })
        
        config = OutlierConfig(action=OutlierAction.LEAVE_AS_IS)
        detector = OutlierDetector(config)
        
        outlier_indices = [5]
        result = detector.handle_outliers(df, outlier_indices)
        
        assert len(result) == len(df)
        assert result['a'].iloc[5] == 100  # Should remain unchanged


class TestDataCleaner:
    """Test cases for DataCleaner."""
    
    def test_data_cleaner_initialization(self):
        """Test DataCleaner initialization."""
        cleaner = DataCleaner()
        assert cleaner.config.handle_missing_first is True
        assert cleaner.config.preserve_original is True
        assert cleaner.missing_handler is not None
        assert cleaner.outlier_detector is not None
        assert cleaner.original_data is None
    
    def test_data_cleaner_custom_config(self):
        """Test DataCleaner with custom configuration."""
        missing_config = MissingDataConfig(method=MissingDataMethod.FILL_MEAN)
        outlier_config = OutlierConfig(method=OutlierMethod.Z_SCORE)
        config = CleaningConfig(
            missing_data=missing_config,
            outlier_detection=outlier_config,
            handle_missing_first=False,
            preserve_original=True
        )
        
        cleaner = DataCleaner(config)
        assert cleaner.config.handle_missing_first is False
        assert cleaner.config.missing_data.method == MissingDataMethod.FILL_MEAN
        assert cleaner.config.outlier_detection.method == OutlierMethod.Z_SCORE
    
    def test_clean_data_comprehensive(self):
        """Test comprehensive data cleaning."""
        df = pd.DataFrame({
            'a': [1, 2, np.nan, 4, 5, 100],  # Missing value and outlier
            'b': [6, 7, 8, 9, 10, 11],
            'c': ['x', 'y', None, 'w', 'v', 'u']  # Missing value
        })
        
        config = CleaningConfig(
            missing_data=MissingDataConfig(method=MissingDataMethod.FILL_MEDIAN),
            outlier_detection=OutlierConfig(
                method=OutlierMethod.IQR,
                action=OutlierAction.CAP
            ),
            handle_missing_first=True,
            preserve_original=True
        )
        
        cleaner = DataCleaner(config)
        cleaned_df, report = cleaner.clean_data(df)
        
        # Check that original data is preserved
        assert cleaner.original_data is not None
        pd.testing.assert_frame_equal(cleaner.original_data, df)
        
        # Check that cleaning was applied
        assert report.original_shape == df.shape
        assert report.final_shape == cleaned_df.shape
        assert len(report.actions_taken) > 0
        assert report.missing_data_report is not None
        assert report.outlier_report is not None
    
    def test_clean_data_missing_first(self):
        """Test cleaning with missing data handled first."""
        df = pd.DataFrame({
            'a': [1, 2, np.nan, 4, 5, 100],
            'b': [6, 7, 8, 9, 10, 11],
        })
        
        config = CleaningConfig(
            missing_data=MissingDataConfig(method=MissingDataMethod.FILL_MEAN),
            outlier_detection=OutlierConfig(method=OutlierMethod.IQR),
            handle_missing_first=True
        )
        
        cleaner = DataCleaner(config)
        cleaned_df, report = cleaner.clean_data(df)
        
        # Missing data should be handled first
        assert "missing data handling" in report.actions_taken[0]
        assert cleaned_df.isnull().sum().sum() == 0
    
    def test_clean_data_outliers_first(self):
        """Test cleaning with outliers handled first."""
        df = pd.DataFrame({
            'a': [1, 2, np.nan, 4, 5, 100],
            'b': [6, 7, 8, 9, 10, 11],
        })
        
        config = CleaningConfig(
            missing_data=MissingDataConfig(method=MissingDataMethod.FILL_MEAN),
            outlier_detection=OutlierConfig(method=OutlierMethod.IQR),
            handle_missing_first=False
        )
        
        cleaner = DataCleaner(config)
        cleaned_df, report = cleaner.clean_data(df)
        
        # Outliers should be handled first
        assert "outlier handling" in report.actions_taken[0]
    
    def test_clean_data_no_preserve_original(self):
        """Test cleaning without preserving original data."""
        df = pd.DataFrame({
            'a': [1, 2, np.nan, 4, 5],
            'b': [6, 7, 8, 9, 10],
        })
        
        config = CleaningConfig(preserve_original=False)
        cleaner = DataCleaner(config)
        cleaned_df, report = cleaner.clean_data(df)
        
        # Original data should not be preserved
        assert cleaner.original_data is None
    
    def test_get_original_data(self):
        """Test getting original data."""
        df = pd.DataFrame({
            'a': [1, 2, np.nan, 4, 5],
            'b': [6, 7, 8, 9, 10],
        })
        
        cleaner = DataCleaner()
        cleaned_df, report = cleaner.clean_data(df)
        
        original = cleaner.get_original_data()
        assert original is not None
        pd.testing.assert_frame_equal(original, df)


class TestUtilityFunctions:
    """Test cases for utility functions."""
    
    def test_analyze_missing_data_utility(self):
        """Test analyze_missing_data utility function."""
        df = pd.DataFrame({
            'a': [1, 2, np.nan, 4, 5],
            'b': [6, np.nan, 8, np.nan, 10],
        })
        
        report = analyze_missing_data(df)
        
        assert report.total_missing == 3
        assert report.missing_percentage > 0
        assert len(report.recommendations) > 0
    
    def test_detect_outliers_utility(self):
        """Test detect_outliers utility function."""
        df = pd.DataFrame({
            'a': [1, 2, 3, 4, 5, 100],
            'b': [6, 7, 8, 9, 10, 11],
        })
        
        report = detect_outliers(df, method="iqr")
        
        assert report.method == "iqr"
        assert report.total_outliers >= 0
    
    def test_detect_outliers_utility_with_kwargs(self):
        """Test detect_outliers utility function with kwargs."""
        df = pd.DataFrame({
            'a': [1, 2, 3, 4, 5, 100],
            'b': [6, 7, 8, 9, 10, 11],
        })
        
        report = detect_outliers(df, method="z_score", z_threshold=2.0)
        
        assert report.method == "z_score"
        assert report.threshold_values['z_threshold'] == 2.0
    
    def test_clean_dataset_utility(self):
        """Test clean_dataset utility function."""
        df = pd.DataFrame({
            'a': [1, 2, np.nan, 4, 5, 100],
            'b': [6, 7, 8, 9, 10, 11],
        })
        
        cleaned_df, report = clean_dataset(
            df,
            missing_method="fill_mean",
            outlier_method="iqr",
            outlier_action="cap"
        )
        
        assert report.original_shape == df.shape
        assert cleaned_df.isnull().sum().sum() == 0
        assert len(report.actions_taken) > 0
    
    def test_clean_dataset_utility_with_kwargs(self):
        """Test clean_dataset utility function with kwargs."""
        df = pd.DataFrame({
            'a': [1, 2, np.nan, 4, 5, 100],
            'b': [6, 7, 8, 9, 10, 11],
        })
        
        cleaned_df, report = clean_dataset(
            df,
            missing_method="fill_knn",
            outlier_method="z_score",
            outlier_action="remove",
            knn_neighbors=3,
            z_threshold=2.0,
            handle_missing_first=False
        )
        
        assert report.original_shape == df.shape
        assert cleaned_df.isnull().sum().sum() == 0
        assert len(report.actions_taken) > 0


class TestErrorHandling:
    """Test cases for error handling."""
    
    def test_statistical_distance_singular_matrix(self):
        """Test statistical distance with singular covariance matrix."""
        # Create data that will result in singular covariance matrix
        df = pd.DataFrame({
            'a': [1, 1, 1, 1, 1],  # No variance
            'b': [2, 2, 2, 2, 2],  # No variance
        })
        
        config = OutlierConfig(method=OutlierMethod.STATISTICAL_DISTANCE)
        detector = OutlierDetector(config)
        
        # Should fallback to Z-score method
        report = detector.detect_outliers(df)
        
        assert report.total_outliers >= 0
    
    def test_empty_dataframe_handling(self):
        """Test handling of empty dataframes."""
        df = pd.DataFrame()
        
        # Missing data analysis
        handler = MissingDataHandler()
        report = handler.analyze_missing_data(df)
        assert report.total_missing == 0
        
        # Outlier detection
        detector = OutlierDetector()
        outlier_report = detector.detect_outliers(df)
        assert outlier_report.total_outliers == 0
        
        # Data cleaning
        cleaner = DataCleaner()
        cleaned_df, cleaning_report = cleaner.clean_data(df)
        assert len(cleaned_df) == 0
    
    def test_single_column_dataframe(self):
        """Test handling of single column dataframes."""
        df = pd.DataFrame({'a': [1, 2, np.nan, 4, 5, 100]})
        
        cleaner = DataCleaner()
        cleaned_df, report = cleaner.clean_data(df)
        
        assert len(cleaned_df.columns) == 1
        assert report.original_shape[1] == 1
    
    def test_all_missing_data(self):
        """Test handling of dataframes with all missing data."""
        df = pd.DataFrame({
            'a': [np.nan, np.nan, np.nan],
            'b': [None, None, None],
        })
        
        cleaner = DataCleaner()
        cleaned_df, report = cleaner.clean_data(df)
        
        assert len(cleaned_df) <= len(df)
        assert report.missing_data_report.total_missing == 6 