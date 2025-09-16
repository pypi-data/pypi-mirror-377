"""
Tests for data management MCP tools.
"""

import json
import shutil
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import numpy as np
import pandas as pd
import pytest
from mcp.types import TextContent, Tool

from mcp_ds_toolkit_server.tools.data_management import DataManagementTools


def parse_tool_result(result_text):
    """Parse tool result that could be either JSON or plain text."""
    try:
        return json.loads(result_text)
    except json.JSONDecodeError:
        return {"text_response": result_text}


def check_success_result(result, expected_status="success"):
    """Check if result indicates success, handling both JSON and text formats."""
    if isinstance(result, dict):
        if "status" in result:
            return result["status"] == expected_status
        elif "text_response" in result:
            return "success" in result["text_response"].lower()
    return False


class TestDataManagementTools:
    """Tests for DataManagementTools class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.tools = DataManagementTools(workspace_path=self.temp_dir)

        # Create sample dataset
        self.sample_data = pd.DataFrame(
            {
                "feature1": np.random.normal(0, 1, 100),
                "feature2": np.random.normal(5, 2, 100),
                "category": np.random.choice(["A", "B", "C"], 100),
                "target": np.random.randint(0, 2, 100),
            }
        )

        # Save sample dataset to temp file
        self.sample_file = Path(self.temp_dir) / "sample.csv"
        self.sample_data.to_csv(self.sample_file, index=False)

    def teardown_method(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir)

    def test_get_tools(self):
        """Test getting available tools."""
        tools = self.tools.get_tools()

        assert isinstance(tools, list)
        assert len(tools) > 0

        # Check that all tools are Tool instances
        for tool in tools:
            assert isinstance(tool, Tool)
            assert hasattr(tool, "name")
            assert hasattr(tool, "description")
            assert hasattr(tool, "inputSchema")

        # Check for expected tools
        tool_names = [tool.name for tool in tools]
        expected_tools = [
            "load_dataset",
            "validate_dataset",
            "profile_dataset",
            "preprocess_dataset",
            "clean_dataset",
            "split_dataset",
            "list_datasets",
            "get_dataset_info",
            "export_dataset",
        ]

        for expected_tool in expected_tools:
            assert expected_tool in tool_names

    @pytest.mark.asyncio
    async def test_load_dataset_csv(self):
        """Test loading CSV dataset."""
        arguments = {
            "source": str(self.sample_file),
            "format": "csv",
            "name": "test_dataset",
        }

        result = await self.tools.handle_tool_call("load_dataset", arguments)

        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], TextContent)
        # Check result using flexible parser
        data = parse_tool_result(result[0].text)
        assert check_success_result(data)
        assert "test_dataset" in self.tools.datasets
        assert self.tools.datasets["test_dataset"].shape == self.sample_data.shape

    @pytest.mark.asyncio
    async def test_validate_dataset(self):
        """Test dataset validation."""
        # First load a dataset
        self.tools.datasets["test_dataset"] = self.sample_data.copy()

        arguments = {
            "dataset_name": "test_dataset",
            "validation_rules": {
                "required_columns": ["feature1", "feature2"],
                "min_rows": 50,
                "max_missing_ratio": 0.1,
            },
        }

        result = await self.tools.handle_tool_call("validate_dataset", arguments)

        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], TextContent)
        # Check result using flexible parser
        data = parse_tool_result(result[0].text)
        assert "validation" in data or "validation" in result[0].text.lower()

    @pytest.mark.asyncio
    async def test_profile_dataset(self):
        """Test dataset profiling."""
        # First load a dataset
        self.tools.datasets["test_dataset"] = self.sample_data.copy()

        arguments = {
            "dataset_name": "test_dataset",
            "include_correlations": True,
            "include_distributions": True,
        }

        result = await self.tools.handle_tool_call("profile_dataset", arguments)

        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], TextContent)
        # Check result using flexible parser
        data = parse_tool_result(result[0].text)
        assert "dataset_name" in data or "test_dataset" in result[0].text

    @pytest.mark.asyncio
    async def test_preprocess_dataset(self):
        """Test dataset preprocessing."""
        # First load a dataset
        self.tools.datasets["test_dataset"] = self.sample_data.copy()

        arguments = {
            "dataset_name": "test_dataset",
            "target_column": "target",
            "preprocessing_config": {
                "scaling_method": "standard",
                "encoding_method": "onehot",
                "imputation_strategy": "median",
                "categorical_imputation_strategy": "mode",
            },
            "output_name": "preprocessed_dataset",
        }

        result = await self.tools.handle_tool_call("preprocess_dataset", arguments)

        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], TextContent)
        # Check result using flexible parser
        data = parse_tool_result(result[0].text)
        assert check_success_result(data)
        assert "preprocessed_dataset" in self.tools.datasets

    @pytest.mark.asyncio
    async def test_clean_dataset(self):
        """Test dataset cleaning."""
        # Create dataset with missing values and outliers
        dirty_data = self.sample_data.copy()
        dirty_data.loc[0:5, "feature1"] = np.nan
        dirty_data.loc[90:95, "feature2"] = 1000  # outliers

        self.tools.datasets["dirty_dataset"] = dirty_data

        arguments = {
            "dataset_name": "dirty_dataset",
            "missing_strategy": "fill_median",
            "outlier_strategy": "cap",
            "outlier_method": "iqr",
            "output_name": "clean_dataset",
        }

        result = await self.tools.handle_tool_call("clean_dataset", arguments)

        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], TextContent)
        # Check result using flexible parser
        data = parse_tool_result(result[0].text)
        assert check_success_result(data)
        assert "clean_dataset" in self.tools.datasets

    @pytest.mark.asyncio
    async def test_split_dataset(self):
        """Test dataset splitting."""
        # First load a dataset
        self.tools.datasets["test_dataset"] = self.sample_data.copy()

        arguments = {
            "dataset_name": "test_dataset",
            "split_method": "random",
            "test_size": 0.2,
            "val_size": 0.2,
            "random_state": 42,
        }

        result = await self.tools.handle_tool_call("split_dataset", arguments)

        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], TextContent)
        # Check result using flexible parser
        data = parse_tool_result(result[0].text)
        assert check_success_result(data)

        # Check that splits were created
        assert "test_dataset_train" in self.tools.datasets
        assert "test_dataset_validation" in self.tools.datasets
        assert "test_dataset_test" in self.tools.datasets

    @pytest.mark.asyncio
    async def test_list_datasets(self):
        """Test listing datasets."""
        # Add some datasets
        self.tools.datasets["dataset1"] = self.sample_data.copy()
        self.tools.datasets["dataset2"] = self.sample_data.copy()

        arguments = {"include_details": True}

        result = await self.tools.handle_tool_call("list_datasets", arguments)

        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], TextContent)
        # Check result using flexible parser
        data = parse_tool_result(result[0].text)
        if "datasets" in data:
            dataset_names = [d["name"] for d in data["datasets"]]
            assert "dataset1" in dataset_names
            assert "dataset2" in dataset_names
        else:
            # Text format fallback
            assert "dataset1" in result[0].text
            assert "dataset2" in result[0].text

    @pytest.mark.asyncio
    async def test_get_dataset_info(self):
        """Test getting dataset information."""
        # First load a dataset
        self.tools.datasets["test_dataset"] = self.sample_data.copy()
        self.tools.dataset_metadata["test_dataset"] = {
            "source": "test_source",
            "loaded_at": "2023-01-01T00:00:00",
        }

        arguments = {
            "dataset_name": "test_dataset",
            "include_sample": True,
            "sample_size": 5,
        }

        result = await self.tools.handle_tool_call("get_dataset_info", arguments)

        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], TextContent)
        # Check result using flexible parser
        data = parse_tool_result(result[0].text)
        assert "dataset_name" in data or "test_dataset" in result[0].text

    @pytest.mark.asyncio
    async def test_export_dataset(self):
        """Test exporting dataset."""
        # First load a dataset
        self.tools.datasets["test_dataset"] = self.sample_data.copy()

        export_path = Path(self.temp_dir) / "exported.csv"
        arguments = {
            "dataset_name": "test_dataset",
            "output_path": str(export_path),
            "format": "csv",
        }

        result = await self.tools.handle_tool_call("export_dataset", arguments)

        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], TextContent)
        # Check result using flexible parser
        data = parse_tool_result(result[0].text)
        assert check_success_result(data)
        assert export_path.exists()

    @pytest.mark.asyncio
    async def test_dataset_not_found_error(self):
        """Test error handling when dataset not found."""
        arguments = {"dataset_name": "nonexistent_dataset"}

        result = await self.tools.handle_tool_call("validate_dataset", arguments)

        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], TextContent)
        # Check for error in flexible format
        data = parse_tool_result(result[0].text)
        is_error = ("status" in data and data["status"] == "error") or "not found" in result[0].text.lower()
        assert is_error

    @pytest.mark.asyncio
    async def test_unknown_tool_error(self):
        """Test error handling for unknown tool."""
        arguments = {}

        result = await self.tools.handle_tool_call("unknown_tool", arguments)

        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], TextContent)
        # Unknown tool will likely return an error message, check content flexibly
        assert "unknown" in result[0].text.lower() or "error" in result[0].text.lower()

# DVC functionality removed - using local storage only


class TestDataManagementToolsIntegration:
    """Integration tests for data management tools."""

    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.tools = DataManagementTools(workspace_path=self.temp_dir)

        # Create sample dataset
        self.sample_data = pd.DataFrame(
            {
                "feature1": np.random.normal(0, 1, 100),
                "feature2": np.random.normal(5, 2, 100),
                "category": np.random.choice(["A", "B", "C"], 100),
                "target": np.random.randint(0, 2, 100),
            }
        )

        # Save sample dataset to temp file
        self.sample_file = Path(self.temp_dir) / "sample.csv"
        self.sample_data.to_csv(self.sample_file, index=False)

    def teardown_method(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir)

    @pytest.mark.asyncio
    async def test_full_data_pipeline(self):
        """Test complete data management pipeline."""
        # 1. Load dataset
        load_args = {
            "source": str(self.sample_file),
            "format": "csv",
            "name": "pipeline_dataset",
        }
        result = await self.tools.handle_tool_call("load_dataset", load_args)
        data = parse_tool_result(result[0].text)
        assert check_success_result(data)

        # 2. Validate dataset
        validate_args = {
            "dataset_name": "pipeline_dataset",
            "validation_rules": {
                "required_columns": ["feature1", "feature2"],
                "min_rows": 50,
            },
        }
        result = await self.tools.handle_tool_call("validate_dataset", validate_args)
        data = parse_tool_result(result[0].text)
        assert "validation" in data or "validation" in result[0].text.lower()

        # 3. Profile dataset
        profile_args = {
            "dataset_name": "pipeline_dataset",
            "include_correlations": True,
        }
        result = await self.tools.handle_tool_call("profile_dataset", profile_args)
        data = parse_tool_result(result[0].text)
        assert "dataset_name" in data or "dataset" in result[0].text.lower()

        # 4. Clean dataset
        clean_args = {
            "dataset_name": "pipeline_dataset",
            "missing_strategy": "fill_median",
            "outlier_strategy": "cap",
            "outlier_method": "iqr",
            "output_name": "clean_dataset",
        }
        result = await self.tools.handle_tool_call("clean_dataset", clean_args)
        data = parse_tool_result(result[0].text)
        assert check_success_result(data)

        # 5. Preprocess dataset
        preprocess_args = {
            "dataset_name": "clean_dataset",
            "target_column": "target",
            "preprocessing_config": {
                "scaling_method": "standard",
                "encoding_method": "onehot",
            },
            "output_name": "preprocessed_dataset",
        }
        result = await self.tools.handle_tool_call(
            "preprocess_dataset", preprocess_args
        )
        data = parse_tool_result(result[0].text)
        assert check_success_result(data)

        # 6. Split dataset
        split_args = {
            "dataset_name": "preprocessed_dataset",
            "split_method": "random",
            "test_size": 0.2,
            "val_size": 0.2,
        }
        result = await self.tools.handle_tool_call("split_dataset", split_args)
        data = parse_tool_result(result[0].text)
        assert check_success_result(data)

        # 7. List all datasets
        list_args = {"include_details": True}
        result = await self.tools.handle_tool_call("list_datasets", list_args)
        data = parse_tool_result(result[0].text)
        assert "datasets" in data or "dataset" in result[0].text.lower()

        # Verify we have all expected datasets
        expected_datasets = [
            "pipeline_dataset",
            "clean_dataset",
            "preprocessed_dataset",
            "preprocessed_dataset_train",
            "preprocessed_dataset_validation",
            "preprocessed_dataset_test",
        ]

        for dataset_name in expected_datasets:
            assert dataset_name in self.tools.datasets
            if "datasets" in data:
                dataset_names = [d["name"] for d in data["datasets"]]
                assert dataset_name in dataset_names
            else:
                assert dataset_name in result[0].text

    @pytest.mark.asyncio
    async def test_error_propagation(self):
        """Test that errors are properly handled and propagated."""
        # Test with invalid file path
        load_args = {
            "source": "/nonexistent/file.csv",
            "format": "csv",
            "name": "error_dataset",
        }

        result = await self.tools.handle_tool_call("load_dataset", load_args)
        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], TextContent)
        assert "error" in result[0].text.lower() or "not found" in result[0].text.lower()
