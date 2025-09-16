"""
Tests for the preprocessing module.
"""

import os
import tempfile
from unittest.mock import Mock, patch

import numpy as np
import pandas as pd
import pytest
from sklearn.datasets import make_classification, make_regression
from sklearn.model_selection import train_test_split

from mcp_ds_toolkit_server.data.preprocessing import (
    CustomTransformer,
    EncodingMethod,
    ImputationMethod,
    PreprocessingConfig,
    PreprocessingPipeline,
    PreprocessingReport,
    ScalingMethod,
    SelectionMethod,
    create_preprocessing_pipeline,
    preprocess_for_ml,
    quick_preprocess,
)


class TestPreprocessingConfig:
    """Test preprocessing configuration."""
    
    def test_default_config(self):
        """Test default configuration values."""
        config = PreprocessingConfig()
        assert config.numeric_scaling == ScalingMethod.NONE
        assert config.categorical_encoding == EncodingMethod.NONE
        assert config.numeric_imputation == ImputationMethod.MEDIAN
        assert config.categorical_imputation == ImputationMethod.MODE
        assert config.feature_selection == SelectionMethod.NONE
        assert config.random_state == 42
    
    def test_custom_config(self):
        """Test custom configuration values."""
        config = PreprocessingConfig(
            numeric_scaling=ScalingMethod.MINMAX,
            categorical_encoding=EncodingMethod.ORDINAL,
            feature_selection=SelectionMethod.UNIVARIATE_KBEST,
            selection_k=20
        )
        assert config.numeric_scaling == ScalingMethod.MINMAX
        assert config.categorical_encoding == EncodingMethod.ORDINAL
        assert config.feature_selection == SelectionMethod.UNIVARIATE_KBEST
        assert config.selection_k == 20


class TestCustomTransformer:
    """Test custom transformer functionality."""
    
    def test_custom_transformer_basic(self):
        """Test basic custom transformer functionality."""
        def double_values(X):
            return X * 2
        
        transformer = CustomTransformer(transform_func=double_values)
        X = np.array([[1, 2], [3, 4]])
        
        transformer.fit(X)
        X_transformed = transformer.transform(X)
        
        expected = np.array([[2, 4], [6, 8]])
        np.testing.assert_array_equal(X_transformed, expected)
    
    def test_custom_transformer_no_function(self):
        """Test custom transformer with no function."""
        transformer = CustomTransformer()
        X = np.array([[1, 2], [3, 4]])
        
        transformer.fit(X)
        X_transformed = transformer.transform(X)
        
        np.testing.assert_array_equal(X_transformed, X)
    
    def test_custom_transformer_feature_names(self):
        """Test custom transformer with feature names."""
        feature_names = ['feature_1', 'feature_2']
        transformer = CustomTransformer(feature_names=feature_names)
        
        names = transformer.get_feature_names_out()
        assert names == feature_names


