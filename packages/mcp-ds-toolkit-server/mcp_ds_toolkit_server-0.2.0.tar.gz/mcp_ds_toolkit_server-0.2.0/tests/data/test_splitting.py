"""
Tests for the data splitting module.
"""

from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

import numpy as np
import pandas as pd
import pytest

from mcp_ds_toolkit_server.data.splitting import (
    CrossValidationConfig,
    CrossValidationMethod,
    DataSplitter,
    SplitMetrics,
    SplittingConfig,
    SplittingMethod,
    SplittingReport,
    create_stratified_splits,
    create_time_series_splits,
    split_dataset,
)


class TestSplittingConfig:
    """Test cases for SplittingConfig."""
    
    def test_splitting_config_initialization(self):
        """Test SplittingConfig initialization."""
        config = SplittingConfig()
        assert config.method == SplittingMethod.RANDOM
        assert config.train_size == 0.7
        assert config.validation_size == 0.15
        assert config.test_size == 0.15
        assert config.random_state == 42
        assert config.shuffle is True
        
    def test_splitting_config_validation(self):
        """Test SplittingConfig validation."""
        # Test valid configuration
        config = SplittingConfig(train_size=0.6, validation_size=0.2, test_size=0.2)
        assert config.train_size == 0.6
        
        # Test invalid sum
        with pytest.raises(ValueError):
            SplittingConfig(train_size=0.5, validation_size=0.3, test_size=0.3)
        
        # Test negative sizes
        with pytest.raises(ValueError):
            SplittingConfig(train_size=-0.1, validation_size=0.6, test_size=0.5)
    
    def test_splitting_config_custom_settings(self):
        """Test SplittingConfig with custom settings."""
        config = SplittingConfig(
            method=SplittingMethod.STRATIFIED,
            train_size=0.8,
            validation_size=0.1,
            test_size=0.1,
            stratify_column='target',
            shuffle=False
        )
        assert config.method == SplittingMethod.STRATIFIED
        assert config.stratify_column == 'target'
        assert config.shuffle is False


class TestCrossValidationConfig:
    """Test cases for CrossValidationConfig."""
    
    def test_cv_config_initialization(self):
        """Test CrossValidationConfig initialization."""
        config = CrossValidationConfig()
        assert config.method == CrossValidationMethod.K_FOLD
        assert config.n_splits == 5
        assert config.random_state == 42
        
    def test_cv_config_validation(self):
        """Test CrossValidationConfig validation."""
        # Test valid configuration
        config = CrossValidationConfig(n_splits=10, test_size=0.3)
        assert config.n_splits == 10
        
        # Test invalid n_splits
        with pytest.raises(ValueError):
            CrossValidationConfig(n_splits=1)
        
        # Test invalid test_size
        with pytest.raises(ValueError):
            CrossValidationConfig(test_size=-0.1)
        
        with pytest.raises(ValueError):
            CrossValidationConfig(test_size=1.1)


