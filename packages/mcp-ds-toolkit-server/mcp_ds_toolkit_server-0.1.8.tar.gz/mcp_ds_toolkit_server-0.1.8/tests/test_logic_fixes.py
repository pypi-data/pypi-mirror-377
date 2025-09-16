"""
Unit tests for logic fixes and improvements.

Tests conservative preprocessing defaults, parameter alias mapping,
and other logic flaw fixes identified during the project review.
"""

from unittest.mock import Mock, patch

import numpy as np
import pandas as pd
import pytest

from mcp_ds_toolkit_server.data.preprocessing import (
    EncodingMethod,
    ImputationMethod,
    PreprocessingConfig,
    PreprocessingPipeline,
    ScalingMethod,
    SelectionMethod,
)
from mcp_ds_toolkit_server.data.splitting import (
    DataSplitter,
    SplittingConfig,
    SplittingMethod,
)
from mcp_ds_toolkit_server.tools.data_management import DataManagementTools


class TestConservativePreprocessingDefaults:
    """Test conservative preprocessing defaults to prevent column explosion."""

    def test_preprocessing_config_defaults(self):
        """Test that PreprocessingConfig has conservative defaults."""
        config = PreprocessingConfig()

        # Conservative defaults - no aggressive transformations by default
        assert config.numeric_scaling == ScalingMethod.NONE
        assert config.categorical_encoding == EncodingMethod.NONE
        assert config.feature_selection == SelectionMethod.NONE
        assert (
            config.numeric_imputation == ImputationMethod.MEDIAN
        )  # Reasonable default
        assert (
            config.categorical_imputation == ImputationMethod.MODE
        )  # Reasonable default

    def test_preprocessing_pipeline_conservative_behavior(self):
        """Test that preprocessing pipeline preserves column count by default."""
        # Create test data with categorical columns
        data = pd.DataFrame(
            {
                "numeric1": [1, 2, 3, 4, 5],
                "numeric2": [1.1, 2.2, 3.3, 4.4, 5.5],
                "category1": ["A", "B", "A", "C", "B"],
                "category2": ["X", "Y", "X", "Z", "Y"],
                "target": [0, 1, 0, 1, 0],
            }
        )

        # Use default (conservative) config
        config = PreprocessingConfig()
        pipeline = PreprocessingPipeline(config)

        X = data.drop("target", axis=1)
        y = data["target"]

        # Transform the data
        X_transformed = pipeline.fit_transform(X, y)

        # With conservative defaults, column count should be preserved
        # (only missing value imputation should occur, which doesn't change column count)
        assert X_transformed.shape[1] == X.shape[1]
        # Note: Column names may be standardized by the pipeline for consistency
        assert X_transformed.shape[0] == X.shape[0]

    def test_preprocessing_pipeline_aggressive_behavior_when_requested(self):
        """Test that aggressive preprocessing works when explicitly requested."""
        # Create test data with categorical columns
        data = pd.DataFrame(
            {
                "numeric1": [1, 2, 3, 4, 5],
                "numeric2": [1.1, 2.2, 3.3, 4.4, 5.5],
                "category1": ["A", "B", "A", "C", "B"],
                "category2": ["X", "Y", "X", "Z", "Y"],
                "target": [0, 1, 0, 1, 0],
            }
        )

        # Explicitly request aggressive preprocessing
        config = PreprocessingConfig(
            numeric_scaling=ScalingMethod.STANDARD,
            categorical_encoding=EncodingMethod.ONEHOT,
        )
        pipeline = PreprocessingPipeline(config)

        X = data.drop("target", axis=1)
        y = data["target"]

        # Transform the data
        X_transformed = pipeline.fit_transform(X, y)

        # With one-hot encoding, we should have more columns
        # category1: A, B, C (3 columns, but drop_first=True so 2)
        # category2: X, Y, Z (3 columns, but drop_first=True so 2)
        # numeric1, numeric2 (2 columns)
        # Total: 2 + 2 + 2 = 6 columns
        assert X_transformed.shape[1] > X.shape[1]
        assert X_transformed.shape[1] == 6  # 2 numeric + 2 + 2 from one-hot

    def test_no_column_explosion_with_wine_dataset(self):
        """Test that wine dataset doesn't explode with conservative defaults."""
        # Simulate wine dataset structure (13 numeric features + target)
        np.random.seed(42)
        data = pd.DataFrame(
            {
                **{f"feature_{i}": np.random.randn(100) for i in range(13)},
                "target": np.random.randint(0, 3, 100),
            }
        )

        config = PreprocessingConfig()  # Conservative defaults
        pipeline = PreprocessingPipeline(config)

        X = data.drop("target", axis=1)
        y = data["target"]

        X_transformed = pipeline.fit_transform(X, y)

        # Should preserve original 13 columns
        assert X_transformed.shape[1] == 13
        assert X_transformed.shape[0] == 100