class TestPreprocessingPipeline:
    """Test preprocessing pipeline functionality."""
    
    @pytest.fixture
    def sample_data(self):
        """Create sample data for testing."""
        np.random.seed(42)
        n_samples = 100
        
        # Create mixed data
        numeric_data = np.random.randn(n_samples, 3)
        categorical_data = np.random.choice(['A', 'B', 'C'], size=(n_samples, 2))
        
        # Add some missing values
        numeric_data[5:10, 0] = np.nan
        categorical_data[10:15, 1] = None
        
        df = pd.DataFrame({
            'num1': numeric_data[:, 0],
            'num2': numeric_data[:, 1],
            'num3': numeric_data[:, 2],
            'cat1': categorical_data[:, 0],
            'cat2': categorical_data[:, 1]
        })
        
        # Create target variable
        target = np.random.choice([0, 1], size=n_samples)
        y = pd.Series(target, name='target')
        
        return df, y
    
    def test_pipeline_initialization(self):
        """Test pipeline initialization."""
        pipeline = PreprocessingPipeline()
        assert pipeline.config is not None
        assert not pipeline.is_fitted
        assert pipeline.pipeline is None
    
    def test_pipeline_fit_transform(self, sample_data):
        """Test pipeline fit and transform."""
        X, y = sample_data
        
        config = PreprocessingConfig(
            numeric_scaling=ScalingMethod.STANDARD,
            categorical_encoding=EncodingMethod.ONEHOT,
            numeric_imputation=ImputationMethod.MEDIAN,
            categorical_imputation=ImputationMethod.MODE
        )
        
        pipeline = PreprocessingPipeline(config)
        X_transformed = pipeline.fit_transform(X, y)
        
        assert pipeline.is_fitted
        assert isinstance(X_transformed, pd.DataFrame)
        assert X_transformed.shape[0] == X.shape[0]
        assert X_transformed.shape[1] >= X.shape[1]  # May increase due to encoding
        
        # Check no missing values after imputation
        assert X_transformed.isnull().sum().sum() == 0
    
    def test_pipeline_different_scalers(self, sample_data):
        """Test pipeline with different scaling methods."""
        X, y = sample_data
        
        scaling_methods = [
            ScalingMethod.STANDARD,
            ScalingMethod.MINMAX,
            ScalingMethod.ROBUST,
            ScalingMethod.MAXABS
        ]
        
        for method in scaling_methods:
            config = PreprocessingConfig(numeric_scaling=method)
            pipeline = PreprocessingPipeline(config)
            X_transformed = pipeline.fit_transform(X, y)
            
            assert pipeline.is_fitted
            assert isinstance(X_transformed, pd.DataFrame)
            assert X_transformed.shape[0] == X.shape[0]
    
    def test_pipeline_different_encoders(self, sample_data):
        """Test pipeline with different encoding methods."""
        X, y = sample_data
        
        encoding_methods = [
            EncodingMethod.ONEHOT,
            EncodingMethod.ORDINAL,
            EncodingMethod.LABEL
        ]
        
        for method in encoding_methods:
            config = PreprocessingConfig(categorical_encoding=method)
            pipeline = PreprocessingPipeline(config)
            X_transformed = pipeline.fit_transform(X, y)
            
            assert pipeline.is_fitted
            assert isinstance(X_transformed, pd.DataFrame)
            assert X_transformed.shape[0] == X.shape[0]
    
    def test_pipeline_feature_selection(self, sample_data):
        """Test pipeline with feature selection."""
        X, y = sample_data
        
        # Test with conservative defaults (no encoding) - should skip feature selection
        config = PreprocessingConfig(
            feature_selection=SelectionMethod.UNIVARIATE_KBEST,
            selection_k=3
        )
        
        pipeline = PreprocessingPipeline(config)
        X_transformed = pipeline.fit_transform(X, y)
        
        assert pipeline.is_fitted
        assert isinstance(X_transformed, pd.DataFrame)
        assert X_transformed.shape[0] == X.shape[0]
        # With conservative defaults, feature selection should be skipped, so shape should be same
        assert X_transformed.shape[1] == X.shape[1]
        
        # Test with proper encoding - feature selection should work
        config_with_encoding = PreprocessingConfig(
            categorical_encoding=EncodingMethod.ORDINAL,
            feature_selection=SelectionMethod.UNIVARIATE_KBEST,
            selection_k=3
        )
        
        pipeline_with_encoding = PreprocessingPipeline(config_with_encoding)
        X_transformed_encoded = pipeline_with_encoding.fit_transform(X, y)
        
        assert pipeline_with_encoding.is_fitted
        assert isinstance(X_transformed_encoded, pd.DataFrame)
        assert X_transformed_encoded.shape[0] == X.shape[0]
        # With encoding, feature selection should work
        assert X_transformed_encoded.shape[1] == 3  # selection_k=3
    
    def test_pipeline_polynomial_features(self, sample_data):
        """Test pipeline with polynomial features."""
        X, y = sample_data
        
        # Use encoding with polynomial features for proper mixed data handling
        config = PreprocessingConfig(
            categorical_encoding=EncodingMethod.ORDINAL,  # Encode categorical data
            create_polynomial_features=True,
            polynomial_degree=2
        )
        
        pipeline = PreprocessingPipeline(config)
        X_transformed = pipeline.fit_transform(X, y)
        
        assert pipeline.is_fitted
        assert isinstance(X_transformed, pd.DataFrame)
        assert X_transformed.shape[0] == X.shape[0]
        # Polynomial features should increase feature count significantly
        assert X_transformed.shape[1] > X.shape[1]
    
    def test_pipeline_separate_fit_transform(self, sample_data):
        """Test separate fit and transform calls."""
        X, y = sample_data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        pipeline = PreprocessingPipeline()
        pipeline.fit(X_train, y_train)
        
        X_train_transformed = pipeline.transform(X_train)
        X_test_transformed = pipeline.transform(X_test)
        
        assert pipeline.is_fitted
        assert isinstance(X_train_transformed, pd.DataFrame)
        assert isinstance(X_test_transformed, pd.DataFrame)
        assert X_train_transformed.shape[1] == X_test_transformed.shape[1]
    
    def test_pipeline_transform_without_fit(self, sample_data):
        """Test transform without fit raises error."""
        X, y = sample_data
        
        pipeline = PreprocessingPipeline()
        
        with pytest.raises(ValueError, match="Pipeline must be fitted"):
            pipeline.transform(X)
    
    def test_pipeline_save_load(self, sample_data):
        """Test pipeline save and load functionality."""
        X, y = sample_data
        
        pipeline = PreprocessingPipeline()
        pipeline.fit(X, y)
        
        with tempfile.NamedTemporaryFile(suffix='.pkl', delete=False) as tmp:
            pipeline.save_pipeline(tmp.name)
            
            # Load pipeline
            loaded_pipeline = PreprocessingPipeline.load_pipeline(tmp.name)
            
            assert loaded_pipeline.is_fitted
            assert loaded_pipeline.config.numeric_scaling == pipeline.config.numeric_scaling
            assert loaded_pipeline.numeric_columns == pipeline.numeric_columns
            assert loaded_pipeline.categorical_columns == pipeline.categorical_columns
            
            # Test that both pipelines produce same results
            X_orig = pipeline.transform(X)
            X_loaded = loaded_pipeline.transform(X)
            
            pd.testing.assert_frame_equal(X_orig, X_loaded)
            
            # Clean up
            os.unlink(tmp.name)
    
    def test_pipeline_save_without_fit(self, sample_data):
        """Test save without fit raises error."""
        pipeline = PreprocessingPipeline()
        
        with pytest.raises(ValueError, match="Pipeline must be fitted"):
            pipeline.save_pipeline("test.pkl")
    
    def test_pipeline_generate_report(self, sample_data):
        """Test preprocessing report generation."""
        X, y = sample_data
        
        pipeline = PreprocessingPipeline()
        X_transformed = pipeline.fit_transform(X, y)
        
        report = pipeline.generate_report(X, X_transformed)
        
        assert isinstance(report, PreprocessingReport)
        assert report.original_shape == X.shape
        assert report.final_shape == X_transformed.shape
        assert report.original_columns == X.columns.tolist()
        assert report.final_columns == X_transformed.columns.tolist()
        assert len(report.numeric_columns) == 3
        assert len(report.categorical_columns) == 2
        assert report.config == pipeline.config
        
        # Check calculated metrics
        assert hasattr(report, 'dimensionality_change')
        assert hasattr(report, 'feature_reduction_ratio')