class TestDataSplitter:
    """Test cases for DataSplitter."""
    
    def test_data_splitter_initialization(self):
        """Test DataSplitter initialization."""
        splitter = DataSplitter()
        assert splitter.config.method == SplittingMethod.RANDOM
        assert splitter.label_encoders == {}
        assert splitter.split_indices == {}
        assert splitter._split_data == {}
        
    def test_data_splitter_with_config(self):
        """Test DataSplitter with custom configuration."""
        config = SplittingConfig(method=SplittingMethod.STRATIFIED)
        splitter = DataSplitter(config)
        assert splitter.config.method == SplittingMethod.STRATIFIED
    
    def test_split_data_random(self):
        """Test random data splitting."""
        # Create test data
        df = pd.DataFrame({
            'feature1': np.random.randn(100),
            'feature2': np.random.randn(100),
            'target': np.random.randint(0, 2, 100)
        })
        
        config = SplittingConfig(method=SplittingMethod.RANDOM)
        splitter = DataSplitter(config)
        
        train_df, val_df, test_df, report = splitter.split_data(df)
        
        # Check split sizes
        assert len(train_df) == 70
        assert len(val_df) == 15
        assert len(test_df) == 15
        assert len(train_df) + len(val_df) + len(test_df) == len(df)
        
        # Check report
        assert report.method == "random"
        assert report.total_samples == 100
        assert report.train_metrics.size == 70
        assert report.validation_metrics.size == 15
        assert report.test_metrics.size == 15
    
    def test_split_data_stratified(self):
        """Test stratified data splitting."""
        # Create test data with class imbalance
        df = pd.DataFrame({
            'feature1': np.random.randn(100),
            'feature2': np.random.randn(100),
            'target': np.random.choice([0, 1], 100, p=[0.7, 0.3])
        })
        
        config = SplittingConfig(method=SplittingMethod.STRATIFIED)
        splitter = DataSplitter(config)
        
        train_df, val_df, test_df, report = splitter.split_data(df, target_column='target')
        
        # Check split sizes
        assert len(train_df) + len(val_df) + len(test_df) == len(df)
        
        # Check stratification
        original_ratio = df['target'].mean()
        train_ratio = train_df['target'].mean()
        val_ratio = val_df['target'].mean()
        test_ratio = test_df['target'].mean()
        
        # Ratios should be approximately equal
        assert abs(original_ratio - train_ratio) < 0.1
        assert abs(original_ratio - val_ratio) < 0.2  # Smaller sets have more variance
        assert abs(original_ratio - test_ratio) < 0.2
        
        # Check report
        assert report.method == "stratified"
        assert report.stratification_quality is not None
        assert report.stratification_quality > 0.5
    
    def test_split_data_time_series(self):
        """Test time series data splitting."""
        # Create time series data
        dates = pd.date_range('2023-01-01', periods=100, freq='D')
        df = pd.DataFrame({
            'date': dates,
            'value': np.random.randn(100),
            'feature': np.random.randn(100)
        })
        
        config = SplittingConfig(method=SplittingMethod.TIME_SERIES, time_column='date')
        splitter = DataSplitter(config)
        
        train_df, val_df, test_df, report = splitter.split_data(df)
        
        # Check chronological order
        assert train_df['date'].max() <= val_df['date'].min()
        assert val_df['date'].max() <= test_df['date'].min()
        
        # Check report
        assert report.method == "time_series"
        assert report.time_overlap is False
        assert report.train_metrics.time_range is not None
        assert report.validation_metrics.time_range is not None
        assert report.test_metrics.time_range is not None
    
    def test_split_data_group_based(self):
        """Test group-based data splitting."""
        # Create grouped data
        df = pd.DataFrame({
            'group': np.repeat(range(10), 10),
            'feature': np.random.randn(100),
            'target': np.random.randint(0, 2, 100)
        })
        
        config = SplittingConfig(method=SplittingMethod.GROUP_BASED, group_column='group')
        splitter = DataSplitter(config)
        
        train_df, val_df, test_df, report = splitter.split_data(df)
        
        # Check no group overlap
        train_groups = set(train_df['group'].unique())
        val_groups = set(val_df['group'].unique())
        test_groups = set(test_df['group'].unique())
        
        assert len(train_groups & val_groups) == 0
        assert len(val_groups & test_groups) == 0
        assert len(train_groups & test_groups) == 0
        
        # Check report
        assert report.method == "group_based"
        assert report.group_overlap is False
    
    def test_split_data_manual(self):
        """Test manual data splitting."""
        # Create test data
        df = pd.DataFrame({
            'feature1': np.random.randn(100),
            'feature2': np.random.randn(100),
            'target': np.random.randint(0, 2, 100)
        })
        
        # Define manual indices
        custom_indices = {
            'train': list(range(70)),
            'validation': list(range(70, 85)),
            'test': list(range(85, 100))
        }
        
        config = SplittingConfig(method=SplittingMethod.MANUAL, custom_indices=custom_indices)
        splitter = DataSplitter(config)
        
        train_df, val_df, test_df, report = splitter.split_data(df)
        
        # Check exact indices
        assert train_df.index.tolist() == custom_indices['train']
        assert val_df.index.tolist() == custom_indices['validation']
        assert test_df.index.tolist() == custom_indices['test']
        
        # Check report
        assert report.method == "manual"
    
    def test_split_data_empty_dataframe(self):
        """Test splitting empty DataFrame."""
        df = pd.DataFrame()
        splitter = DataSplitter()
        
        with pytest.raises(ValueError):
            splitter.split_data(df)
    
    def test_split_data_validation_errors(self):
        """Test validation errors in split_data."""
        df = pd.DataFrame({
            'feature1': np.random.randn(100),
            'target': np.random.randint(0, 2, 100)
        })
        
        # Test stratified without target
        config = SplittingConfig(method=SplittingMethod.STRATIFIED)
        splitter = DataSplitter(config)
        
        with pytest.raises(ValueError):
            splitter.split_data(df)
        
        # Test time series without time column
        config = SplittingConfig(method=SplittingMethod.TIME_SERIES)
        splitter = DataSplitter(config)
        
        with pytest.raises(ValueError):
            splitter.split_data(df)
    
    def test_create_cross_validation_splits(self):
        """Test cross-validation splits creation."""
        # Create test data
        df = pd.DataFrame({
            'feature1': np.random.randn(100),
            'feature2': np.random.randn(100),
            'target': np.random.randint(0, 2, 100)
        })
        
        splitter = DataSplitter()
        cv_config = CrossValidationConfig(method=CrossValidationMethod.K_FOLD, n_splits=5)
        
        splits = list(splitter.create_cross_validation_splits(df, cv_config))
        
        # Check number of splits
        assert len(splits) == 5
        
        # Check each split
        for train_df, val_df in splits:
            assert len(train_df) > 0
            assert len(val_df) > 0
            assert len(train_df) + len(val_df) == len(df)
    
    def test_create_stratified_cv_splits(self):
        """Test stratified cross-validation splits."""
        # Create test data
        df = pd.DataFrame({
            'feature1': np.random.randn(100),
            'feature2': np.random.randn(100),
            'target': np.random.choice([0, 1], 100, p=[0.7, 0.3])
        })
        
        splitter = DataSplitter()
        cv_config = CrossValidationConfig(method=CrossValidationMethod.STRATIFIED_K_FOLD, n_splits=5)
        
        splits = list(splitter.create_cross_validation_splits(df, cv_config, target_column='target'))
        
        # Check number of splits
        assert len(splits) == 5
        
        # Check stratification in each split
        original_ratio = df['target'].mean()
        for train_df, val_df in splits:
            train_ratio = train_df['target'].mean()
            val_ratio = val_df['target'].mean()
            
            # Ratios should be approximately equal to original
            assert abs(original_ratio - train_ratio) < 0.15
            assert abs(original_ratio - val_ratio) < 0.25
    
    def test_get_split_indices(self):
        """Test getting split indices."""
        df = pd.DataFrame({
            'feature1': np.random.randn(100),
            'target': np.random.randint(0, 2, 100)
        })
        
        splitter = DataSplitter()
        train_df, val_df, test_df, report = splitter.split_data(df)
        
        indices = splitter.get_split_indices()
        
        assert 'train' in indices
        assert 'validation' in indices
        assert 'test' in indices
        assert len(indices['train']) == len(train_df)
        assert len(indices['validation']) == len(val_df)
        assert len(indices['test']) == len(test_df)
    
    def test_get_split_data(self):
        """Test getting split data."""
        df = pd.DataFrame({
            'feature1': np.random.randn(100),
            'target': np.random.randint(0, 2, 100)
        })
        
        splitter = DataSplitter()
        train_df, val_df, test_df, report = splitter.split_data(df)
        
        split_data = splitter.get_split_data()
        
        assert 'train' in split_data
        assert 'validation' in split_data
        assert 'test' in split_data
        pd.testing.assert_frame_equal(split_data['train'], train_df)
        pd.testing.assert_frame_equal(split_data['validation'], val_df)
        pd.testing.assert_frame_equal(split_data['test'], test_df)