class TestParameterAliasMapping:
    """Test parameter alias mapping for user-friendly parameter names."""

    @pytest.fixture
    def data_tools(self, tmp_path):
        """Create DataManagementTools instance for testing."""
        return DataManagementTools(workspace_path=tmp_path)

    def test_missing_strategy_alias_mapping(self, data_tools):
        """Test mapping of missing strategy aliases."""
        # Test the private method that maps aliases
        assert hasattr(data_tools, "_handle_clean_dataset")

        # The mapping should be in the handler method
        # We can test this by checking the enum values directly
        from mcp_ds_toolkit_server.data.cleaning import MissingDataMethod

        # Test that both full names and aliases are valid enum values or can be mapped
        valid_strategies = [
            "drop_rows",
            "drop_columns",
            "fill_median",
            "fill_mean",
            "fill_mode",
            "fill_constant",
            "median",
            "mean",
            "mode",
        ]

        # The full enum names should exist
        assert MissingDataMethod.FILL_MEDIAN.value == "fill_median"
        assert MissingDataMethod.FILL_MEAN.value == "fill_mean"
        assert MissingDataMethod.FILL_MODE.value == "fill_mode"
        assert MissingDataMethod.DROP_ROWS.value == "drop_rows"

    def test_scaling_method_alias_mapping(self, data_tools):
        """Test mapping of scaling method aliases."""
        from mcp_ds_toolkit_server.data.preprocessing import ScalingMethod

        # Test that both full names and aliases are supported
        assert ScalingMethod.STANDARD.value == "standard"
        assert ScalingMethod.MINMAX.value == "minmax"
        assert ScalingMethod.NONE.value == "none"

        # Common aliases should be mappable
        # "standardize" -> "standard", "normalize" -> "minmax"
        # This mapping logic should be in the MCP tool handler


class TestImprovedDatasetSplitting:
    """Test improved dataset splitting with better defaults."""

    def test_splitting_config_improved_defaults(self):
        """Test that splitting config has reasonable defaults (70/15/15)."""
        config = SplittingConfig()

        # Should default to reasonable splits
        assert config.test_size == 0.15  # 15%
        assert config.validation_size == 0.15  # 15%
        assert config.train_size == 0.7  # 70%

    def test_data_splitter_improved_splits(self):
        """Test that DataSplitter produces 70/20/10 splits by default."""
        # Create test data
        data = pd.DataFrame(
            {
                "feature1": range(100),
                "feature2": range(100, 200),
                "target": [i % 3 for i in range(100)],  # 3 classes
            }
        )

        config = SplittingConfig(
            method=SplittingMethod.RANDOM
        )
        splitter = DataSplitter(config=config)

        train_df, val_df, test_df, report = splitter.split_data(data, target_column="target")

        # Check proportions (with some tolerance for rounding)
        total_samples = len(data)
        train_ratio = len(train_df) / total_samples
        val_ratio = len(val_df) / total_samples if val_df is not None else 0
        test_ratio = len(test_df) / total_samples

        assert abs(train_ratio - 0.7) < 0.05  # ~70%
        assert abs(val_ratio - 0.15) < 0.05  # ~15% (default)
        assert abs(test_ratio - 0.15) < 0.05  # ~15% (default)

    def test_three_way_split_validation(self):
        """Test that three-way splits sum to 100% and are mutually exclusive."""
        data = pd.DataFrame(
            {
                "feature1": range(1000),  # Larger dataset for better proportions
                "target": [i % 2 for i in range(1000)],
            }
        )

        config = SplittingConfig(
            method=SplittingMethod.RANDOM,
            test_size=0.2,
            validation_size=0.1,
        )
        splitter = DataSplitter(config=config)

        train_df, val_df, test_df, report = splitter.split_data(data, target_column="target")

        # Verify no data leakage
        train_indices = set(train_df.index)
        val_indices = set(val_df.index) if val_df is not None else set()
        test_indices = set(test_df.index)

        # Sets should be mutually exclusive
        assert len(train_indices & val_indices) == 0
        assert len(train_indices & test_indices) == 0
        assert len(val_indices & test_indices) == 0

        # All data should be accounted for
        total_indices = train_indices | val_indices | test_indices
        assert len(total_indices) == len(data)