class TestUtilityFunctions:
    """Test utility functions."""
    
    @pytest.fixture
    def sample_data(self):
        """Create sample data for testing."""
        X, y = make_classification(
            n_samples=100, n_features=10, n_redundant=2,
            n_informative=8, n_clusters_per_class=1, random_state=42
        )
        
        # Add some categorical features
        categorical_data = np.random.choice(['A', 'B', 'C'], size=(100, 2))
        
        # Create DataFrame
        feature_names = [f'num_feature_{i}' for i in range(10)]
        categorical_names = ['cat_feature_1', 'cat_feature_2']
        
        df = pd.DataFrame(X, columns=feature_names)
        df['cat_feature_1'] = categorical_data[:, 0]
        df['cat_feature_2'] = categorical_data[:, 1]
        
        return df, pd.Series(y, name='target')
    
    def test_create_preprocessing_pipeline(self):
        """Test create_preprocessing_pipeline function."""
        # Test with enum values
        pipeline = create_preprocessing_pipeline(
            scaling_method=ScalingMethod.MINMAX,
            encoding_method=EncodingMethod.ORDINAL,
            imputation_method=ImputationMethod.MEAN
        )
        
        assert isinstance(pipeline, PreprocessingPipeline)
        assert pipeline.config.numeric_scaling == ScalingMethod.MINMAX
        assert pipeline.config.categorical_encoding == EncodingMethod.ORDINAL
        assert pipeline.config.numeric_imputation == ImputationMethod.MEAN
        
        # Test with string values
        pipeline = create_preprocessing_pipeline(
            scaling_method="robust",
            encoding_method="onehot",
            imputation_method="mode"
        )
        
        assert isinstance(pipeline, PreprocessingPipeline)
        assert pipeline.config.numeric_scaling == ScalingMethod.ROBUST
        assert pipeline.config.categorical_encoding == EncodingMethod.ONEHOT
        assert pipeline.config.numeric_imputation == ImputationMethod.MODE
    
    def test_quick_preprocess(self, sample_data):
        """Test quick_preprocess function."""
        X, y = sample_data
        
        X_train, X_test, y_train, y_test = quick_preprocess(
            X, y, test_size=0.2, random_state=42
        )
        
        assert isinstance(X_train, pd.DataFrame)
        assert isinstance(X_test, pd.DataFrame)
        assert isinstance(y_train, pd.Series)
        assert isinstance(y_test, pd.Series)
        
        assert X_train.shape[0] == int(0.8 * len(X))
        assert X_test.shape[0] == int(0.2 * len(X))
        assert len(y_train) == X_train.shape[0]
        assert len(y_test) == X_test.shape[0]
        
        # Check that columns are consistent
        assert X_train.shape[1] == X_test.shape[1]
        assert list(X_train.columns) == list(X_test.columns)
    
    def test_quick_preprocess_without_target(self, sample_data):
        """Test quick_preprocess without target variable."""
        X, _ = sample_data
        
        X_train, X_test, y_train, y_test = quick_preprocess(
            X, test_size=0.2, random_state=42
        )
        
        assert isinstance(X_train, pd.DataFrame)
        assert isinstance(X_test, pd.DataFrame)
        assert y_train is None
        assert y_test is None
        
        assert X_train.shape[0] == int(0.8 * len(X))
        assert X_test.shape[0] == int(0.2 * len(X))
    
    def test_preprocess_for_ml(self, sample_data):
        """Test preprocess_for_ml function."""
        X, y = sample_data
        
        result = preprocess_for_ml(
            X, y, 
            task_type='classification',
            test_size=0.2,
            validation_size=0.2,
            random_state=42
        )
        
        # Check return structure
        assert isinstance(result, dict)
        required_keys = [
            'X_train', 'X_val', 'X_test',
            'y_train', 'y_val', 'y_test',
            'pipeline', 'report', 'original_shapes'
        ]
        
        for key in required_keys:
            assert key in result
        
        # Check data types
        assert isinstance(result['X_train'], pd.DataFrame)
        assert isinstance(result['X_val'], pd.DataFrame)
        assert isinstance(result['X_test'], pd.DataFrame)
        assert isinstance(result['y_train'], pd.Series)
        assert isinstance(result['y_val'], pd.Series)
        assert isinstance(result['y_test'], pd.Series)
        assert isinstance(result['pipeline'], PreprocessingPipeline)
        assert isinstance(result['report'], PreprocessingReport)
        
        # Check shapes
        total_samples = len(X)
        expected_train = int(0.6 * total_samples)  # 60% train
        expected_val = int(0.2 * total_samples)    # 20% validation
        expected_test = int(0.2 * total_samples)   # 20% test
        
        assert result['X_train'].shape[0] == expected_train
        assert result['X_val'].shape[0] == expected_val
        assert result['X_test'].shape[0] == expected_test
        
        # Check that all datasets have same number of features
        assert result['X_train'].shape[1] == result['X_val'].shape[1] == result['X_test'].shape[1]
    
    def test_preprocess_for_ml_regression(self, sample_data):
        """Test preprocess_for_ml with regression task."""
        X, _ = sample_data
        
        # Create regression target
        y_reg = np.random.randn(len(X))
        
        result = preprocess_for_ml(
            X, y_reg, 
            task_type='regression',
            test_size=0.2,
            validation_size=0.2,
            random_state=42
        )
        
        assert isinstance(result, dict)
        assert isinstance(result['pipeline'], PreprocessingPipeline)
        assert isinstance(result['report'], PreprocessingReport)
    
    def test_preprocess_for_ml_without_target(self, sample_data):
        """Test preprocess_for_ml without target variable."""
        X, _ = sample_data
        
        result = preprocess_for_ml(
            X, 
            test_size=0.2,
            validation_size=0.2,
            random_state=42
        )
        
        assert isinstance(result, dict)
        assert result['y_train'] is None
        assert result['y_val'] is None
        assert result['y_test'] is None
        assert isinstance(result['pipeline'], PreprocessingPipeline)
        assert isinstance(result['report'], PreprocessingReport)