class TestSplittingReport:
    """Test cases for SplittingReport."""
    
    def test_splitting_report_creation(self):
        """Test SplittingReport creation."""
        # Create test data
        df = pd.DataFrame({
            'feature1': np.random.randn(100),
            'target': np.random.randint(0, 2, 100)
        })
        
        splitter = DataSplitter()
        train_df, val_df, test_df, report = splitter.split_data(df)
        
        # Check report structure
        assert isinstance(report, SplittingReport)
        assert report.method == "random"
        assert report.total_samples == 100
        assert isinstance(report.train_metrics, SplitMetrics)
        assert isinstance(report.validation_metrics, SplitMetrics)
        assert isinstance(report.test_metrics, SplitMetrics)
        assert isinstance(report.recommendations, list)
    
    def test_split_metrics_calculation(self):
        """Test SplitMetrics calculation."""
        # Create test data
        df = pd.DataFrame({
            'feature1': np.random.randn(100),
            'target': np.random.randint(0, 2, 100)
        })
        
        config = SplittingConfig(method=SplittingMethod.STRATIFIED)
        splitter = DataSplitter(config)
        train_df, val_df, test_df, report = splitter.split_data(df, target_column='target')
        
        # Check metrics
        assert report.train_metrics.size == len(train_df)
        assert report.train_metrics.percentage == (len(train_df) / len(df)) * 100
        assert report.train_metrics.class_distribution is not None
        
        assert report.validation_metrics.size == len(val_df)
        assert report.validation_metrics.percentage == (len(val_df) / len(df)) * 100
        assert report.validation_metrics.class_distribution is not None