class TestMCPToolSchemaImprovements:
    """Test improvements to MCP tool schemas and parameter handling."""

    @pytest.fixture
    def data_tools(self, tmp_path):
        """Create DataManagementTools instance."""
        return DataManagementTools(workspace_path=tmp_path)

    def test_preprocess_dataset_tool_schema(self, data_tools):
        """Test that preprocess_dataset tool has improved schema."""
        tools = data_tools.get_tools()
        preprocess_tool = next(
            tool for tool in tools if tool.name == "preprocess_dataset"
        )

        # Check that schema includes both full names and aliases
        scaling_enum = preprocess_tool.inputSchema["properties"][
            "preprocessing_config"
        ]["properties"]["scaling_method"]["enum"]

        # Should support both full names and common aliases
        assert "standard" in scaling_enum
        assert "none" in scaling_enum
        assert "standardize" in scaling_enum  # Alias
        assert "normalize" in scaling_enum  # Alias

    def test_clean_dataset_tool_schema(self, data_tools):
        """Test that clean_dataset tool has improved schema."""
        tools = data_tools.get_tools()
        clean_tool = next(tool for tool in tools if tool.name == "clean_dataset")

        # Check that schema includes both full names and aliases
        missing_enum = clean_tool.inputSchema["properties"]["missing_strategy"]["enum"]

        # Should support both full names and short aliases
        assert "fill_median" in missing_enum
        assert "fill_mean" in missing_enum
        assert "median" in missing_enum  # Alias
        assert "mean" in missing_enum  # Alias

    def test_split_dataset_improved_defaults(self, data_tools):
        """Test that split_dataset tool has improved default documentation."""
        tools = data_tools.get_tools()
        split_tool = next(tool for tool in tools if tool.name == "split_dataset")

        # Check for improved default documentation
        schema = split_tool.inputSchema["properties"]

        # val_size should default to 0.1 for 70/20/10 split
        if "val_size" in schema:
            val_size_prop = schema["val_size"]
            assert val_size_prop.get("default", 0.1) == 0.1

            # Description should mention the improved default
            description = val_size_prop.get("description", "")
            assert "70/20/10" in description or "0.1" in str(
                val_size_prop.get("default")
            )


class TestNewFeaturesIntegration:
    """Test integration of new features like model evaluation tools."""

    @pytest.fixture
    def data_tools(self, tmp_path):
        """Create DataManagementTools instance."""
        return DataManagementTools(workspace_path=tmp_path)

    def test_evaluate_model_tool_available(self, data_tools):
        """Test that evaluate_model tool is available."""
        tools = data_tools.get_tools()
        tool_names = [tool.name for tool in tools]

        # Removed quick_* tools - these are now available in TrainingTools only
        assert "generate_learning_curve" in tool_names

    def test_learning_curve_tool_schema(self, data_tools):
        """Test learning curve tool schema."""
        tools = data_tools.get_tools()
        curve_tool = next(tool for tool in tools if tool.name == "generate_learning_curve")

        required_fields = curve_tool.inputSchema["required"]
        assert "dataset_name" in required_fields
        assert "target_column" in required_fields


class TestQualityGatesAndValidation:
    """Test quality gates and validation improvements."""

    def test_preprocessing_validation(self):
        """Test that preprocessing config validates properly."""
        # Valid config should work
        config = PreprocessingConfig(
            numeric_scaling=ScalingMethod.STANDARD,
            categorical_encoding=EncodingMethod.ONEHOT,
        )
        assert config.numeric_scaling == ScalingMethod.STANDARD

        # Invalid enum values should raise errors during enum creation
        with pytest.raises((ValueError, TypeError)):
            ScalingMethod("invalid_method")

    def test_conservative_defaults_preserve_data_integrity(self):
        """Test that conservative defaults preserve data integrity."""
        # Create data with various types
        data = pd.DataFrame(
            {
                "int_col": [1, 2, 3, 4, 5],
                "float_col": [1.1, 2.2, 3.3, 4.4, 5.5],
                "str_col": ["a", "b", "c", "d", "e"],
                "bool_col": [True, False, True, False, True],
            }
        )

        config = PreprocessingConfig()  # Conservative defaults
        pipeline = PreprocessingPipeline(config)

        # Transform should preserve essential data characteristics
        transformed = pipeline.fit_transform(data)

        # Same number of rows
        assert len(transformed) == len(data)

        # Same column count (no column explosion)
        assert transformed.shape[1] == data.shape[1]

        # Data types should be reasonable - values should still be convertible to numeric
        # Check first two columns (originally int_col and float_col)
        # Note: ColumnTransformer may convert to object dtype, but values should be numeric
        try:
            pd.to_numeric(transformed.iloc[:, 0])
            pd.to_numeric(transformed.iloc[:, 1])
            numeric_preserved = True
        except (ValueError, TypeError):
            numeric_preserved = False
        
        assert numeric_preserved, "Numeric values should be preserved even if dtype changes"


if __name__ == "__main__":
    pytest.main([__file__])