class TestPreprocessingReport:
    """Test preprocessing report functionality."""
    
    def test_report_post_init(self):
        """Test report post-init calculations."""
        report = PreprocessingReport(
            original_shape=(100, 10),
            final_shape=(100, 8),
            original_columns=['col1', 'col2'],
            final_columns=['col1'],
            numeric_columns=['col1'],
            categorical_columns=['col2'],
            scaling_applied=True,
            encoding_applied=True,
            imputation_applied=False,
            feature_selection_applied=True,
            feature_engineering_applied=False,
            dropped_columns=['col2'],
            imputed_columns=[],
            scaled_columns=['col1'],
            encoded_columns=['col2'],
            selected_features=['col1'],
            missing_values_before=5,
            missing_values_after=0,
            config=PreprocessingConfig()
        )
        
        assert report.dimensionality_change == -2
        assert report.feature_reduction_ratio == 0.2
    
    def test_report_no_change(self):
        """Test report with no dimensionality change."""
        report = PreprocessingReport(
            original_shape=(100, 10),
            final_shape=(100, 10),
            original_columns=['col1', 'col2'],
            final_columns=['col1', 'col2'],
            numeric_columns=['col1'],
            categorical_columns=['col2'],
            scaling_applied=False,
            encoding_applied=False,
            imputation_applied=False,
            feature_selection_applied=False,
            feature_engineering_applied=False,
            dropped_columns=[],
            imputed_columns=[],
            scaled_columns=[],
            encoded_columns=[],
            selected_features=['col1', 'col2'],
            missing_values_before=0,
            missing_values_after=0,
            config=PreprocessingConfig()
        )
        
        assert report.dimensionality_change == 0
        assert report.feature_reduction_ratio == 0.0