class TestUtilityFunctions:
    """Test cases for utility functions."""
    
    def test_split_dataset_utility(self):
        """Test split_dataset utility function."""
        df = pd.DataFrame({
            'feature1': np.random.randn(100),
            'feature2': np.random.randn(100),
            'target': np.random.randint(0, 2, 100)
        })
        
        train_df, val_df, test_df, report = split_dataset(df, method='random')
        
        assert len(train_df) == 70
        assert len(val_df) == 15
        assert len(test_df) == 15
        assert report.method == "random"
    
    def test_split_dataset_utility_with_custom_sizes(self):
        """Test split_dataset utility with custom sizes."""
        df = pd.DataFrame({
            'feature1': np.random.randn(100),
            'target': np.random.randint(0, 2, 100)
        })
        
        train_df, val_df, test_df, report = split_dataset(
            df, 
            method='random',
            train_size=0.6,
            validation_size=0.2,
            test_size=0.2
        )
        
        assert len(train_df) == 60
        assert len(val_df) == 20
        assert len(test_df) == 20
    
    def test_split_dataset_utility_stratified(self):
        """Test split_dataset utility with stratified method."""
        df = pd.DataFrame({
            'feature1': np.random.randn(100),
            'target': np.random.choice([0, 1], 100, p=[0.7, 0.3])
        })
        
        train_df, val_df, test_df, report = split_dataset(
            df, 
            method='stratified',
            target_column='target'
        )
        
        assert report.method == "stratified"
        assert report.stratification_quality is not None
    
    def test_create_time_series_splits_utility(self):
        """Test create_time_series_splits utility function."""
        # Create time series data
        dates = pd.date_range('2023-01-01', periods=100, freq='D')
        df = pd.DataFrame({
            'date': dates,
            'value': np.random.randn(100)
        })
        
        splits = list(create_time_series_splits(df, time_column='date', n_splits=5))
        
        assert len(splits) == 5
        
        # Check chronological order
        for train_df, val_df in splits:
            assert len(train_df) > 0
            assert len(val_df) > 0
            assert train_df['date'].max() <= val_df['date'].min()
    
    def test_create_stratified_splits_utility(self):
        """Test create_stratified_splits utility function."""
        df = pd.DataFrame({
            'feature1': np.random.randn(100),
            'target': np.random.choice([0, 1], 100, p=[0.7, 0.3])
        })
        
        splits = list(create_stratified_splits(df, target_column='target', n_splits=5))
        
        assert len(splits) == 5
        
        # Check stratification
        original_ratio = df['target'].mean()
        for train_df, val_df in splits:
            train_ratio = train_df['target'].mean()
            val_ratio = val_df['target'].mean()
            
            # Ratios should be approximately equal to original
            assert abs(original_ratio - train_ratio) < 0.15
            assert abs(original_ratio - val_ratio) < 0.25


class TestEdgeCases:
    """Test edge cases and error conditions."""
    
    def test_small_dataset_splitting(self):
        """Test splitting very small datasets."""
        # Create very small dataset
        df = pd.DataFrame({
            'feature1': [1, 2, 3, 4, 5],
            'target': [0, 1, 0, 1, 0]
        })
        
        splitter = DataSplitter()
        train_df, val_df, test_df, report = splitter.split_data(df)
        
        # Should still work but generate warnings in recommendations
        assert len(train_df) + len(val_df) + len(test_df) == len(df)
        assert len(report.recommendations) > 0
    
    def test_single_class_stratified_splitting(self):
        """Test stratified splitting with single class."""
        df = pd.DataFrame({
            'feature1': np.random.randn(100),
            'target': np.ones(100)  # All same class
        })
        
        config = SplittingConfig(method=SplittingMethod.STRATIFIED)
        splitter = DataSplitter(config)
        
        train_df, val_df, test_df, report = splitter.split_data(df, target_column='target')
        
        # Should work with single class
        assert len(train_df) + len(val_df) + len(test_df) == len(df)
        assert report.stratification_quality is not None
    
    def test_missing_values_in_data(self):
        """Test splitting data with missing values."""
        df = pd.DataFrame({
            'feature1': np.random.randn(100),
            'feature2': np.random.randn(100),
            'target': np.random.randint(0, 2, 100)
        })
        
        # Add some missing values
        df.loc[10:20, 'feature1'] = np.nan
        df.loc[30:35, 'feature2'] = np.nan
        
        splitter = DataSplitter()
        train_df, val_df, test_df, report = splitter.split_data(df)
        
        # Should handle missing values gracefully
        assert len(train_df) + len(val_df) + len(test_df) == len(df)
        assert report.train_metrics.missing_values >= 0
        assert report.validation_metrics.missing_values >= 0
        assert report.test_metrics.missing_values >= 0
    
    def test_categorical_target_encoding(self):
        """Test encoding of categorical target variables."""
        df = pd.DataFrame({
            'feature1': np.random.randn(100),
            'target': np.random.choice(['A', 'B', 'C'], 100)
        })
        
        config = SplittingConfig(method=SplittingMethod.STRATIFIED)
        splitter = DataSplitter(config)
        
        train_df, val_df, test_df, report = splitter.split_data(df, target_column='target')
        
        # Should encode categorical target properly
        assert len(train_df) + len(val_df) + len(test_df) == len(df)
        assert report.stratification_quality is not None
        assert 'target' in splitter.label_encoders
    
    def test_time_series_unsorted_data(self):
        """Test time series splitting with unsorted data."""
        # Create unsorted time series data
        dates = pd.date_range('2023-01-01', periods=100, freq='D')
        df = pd.DataFrame({
            'date': dates,
            'value': np.random.randn(100)
        })
        
        # Shuffle the data
        df = df.sample(frac=1).reset_index(drop=True)
        
        config = SplittingConfig(method=SplittingMethod.TIME_SERIES, time_column='date', sort_by_time=True)
        splitter = DataSplitter(config)
        
        train_df, val_df, test_df, report = splitter.split_data(df)
        
        # Should sort and split correctly
        assert train_df['date'].max() <= val_df['date'].min()
        assert val_df['date'].max() <= test_df['date'].min()
        assert report.time_overlap is False 