class TestErrorHandling:
    """Test error handling in preprocessing."""
    
    def test_invalid_enum_values(self):
        """Test handling of invalid enum values."""
        with pytest.raises(ValueError):
            ScalingMethod("invalid_method")
        
        with pytest.raises(ValueError):
            EncodingMethod("invalid_method")
        
        with pytest.raises(ValueError):
            SelectionMethod("invalid_method")
        
        with pytest.raises(ValueError):
            ImputationMethod("invalid_method")
    
    def test_pipeline_with_empty_dataframe(self):
        """Test pipeline with empty DataFrame."""
        pipeline = PreprocessingPipeline()
        
        # Empty DataFrame should still work
        X = pd.DataFrame()
        
        with pytest.raises(Exception):  # Should raise some error
            pipeline.fit(X)
    
    def test_pipeline_with_single_column(self):
        """Test pipeline with single column."""
        pipeline = PreprocessingPipeline()
        
        X = pd.DataFrame({'col1': [1, 2, 3, 4, 5]})
        X_transformed = pipeline.fit_transform(X)
        
        assert isinstance(X_transformed, pd.DataFrame)
        assert X_transformed.shape[0] == 5
        assert X_transformed.shape[1] >= 1


@pytest.mark.integration
class TestIntegration:
    """Integration tests for preprocessing pipeline."""
    
    def test_end_to_end_workflow(self):
        """Test complete end-to-end preprocessing workflow."""
        # Create realistic dataset
        X, y = make_classification(
            n_samples=200, n_features=20, n_redundant=5,
            n_informative=15, n_clusters_per_class=2, random_state=42
        )
        
        # Add categorical features
        n_samples = X.shape[0]
        categorical_data = np.column_stack([
            np.random.choice(['A', 'B', 'C', 'D'], size=n_samples),
            np.random.choice(['X', 'Y', 'Z'], size=n_samples),
            np.random.choice(['High', 'Medium', 'Low'], size=n_samples)
        ])
        
        # Create DataFrame
        feature_names = [f'numeric_{i}' for i in range(20)]
        categorical_names = ['category_1', 'category_2', 'category_3']
        
        df = pd.DataFrame(X, columns=feature_names)
        for i, cat_name in enumerate(categorical_names):
            df[cat_name] = categorical_data[:, i]
        
        # Add missing values
        df.loc[10:15, 'numeric_0'] = np.nan
        df.loc[20:25, 'category_1'] = None
        
        target = pd.Series(y, name='target')
        
        # Use preprocess_for_ml for complete workflow
        result = preprocess_for_ml(
            df, target,
            task_type='classification',
            test_size=0.2,
            validation_size=0.2,
            random_state=42
        )
        
        # Verify everything worked
        assert isinstance(result['X_train'], pd.DataFrame)
        assert isinstance(result['pipeline'], PreprocessingPipeline)
        assert isinstance(result['report'], PreprocessingReport)
        
        # Verify no missing values
        assert result['X_train'].isnull().sum().sum() == 0
        assert result['X_val'].isnull().sum().sum() == 0
        assert result['X_test'].isnull().sum().sum() == 0
        
        # Verify shapes are consistent
        n_features = result['X_train'].shape[1]
        assert result['X_val'].shape[1] == n_features
        assert result['X_test'].shape[1] == n_features
        
        # Verify pipeline can be saved and loaded
        with tempfile.NamedTemporaryFile(suffix='.pkl', delete=False) as tmp:
            result['pipeline'].save_pipeline(tmp.name)
            loaded_pipeline = PreprocessingPipeline.load_pipeline(tmp.name)
            
            # Test loaded pipeline works - get raw test data from original splits
            from sklearn.model_selection import train_test_split
            X_train_raw, X_temp, y_train_raw, y_temp = train_test_split(
                df, target, test_size=0.4, random_state=42
            )
            X_val_raw, X_test_raw, y_val_raw, y_test_raw = train_test_split(
                X_temp, y_temp, test_size=0.5, random_state=42
            )
            
            # Transform raw test data with loaded pipeline
            X_test_loaded = loaded_pipeline.transform(X_test_raw)
            
            # Compare shapes (should be consistent)
            assert X_test_loaded.shape[0] == result['X_test'].shape[0]
            assert X_test_loaded.shape[1] == result['X_test'].shape[1]
            
            # Clean up
            os.unlink(tmp.name) 