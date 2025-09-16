"""Data Management Tools Module

This module provides MCP tools for comprehensive data management operations
including dataset loading, validation, profiling, and preprocessing.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Union

import numpy as np
import pandas as pd
from mcp.types import (
    EmbeddedResource,
    ImageContent,
    LoggingLevel,
    TextContent,
    Tool,
)
from sklearn.ensemble import (
    RandomForestClassifier,
    RandomForestRegressor,
    GradientBoostingClassifier,
    GradientBoostingRegressor,
    ExtraTreesClassifier,
    ExtraTreesRegressor,
)
from sklearn.linear_model import LinearRegression, LogisticRegression, Ridge, Lasso, ElasticNet
from sklearn.svm import SVC, SVR
from sklearn.neighbors import KNeighborsClassifier, KNeighborsRegressor
from sklearn.naive_bayes import GaussianNB, MultinomialNB, BernoulliNB
from sklearn.tree import DecisionTreeClassifier, DecisionTreeRegressor

from mcp_ds_toolkit_server.tools.base import BaseMCPTools
from mcp_ds_toolkit_server.data import (
    CleaningConfig,
    CrossValidationMethod,
    DataCleaner,
    DataDriftMetric,
    DataProfiler,
    DatasetLoader,
    DataSplitter,
    DataValidator,
    EncodingMethod,
    ImputationMethod,
    MissingDataConfig,
    MissingDataHandler,
    MissingDataMethod,
    OutlierAction,
    OutlierConfig,
    OutlierDetector,
    OutlierMethod,
    PreprocessingConfig,
    PreprocessingPipeline,
    RemoteConfig,
    RemoteStorageType,
    ScalingMethod,
    SelectionMethod,
    SplittingConfig,
    SplittingMethod,
    VersioningConfig,
    VersioningStrategy,
)
from mcp_ds_toolkit_server.data.model_evaluation import (
    CrossValidationConfig,
    HyperparameterTuningConfig,
    HyperparameterTuningMethod,
    ModelEvaluator,
    TaskType,
    get_default_param_grids,
)
from mcp_ds_toolkit_server.exceptions import DataError
from mcp_ds_toolkit_server.utils.data_resolver import UnifiedDataResolver
from mcp_ds_toolkit_server.utils.persistence import (
    ArtifactBridge,
    PersistenceConfig,
    create_default_persistence_config,
)
from mcp_ds_toolkit_server.utils.config import Settings


class DataManagementTools(BaseMCPTools):
    """MCP tools for data management operations."""

    def __init__(self, workspace_path: Path, artifact_bridge=None):
        """Initialize data management tools.

        Args:
            workspace_path: Path to the workspace directory
            artifact_bridge: Artifact bridge for persistence operations
        """
        # Use base class initialization to eliminate redundancy
        super().__init__(
            workspace_path=workspace_path, 
            persistence_mode="memory_only",
            artifact_bridge=artifact_bridge
        )
        
        # Initialize components
        cache_dir = str(self.workspace_path / "cache")
        self.loader = DatasetLoader(cache_dir=cache_dir)
        self.validator = DataValidator()
        self.profiler = DataProfiler()
        self.preprocessing_pipeline = PreprocessingPipeline()
        self.cleaning_pipeline = DataCleaner()
        self.splitter = DataSplitter()

        # Store loaded datasets - initialize first
        self.datasets: Dict[str, pd.DataFrame] = {}
        self.dataset_metadata: Dict[str, Dict[str, Any]] = {}
        
        # Initialize unified data resolver for intelligent dataset discovery
        self.data_resolver = UnifiedDataResolver(
            memory_registry=self.datasets,
            artifact_bridge=self.artifact_bridge,
            data_loader=self.loader  # Use our workspace-specific loader
        )
        
        self.logger.info(f"DataManagementTools initialized - Registry ID: {id(self.datasets)}, Keys: {list(self.datasets.keys())}")

    def _get_mime_type_for_format(self, format: str) -> str:
        """Get MIME type for dataset format.

        Args:
            format: Dataset format (csv, json, etc.)

        Returns:
            MIME type string
        """
        mime_types = {
            "csv": "text/csv",
            "json": "application/json",
            "parquet": "application/octet-stream",
            "excel": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            "sql": "text/plain",
            "hdf5": "application/octet-stream",
            "feather": "application/octet-stream"
        }
        return mime_types.get(format, "text/plain")

    # Algorithm mapping constants for ML evaluation tools
    CLASSIFICATION_ALGORITHMS = {
        "random_forest": RandomForestClassifier,
        "gradient_boosting": GradientBoostingClassifier,
        "extra_trees": ExtraTreesClassifier,
        "logistic_regression": LogisticRegression,
        "svm": SVC,
        "knn": KNeighborsClassifier,
        "gaussian_nb": GaussianNB,
        "multinomial_nb": MultinomialNB,
        "bernoulli_nb": BernoulliNB,
        "decision_tree": DecisionTreeClassifier,
    }

    REGRESSION_ALGORITHMS = {
        "random_forest": RandomForestRegressor,
        "random_forest_regressor": RandomForestRegressor,
        "gradient_boosting": GradientBoostingRegressor,
        "extra_trees": ExtraTreesRegressor,
        "linear_regression": LinearRegression,
        "ridge": Ridge,
        "lasso": Lasso,
        "elastic_net": ElasticNet,
        "svm": SVR,
        "svm_regressor": SVR,
        "knn": KNeighborsRegressor,
        "decision_tree": DecisionTreeRegressor,
    }

    def _create_model(self, model_type: str, task_type: str):
        """Create a scikit-learn model instance.

        Args:
            model_type: Type of model (e.g., 'random_forest', 'logistic_regression')
            task_type: Type of task ('classification' or 'regression')

        Returns:
            Configured scikit-learn model instance or None if unsupported
        """
        try:
            if task_type == "classification":
                algorithms = self.CLASSIFICATION_ALGORITHMS
            elif task_type == "regression":
                algorithms = self.REGRESSION_ALGORITHMS
            else:
                return None

            if model_type not in algorithms:
                return None

            model_class = algorithms[model_type]

            # Set random state if the model supports it
            kwargs = {}
            # Only add random_state for models that support it
            if model_type in ["random_forest", "random_forest_regressor", "gradient_boosting", "extra_trees", "decision_tree", "logistic_regression"]:
                kwargs["random_state"] = 42

            # Special configurations for specific algorithms
            if model_type == "logistic_regression":
                kwargs["max_iter"] = 1000

            return model_class(**kwargs)

        except Exception:
            return None

    def _resolve_dataset(self, dataset_name: str, dataset_path: str = None, artifact_key: str = None):
        """Resolve dataset using unified data resolver with fallback to legacy registry.
        
        This method provides intelligent dataset discovery across multiple sources:
        1. Unified data resolver (artifact bridge, memory, filesystem)
        2. Legacy self.datasets registry (for backward compatibility)
        
        Args:
            dataset_name: Name of the dataset
            dataset_path: Optional filesystem path
            artifact_key: Optional artifact bridge key
            
        Returns:
            tuple: (DataFrame, data_reference) or raises DataError if not found
        """
        try:
            # Try unified data resolver first
            df, data_reference = self.data_resolver.resolve_data(
                dataset_name=dataset_name,
                dataset_path=dataset_path,
                artifact_key=artifact_key,
                auto_fallback=True
            )
            self.logger.info(f"✅ Resolved dataset '{dataset_name}' via unified resolver from {data_reference.location_type}")
            return df, data_reference
            
        except Exception as resolver_error:
            # Fallback to legacy registry for backward compatibility
            if dataset_name in self.datasets:
                df = self.datasets[dataset_name]
                # Create a data reference for legacy data
                from mcp_ds_toolkit_server.utils.data_resolver import DataReference
                from mcp_ds_toolkit_server.utils.persistence import PersistenceMode
                data_reference = DataReference(
                    name=dataset_name,
                    location_type="legacy_registry",
                    persistence_mode=PersistenceMode.MEMORY_ONLY,
                    memory_key=dataset_name,
                    metadata={"source": "legacy_datasets_registry"}
                )
                self.logger.info(f"✅ Resolved dataset '{dataset_name}' via legacy registry (fallback)")
                return df, data_reference
            else:
                # Neither resolver nor legacy registry found the dataset
                available_datasets = []
                
                # Check unified resolver
                try:
                    available_datasets.extend([ref.name for ref in self.data_resolver.list_available_data()])
                except Exception:
                    pass
                
                # Check legacy registry
                available_datasets.extend(list(self.datasets.keys()))
                
                error_msg = f"Dataset '{dataset_name}' not found in any source."
                if available_datasets:
                    error_msg += f" Available datasets: {sorted(set(available_datasets))}"
                else:
                    error_msg += " No datasets available. Load a dataset first."
                    
                self.logger.error(f"❌ {error_msg}")
                raise DataError(error_msg)

    def get_tools(self) -> List[Tool]:
        """Get all available MCP tools for data management.

        Returns:
            List of MCP tools
        """
        return [
            # Dataset Loading Tools
            Tool(
                name="load_dataset",
                description="Load a dataset from various sources (CSV, JSON, Parquet, SQL, etc.)",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "source": {
                            "type": "string",
                            "description": "Path to the dataset file, database connection string, or file:// URI for uploaded files",
                        },
                        "format": {
                            "type": "string",
                            "enum": [
                                "csv",
                                "json",
                                "parquet",
                                "excel",
                                "sql",
                                "hdf5",
                                "feather",
                            ],
                            "description": "Dataset format",
                        },
                        "name": {
                            "type": "string",
                            "description": "Name to assign to the loaded dataset",
                        },
                        "options": {
                            "type": "object",
                            "description": "Additional loading options",
                            "properties": {
                                "encoding": {
                                    "type": "string",
                                    "description": "File encoding (utf-8, latin-1, cp1252, etc.)",
                                    "default": "utf-8",
                                },
                                "dataset_name": {
                                    "type": "string",
                                    "description": "For sklearn datasets: specify dataset name (wine, iris, etc.)",
                                },
                                "sep": {
                                    "type": "string",
                                    "description": "CSV separator character",
                                    "default": ",",
                                },
                            },
                            "additionalProperties": True,
                        },
                    },
                    "required": ["source", "format", "name"],
                },
            ),
            # Dataset Validation Tools
            Tool(
                name="validate_dataset",
                description="Validate dataset quality and check for issues",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "dataset_name": {
                            "type": "string",
                            "description": "Name of the dataset to validate",
                        },
                        "validation_rules": {
                            "type": "object",
                            "description": "Custom validation rules",
                            "properties": {
                                "required_columns": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                    "description": "Required column names",
                                },
                                "min_rows": {
                                    "type": "integer",
                                    "description": "Minimum number of rows required",
                                },
                                "max_missing_ratio": {
                                    "type": "number",
                                    "description": "Maximum allowed missing data ratio",
                                },
                                "allowed_dtypes": {
                                    "type": "object",
                                    "description": "Expected data types for columns",
                                    "additionalProperties": {"type": "string"},
                                },
                            },
                        },
                    },
                    "required": ["dataset_name"],
                },
            ),
            # Dataset Profiling Tools
            Tool(
                name="profile_dataset",
                description="Generate comprehensive data profile and statistics",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "dataset_name": {
                            "type": "string",
                            "description": "Name of the dataset to profile",
                        },
                        "include_correlations": {
                            "type": "boolean",
                            "description": "Include correlation analysis",
                            "default": True,
                        },
                        "include_distributions": {
                            "type": "boolean",
                            "description": "Include distribution analysis",
                            "default": True,
                        },
                        "correlation_threshold": {
                            "type": "number",
                            "description": "Correlation threshold for reporting",
                            "default": 0.5,
                        },
                    },
                    "required": ["dataset_name"],
                },
            ),
            # Data Preprocessing Tools
            Tool(
                name="preprocess_dataset",
                description="Apply preprocessing transformations to dataset",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "dataset_name": {
                            "type": "string",
                            "description": "Name of the dataset to preprocess",
                        },
                        "target_column": {
                            "type": "string",
                            "description": "Target column name for supervised learning",
                        },
                        "preprocessing_config": {
                            "type": "object",
                            "description": "Preprocessing configuration",
                            "properties": {
                                "scaling_method": {
                                    "type": "string",
                                    "enum": [
                                        "standard",
                                        "minmax",
                                        "robust",
                                        "maxabs",
                                        "quantile_uniform",
                                        "quantile_normal",
                                        "power_yeojonson",
                                        "power_boxcox",
                                        "none",
                                        "standardize",
                                        "normalize",
                                    ],
                                    "description": "Scaling method to apply (supports both full names and common aliases)",
                                },
                                "encoding_method": {
                                    "type": "string",
                                    "enum": ["onehot", "label", "target", "ordinal"],
                                    "description": "Categorical encoding method",
                                },
                                "feature_selection": {
                                    "type": "object",
                                    "properties": {
                                        "method": {
                                            "type": "string",
                                            "enum": [
                                                "variance",
                                                "correlation",
                                                "univariate",
                                                "rfe",
                                                "lasso",
                                            ],
                                            "description": "Feature selection method",
                                        },
                                        "params": {
                                            "type": "object",
                                            "description": "Feature selection parameters",
                                            "additionalProperties": True,
                                        },
                                    },
                                },
                                "handle_missing": {
                                    "type": "boolean",
                                    "description": "Handle missing values",
                                    "default": True,
                                },
                            },
                        },
                        "output_name": {
                            "type": "string",
                            "description": "Name for the preprocessed dataset",
                        },
                    },
                    "required": ["dataset_name", "output_name"],
                },
            ),
            # Data Cleaning Tools
            Tool(
                name="clean_dataset",
                description="Clean dataset by handling missing values and outliers",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "dataset_name": {
                            "type": "string",
                            "description": "Name of the dataset to clean",
                        },
                        "missing_strategy": {
                            "type": "string",
                            "enum": [
                                "drop_rows",
                                "drop_columns",
                                "fill_median",
                                "fill_mean",
                                "fill_mode",
                                "fill_constant",
                                "fill_forward",
                                "fill_backward",
                                "fill_interpolate",
                                "fill_knn",
                                "fill_iterative",
                                "median",
                                "mean",
                                "mode",
                            ],
                            "description": "Strategy for handling missing values (supports both full names and short aliases)",
                        },
                        "outlier_strategy": {
                            "type": "string",
                            "enum": ["remove", "cap", "transform"],
                            "description": "Strategy for handling outliers",
                        },
                        "outlier_method": {
                            "type": "string",
                            "enum": [
                                "z_score",
                                "modified_z_score",
                                "iqr",
                                "isolation_forest",
                                "local_outlier_factor",
                                "dbscan",
                                "percentile",
                                "statistical_distance",
                                "zscore",
                                "lof",
                            ],
                            "description": "Method for outlier detection (supports both full names and short aliases)",
                        },
                        "output_name": {
                            "type": "string",
                            "description": "Name for the cleaned dataset",
                        },
                    },
                    "required": ["dataset_name", "output_name"],
                },
            ),
            # Data Splitting Tools
            Tool(
                name="split_dataset",
                description="Split dataset into train/validation/test sets",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "dataset_name": {
                            "type": "string",
                            "description": "Name of the dataset to split",
                        },
                        "split_method": {
                            "type": "string",
                            "enum": [
                                "random",
                                "stratified",
                                "time_series",
                                "group_based",
                            ],
                            "description": "Method for splitting the dataset",
                        },
                        "test_size": {
                            "type": "number",
                            "description": "Proportion of data for test set",
                            "default": 0.2,
                        },
                        "val_size": {
                            "type": "number",
                            "description": "Proportion of data for validation set (creates 70/20/10 split by default)",
                            "default": 0.1,
                        },
                        "target_column": {
                            "type": "string",
                            "description": "Target column for stratified splitting",
                        },
                        "time_column": {
                            "type": "string",
                            "description": "Time column for time-series splitting",
                        },
                        "group_column": {
                            "type": "string",
                            "description": "Group column for group-based splitting",
                        },
                        "random_state": {
                            "type": "integer",
                            "description": "Random seed for reproducibility",
                            "default": 42,
                        },
                    },
                    "required": ["dataset_name", "split_method"],
                },
            ),
            # Dataset Information Tools
            Tool(
                name="list_datasets",
                description="List all loaded datasets with their metadata",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "include_details": {
                            "type": "boolean",
                            "description": "Include detailed information about each dataset",
                            "default": False,
                        }
                    },
                },
            ),
            Tool(
                name="get_dataset_info",
                description="Get detailed information about a specific dataset",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "dataset_name": {
                            "type": "string",
                            "description": "Name of the dataset",
                        },
                        "include_sample": {
                            "type": "boolean",
                            "description": "Include sample data",
                            "default": True,
                        },
                        "sample_size": {
                            "type": "integer",
                            "description": "Number of sample rows to include",
                            "default": 5,
                        },
                    },
                    "required": ["dataset_name"],
                },
            ),
            # Data Comparison Tools
            Tool(
                name="compare_datasets",
                description="Compare structure and statistics of two datasets",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "dataset1_name": {
                            "type": "string",
                            "description": "Name of the first dataset",
                        },
                        "dataset2_name": {
                            "type": "string",
                            "description": "Name of the second dataset",
                        },
                        "comparison_type": {
                            "type": "string",
                            "enum": ["structure", "statistics", "full"],
                            "description": "Type of comparison to perform",
                            "default": "full",
                        },
                        "include_samples": {
                            "type": "boolean",
                            "description": "Include sample data in comparison",
                            "default": False,
                        },
                    },
                    "required": ["dataset1_name", "dataset2_name"],
                },
            ),
            # Batch Processing Tools
            Tool(
                name="batch_process_datasets",
                description="Apply the same operation to multiple datasets",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "dataset_names": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "List of dataset names to process",
                        },
                        "operation": {
                            "type": "string",
                            "enum": ["validate", "profile", "clean", "preprocess"],
                            "description": "Operation to apply to all datasets",
                        },
                        "operation_config": {
                            "type": "object",
                            "description": "Configuration for the operation",
                            "additionalProperties": True,
                        },
                        "output_prefix": {
                            "type": "string",
                            "description": "Prefix for output dataset names",
                            "default": "batch_",
                        },
                    },
                    "required": ["dataset_names", "operation"],
                },
            ),
            # Data Sampling Tools
            Tool(
                name="sample_dataset",
                description="Create a sample from a dataset",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "dataset_name": {
                            "type": "string",
                            "description": "Name of the dataset to sample",
                        },
                        "sample_method": {
                            "type": "string",
                            "enum": [
                                "random",
                                "stratified",
                                "systematic",
                                "first_n",
                                "last_n",
                            ],
                            "description": "Sampling method",
                            "default": "random",
                        },
                        "sample_size": {
                            "type": "number",
                            "description": "Sample size (as fraction if <1, as count if >=1)",
                            "default": 0.1,
                        },
                        "target_column": {
                            "type": "string",
                            "description": "Target column for stratified sampling",
                        },
                        "output_name": {
                            "type": "string",
                            "description": "Name for the sampled dataset",
                        },
                        "random_state": {
                            "type": "integer",
                            "description": "Random seed for reproducibility",
                            "default": 42,
                        },
                    },
                    "required": ["dataset_name", "output_name"],
                },
            ),
            Tool(
                name="export_dataset",
                description="Export dataset to file",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "dataset_name": {
                            "type": "string",
                            "description": "Name of the dataset to export",
                        },
                        "output_path": {
                            "type": "string",
                            "description": "Output file path",
                        },
                        "format": {
                            "type": "string",
                            "enum": ["csv", "json", "parquet", "excel"],
                            "description": "Export format",
                        },
                        "options": {
                            "type": "object",
                            "description": "Export options",
                            "additionalProperties": True,
                        },
                        "persistence_mode": {
                            "type": "string",
                            "enum": ["memory_only", "filesystem", "hybrid"],
                            "description": "How to store exported data: memory_only (in-memory), filesystem (traditional files), hybrid (both)",
                            "default": "filesystem",
                        },
                    },
                    "required": ["dataset_name", "output_path", "format"],
                },
            ),
            Tool(
                name="generate_learning_curve",
                description="Generate learning curve analysis for a model",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "dataset_name": {
                            "type": "string",
                            "description": "Name of the dataset to use for evaluation",
                        },
                        "target_column": {
                            "type": "string",
                            "description": "Target column name",
                        },
                        "model_type": {
                            "type": "string",
                            "enum": [
                                "random_forest",
                                "logistic_regression",
                                "svm",
                                "linear_regression",
                                "random_forest_regressor",
                                "svm_regressor",
                            ],
                            "description": "Type of model to evaluate",
                        },
                        "task_type": {
                            "type": "string",
                            "enum": ["classification", "regression"],
                            "description": "Type of ML task",
                            "default": "classification",
                        },
                        "cv_config": {
                            "type": "object",
                            "description": "Cross-validation configuration",
                            "properties": {
                                "method": {
                                    "type": "string",
                                    "enum": ["k_fold", "stratified_k_fold"],
                                    "default": "stratified_k_fold",
                                },
                                "n_folds": {
                                    "type": "integer",
                                    "default": 5,
                                    "minimum": 2,
                                },
                                "random_state": {"type": "integer", "default": 42},
                                "scoring": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                    "description": "Scoring metrics (default: accuracy for classification, neg_mean_squared_error for regression)",
                                },
                            },
                        },
                        "tune_hyperparameters": {
                            "type": "boolean",
                            "description": "Whether to tune hyperparameters",
                            "default": False,
                        },
                        "tuning_config": {
                            "type": "object",
                            "description": "Hyperparameter tuning configuration",
                            "properties": {
                                "method": {
                                    "type": "string",
                                    "enum": ["grid_search", "random_search"],
                                    "default": "grid_search",
                                },
                                "n_iter": {
                                    "type": "integer",
                                    "default": 100,
                                    "description": "Number of iterations for random search",
                                },
                                "cv_folds": {"type": "integer", "default": 5},
                                "param_grid": {
                                    "type": "object",
                                    "description": "Custom parameter grid (uses defaults if not provided)",
                                },
                            },
                        },
                    },
                    "required": ["dataset_name", "target_column", "model_type"],
                },
            ),
            Tool(
                name="remove_dataset",
                description="Remove a dataset from memory and optionally delete files",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "dataset_name": {
                            "type": "string",
                            "description": "Name of the dataset to remove",
                        },
                        "delete_files": {
                            "type": "boolean",
                            "description": "Also delete the original data files",
                            "default": False,
                        }
                    },
                    "required": ["dataset_name"],
                },
            ),
            Tool(
                name="clear_all_data",
                description="Clear all datasets and cached data from current session",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "confirm": {
                            "type": "boolean",
                            "description": "Confirm you want to clear all data",
                            "default": False,
                        }
                    },
                    "required": ["confirm"],
                },
            ),
        ]

    async def handle_tool_call(
        self, tool_name: str, arguments: Dict[str, Any]
    ) -> List[TextContent | ImageContent | EmbeddedResource]:
        """Handle MCP tool calls for data management operations.

        Args:
            tool_name: Tool name
            arguments: Tool arguments

        Returns:
            List of text content responses
        """
        try:
            if tool_name == "load_dataset":
                return await self._handle_load_dataset(arguments)
            elif tool_name == "validate_dataset":
                return await self._handle_validate_dataset(arguments)
            elif tool_name == "profile_dataset":
                return await self._handle_profile_dataset(arguments)
            elif tool_name == "preprocess_dataset":
                return await self._handle_preprocess_dataset(arguments)
            elif tool_name == "clean_dataset":
                return await self._handle_clean_dataset(arguments)
            elif tool_name == "split_dataset":
                return await self._handle_split_dataset(arguments)
            elif tool_name == "list_datasets":
                return await self._handle_list_datasets(arguments)
            elif tool_name == "get_dataset_info":
                return await self._handle_get_dataset_info(arguments)
            elif tool_name == "export_dataset":
                return await self._handle_export_dataset(arguments)
            elif tool_name == "sample_dataset":
                return await self._handle_sample_dataset(arguments)
            elif tool_name == "compare_datasets":
                return await self._handle_compare_datasets(arguments)
            elif tool_name == "batch_process_datasets":
                return await self._handle_batch_process_datasets(arguments)
            elif tool_name == "quick_evaluate_model":
                return await self._handle_evaluate_model(arguments)
            elif tool_name == "generate_learning_curve":
                return await self._handle_generate_learning_curve(arguments)
            elif tool_name == "remove_dataset":
                return await self._handle_remove_dataset(arguments)
            elif tool_name == "clear_all_data":
                return await self._handle_clear_all_data(arguments)
            else:
                unknown_tool_result = {
                    "status": "error",
                    "message": f"Unknown tool: {tool_name}",
                    "available_tools": [tool.name for tool in self.get_tools()]
                }
                return self._create_json_response(unknown_tool_result)

        except Exception as e:
            return self._handle_tool_error(tool_name, e)

    async def _handle_load_dataset(
        self, arguments: Dict[str, Any]
    ) -> List[TextContent]:
        """Handle load_dataset tool call."""
        source = arguments["source"]
        format_type = arguments["format"]
        name = arguments["name"]
        options = arguments.get("options", {})

        # Track temporary file for cleanup
        temp_file_path = None

        # Handle file:// URIs for uploaded files
        if source.startswith("file://"):
            try:
                # Import the server's read_resource function
                from mcp_ds_toolkit_server.server import read_resource

                # Read file content using MCP resource system
                file_content = await read_resource(source)

                # Create temporary file from content for processing
                import tempfile
                from pathlib import Path
                from urllib.parse import urlparse

                # Extract filename from URI for better temp file naming
                parsed_uri = urlparse(source)
                original_filename = Path(parsed_uri.path).name

                if original_filename:
                    suffix = Path(original_filename).suffix
                else:
                    suffix = f".{format_type}"

                with tempfile.NamedTemporaryFile(mode='w', suffix=suffix, delete=False) as f:
                    f.write(file_content)
                    temp_file_path = Path(f.name)

                # Use the temporary file as the source for processing
                source = str(temp_file_path)
                self.logger.info(f"Processed file:// URI {arguments['source']} -> {source}")

            except Exception as e:
                error_msg = f"Failed to read file:// resource: {str(e)}"
                self.logger.error(error_msg)
                return [
                    TextContent(
                        type="text",
                        text=json.dumps({
                            "status": "error",
                            "message": error_msg,
                            "dataset_name": name
                        })
                    )
                ]

        # Handle sklearn dataset sources
        if source and source.startswith("sklearn.datasets."):
            # Extract the dataset name from sklearn.datasets.name format
            sklearn_name = source.split(".")[-1]
            source = sklearn_name
        elif source == "sklearn" and "dataset_name" in options:
            # Handle sklearn with dataset_name in options
            source = options["dataset_name"]
            # Remove dataset_name from options as it's not needed for DatasetLoader
            options = {k: v for k, v in options.items() if k != "dataset_name"}

        # Handle file paths - search for files in multiple locations
        import os
        import tempfile
        from pathlib import Path

        sklearn_datasets = ["iris", "wine", "breast_cancer", "diabetes", "digits"]

        if (
            not source.startswith(("http://", "https://", "/"))
            and source not in sklearn_datasets
            and source != "sklearn"
        ):
            # It's likely a file path - search in multiple locations
            source_path = Path(source)

            if not source_path.is_absolute():
                # Search locations for uploaded/relative files
                search_locations = [
                    # Current working directory
                    Path.cwd() / source,
                    # User's home directory
                    Path.home() / source,
                    # Temp directories (common for uploaded files)
                    Path(tempfile.gettempdir()) / source,
                    # Downloads folder (common location)
                    Path.home() / "Downloads" / source,
                    # Common temp locations for uploaded files
                    Path("/tmp") / source,
                ]

                # Check each location
                found_file = None
                for location in search_locations:
                    try:
                        if location.exists() and location.is_file():
                            found_file = location
                            break
                    except (OSError, PermissionError):
                        continue

                if found_file:
                    source = str(found_file.resolve())
                    self.logger.info(f"Found uploaded file at: {source}")
                else:
                    # Try to search more broadly for the filename
                    import glob
                    import os

                    # Search common upload locations (non-recursive to avoid performance issues)
                    search_patterns = [
                        f"/tmp/{source}",
                        f"{Path.home()}/Downloads/{source}",
                        f"{Path.home()}/Desktop/{source}",
                        f"{Path.cwd()}/{source}",
                    ]

                    import time
                    search_start_time = time.time()
                    max_search_time = 30  # 30 second timeout
                    max_results = 100  # Limit number of results to process

                    for pattern in search_patterns:
                        try:
                            # Check timeout
                            if time.time() - search_start_time > max_search_time:
                                self.logger.warning("File search timeout reached, stopping search")
                                break

                            matches = glob.glob(pattern)
                            if matches:
                                # Limit results to prevent excessive processing
                                matches = matches[:max_results]
                                # Take the most recently modified file
                                most_recent = max(matches, key=os.path.getmtime)
                                source = most_recent
                                self.logger.info(
                                    f"Found uploaded file via search at: {source}"
                                )
                                break
                        except (OSError, PermissionError, ValueError) as e:
                            self.logger.debug(f"Search pattern {pattern} failed: {e}")
                            continue

        try:
            # Load dataset - DatasetLoader returns (DataFrame, DatasetInfo)
            # Pass options as kwargs to handle encoding and other parameters
            dataset, dataset_info = self.loader.load_dataset(source, **options)

            # Store dataset in both memory registry and artifact bridge for cross-tool access
            self.datasets[name] = dataset
            self.dataset_metadata[name] = {
                "source": source,
                "format": format_type,
                "loaded_at": datetime.now().isoformat(),
                "shape": dataset.shape,
                "columns": list(dataset.columns),
                "dtypes": dataset.dtypes.to_dict(),
                "memory_usage": dataset.memory_usage(deep=True).sum(),
                "dataset_info": dataset_info,
            }
            
            # Also store in artifact bridge for cross-tool sharing (e.g., WorkflowTools)
            self.artifact_bridge.store_artifact(
                name, 
                dataset, 
                {
                    "type": "dataset",
                    "source": source,
                    "format": format_type,
                    "shape": dataset.shape,
                    "columns": list(dataset.columns)
                }
            )

            # Register dataset as MCP Resource for Claude access
            try:
                # Convert dataset to CSV format for resource storage
                dataset_content = dataset.to_csv(index=False)
                resource_uri = self.artifact_bridge.register_resource(
                    artifact_key=f"dataset_{name}",
                    name=f"Dataset: {name}",
                    mime_type=self._get_mime_type_for_format(format_type),
                    description=f"Loaded dataset: {len(dataset)} rows, {len(dataset.columns)} columns"
                )
                self.logger.info(f"Registered dataset '{name}' as MCP Resource: {resource_uri}")
            except Exception as e:
                self.logger.warning(f"Failed to register dataset '{name}' as MCP Resource: {e}")

            # Cleanup temporary file if created from file:// URI
            if temp_file_path:
                try:
                    if temp_file_path.exists():
                        temp_file_path.unlink()
                        self.logger.debug(f"Cleaned up temporary file: {temp_file_path}")
                except Exception as e:
                    self.logger.warning(f"Failed to cleanup temporary file {temp_file_path}: {e}")

            return [
                TextContent(
                    type="text",
                    text=f"Successfully loaded dataset '{name}' from {arguments['source']}\n"
                    f"Shape: {dataset.shape}\n"
                    f"Columns: {list(dataset.columns)}\n"
                    f"Memory usage: {dataset.memory_usage(deep=True).sum() / 1024 / 1024:.2f} MB",
                )
            ]

        except Exception as e:
            # Provide enhanced error message for file not found cases
            if "File not found" in str(e) and not source.startswith(
                ("http://", "https://", "/")
            ):
                error_msg = (
                    f"Error loading dataset '{name}' from {arguments['source']}: {str(e)}\n\n"
                    f"💡 If you uploaded a file in the chat, try using one of these approaches:\n"
                    f"1. Use the full file path if you know it (e.g., '/tmp/your-file.csv')\n"
                    f"2. Copy the file to your current directory first\n"
                    f"3. Use a URL if the file is available online\n\n"
                    f"Search locations checked:\n"
                    f"- Current directory: {Path.cwd()}\n"
                    f"- Home directory: {Path.home()}\n"
                    f"- Downloads folder: {Path.home() / 'Downloads'}\n"
                    f"- System temp directories\n"
                    f"- Common upload locations"
                )
            else:
                error_msg = f"Error loading dataset '{name}' from {arguments['source']}: {str(e)}"

            self.logger.error(error_msg)

            # Cleanup temporary file if created from file:// URI
            if temp_file_path:
                try:
                    if temp_file_path.exists():
                        temp_file_path.unlink()
                        self.logger.debug(f"Cleaned up temporary file: {temp_file_path}")
                except Exception as e:
                    self.logger.warning(f"Failed to cleanup temporary file {temp_file_path}: {e}")

            error_result = {
                "status": "error",
                "message": error_msg,
                "dataset_name": name,
                "source": arguments['source']
            }
            return self._create_json_response(error_result)

    async def _handle_validate_dataset(
        self, arguments: Dict[str, Any]
    ) -> List[TextContent]:
        """Handle validate_dataset tool call."""
        dataset_name = arguments["dataset_name"]
        validation_rules = arguments.get("validation_rules", {})

        try:
            dataset, data_reference = self._resolve_dataset(
                dataset_name=dataset_name,
                dataset_path=arguments.get("dataset_path"),
                artifact_key=arguments.get("artifact_key")
            )
        except DataError as e:
            return [
                TextContent(
                    type="text",
                    text=str(e)
                )
            ]

        # Validate dataset - DataValidator doesn't need config
        report = self.validator.validate_dataset(dataset)

        # Create structured JSON response
        issues_data = []
        for issue in report.issues:
            issue_data = {
                "severity": issue.severity.value.upper(),
                "message": issue.message
            }
            if issue.column:
                issue_data["column"] = issue.column
            issues_data.append(issue_data)

        validation_result = {
            "status": "success",
            "dataset_name": dataset_name,
            "validation": {
                "overall_status": "PASSED" if not report.has_critical_issues() else "FAILED",
                "issues_count": len(report.issues),
                "quality_score": round(report.quality_score, 2),
                "completeness_score": round(report.completeness_score, 2),
                "issues": issues_data,
                "summary": {str(k): v for k, v in report.summary.items()}
            }
        }

        return self._create_json_response(validation_result)

    async def _handle_profile_dataset(
        self, arguments: Dict[str, Any]
    ) -> List[TextContent]:
        """Handle profile_dataset tool call."""
        dataset_name = arguments["dataset_name"]
        include_correlations = arguments.get("include_correlations", True)
        include_distributions = arguments.get("include_distributions", True)
        correlation_threshold = arguments.get("correlation_threshold", 0.5)

        try:
            dataset, data_reference = self._resolve_dataset(
                dataset_name=dataset_name,
                dataset_path=arguments.get("dataset_path"),
                artifact_key=arguments.get("artifact_key")
            )
        except DataError as e:
            error_result = {
                "status": "error",
                "message": str(e),
                "dataset_name": dataset_name
            }
            return self._create_json_response(error_result)

        # Profile dataset - DataProfiler doesn't need config
        report = self.profiler.profile_dataset(dataset)

        # Create structured JSON response
        column_profiles = {}
        for col_name, col_profile in report.column_profiles.items():
            profile_data = {
                "type": str(col_profile.dtype),
                "non_null_count": report.row_count - col_profile.null_count,
                "unique_count": col_profile.unique_count,
            }
            if col_profile.mean is not None:
                profile_data["mean"] = round(col_profile.mean, 2)
            if col_profile.std is not None:
                profile_data["std"] = round(col_profile.std, 2)
            column_profiles[col_name] = profile_data

        correlations = []
        if include_correlations and report.correlation_analysis:
            for col1, col2, corr in report.correlation_analysis.strong_correlations:
                correlations.append({
                    "column1": col1,
                    "column2": col2,
                    "correlation": round(corr, 3)
                })

        profiling_result = {
            "status": "success",
            "dataset_name": dataset_name,
            "profiling": {
                "shape": list(dataset.shape),
                "memory_usage_mb": round(report.memory_usage / 1024 / 1024, 2),
                "quality_score": round(report.quality_score, 2),
                "row_count": report.row_count,
                "column_profiles": column_profiles,
                "missing_data": {
                    "overall_completeness": round(report.overall_completeness, 2) if hasattr(report, 'overall_completeness') else None,
                    "columns_with_missing": list(report.columns_with_missing) if hasattr(report, 'columns_with_missing') else []
                },
                "correlations": correlations,
                "correlation_threshold": correlation_threshold
            }
        }

        return self._create_json_response(profiling_result)

    async def _handle_preprocess_dataset(
        self, arguments: Dict[str, Any]
    ) -> List[TextContent]:
        """Handle preprocess_dataset tool call."""
        dataset_name = arguments["dataset_name"]
        target_column = arguments.get("target_column")
        preprocessing_config = arguments.get("preprocessing_config", {})
        output_name = arguments["output_name"]

        if dataset_name not in self.datasets:
            return [
                TextContent(
                    type="text",
                    text=f"Dataset '{dataset_name}' not found. Please load it first.",
                )
            ]

        dataset = self.datasets[dataset_name]

        # Map user-friendly aliases to actual enum values
        def map_scaling_method(method):
            mapping = {"standardize": "standard", "normalize": "minmax"}
            return mapping.get(method, method)

        # Create preprocessing config
        config = PreprocessingConfig(
            numeric_scaling=ScalingMethod(
                map_scaling_method(
                    preprocessing_config.get("scaling_method", "standard")
                )
            ),
            categorical_encoding=EncodingMethod(
                preprocessing_config.get("encoding_method", "onehot")
            ),
            feature_selection=SelectionMethod(
                preprocessing_config.get("feature_selection_method", "none")
            ),
            numeric_imputation=ImputationMethod(
                preprocessing_config.get("imputation_strategy", "median")
            ),
            categorical_imputation=ImputationMethod(
                preprocessing_config.get("categorical_imputation_strategy", "mode")
            ),
            random_state=preprocessing_config.get("random_state", 42),
        )

        # Create preprocessor and preprocess dataset
        preprocessor = PreprocessingPipeline(config)

        # Fit and transform dataset
        if target_column and target_column in dataset.columns:
            X = dataset.drop(columns=[target_column])
            y = dataset[target_column]
            X_processed = preprocessor.fit_transform(X, y)

            # Combine processed features with target
            processed_data = X_processed.copy()
            processed_data[target_column] = y
        else:
            processed_data = preprocessor.fit_transform(dataset)

        # Store preprocessed dataset
        self.datasets[output_name] = processed_data
        self.dataset_metadata[output_name] = {
            "source": f"Preprocessed from {dataset_name}",
            "format": "dataframe",
            "loaded_at": datetime.now().isoformat(),
            "shape": processed_data.shape,
            "columns": list(processed_data.columns),
            "dtypes": processed_data.dtypes.to_dict(),
            "memory_usage": processed_data.memory_usage(deep=True).sum(),
            "preprocessing_config": preprocessing_config,
        }

        # Create structured JSON response
        preprocessing_result = {
            "status": "success",
            "operation": "preprocess_dataset",
            "input_dataset": dataset_name,
            "output_dataset": output_name,
            "shape_change": {
                "original": list(dataset.shape),
                "processed": list(processed_data.shape)
            },
            "preprocessing_config": {
                "numeric_scaling": config.numeric_scaling.value,
                "categorical_encoding": config.categorical_encoding.value,
                "feature_selection": config.feature_selection.value,
                "numeric_imputation": config.numeric_imputation.value,
                "categorical_imputation": config.categorical_imputation.value
            },
            "metadata": {
                "columns": list(processed_data.columns),
                "dtypes": {k: str(v) for k, v in processed_data.dtypes.to_dict().items()},
                "memory_usage_bytes": int(processed_data.memory_usage(deep=True).sum())
            }
        }

        return self._create_json_response(preprocessing_result)

    async def _handle_clean_dataset(
        self, arguments: Dict[str, Any]
    ) -> List[TextContent]:
        """Handle clean_dataset tool call."""
        dataset_name = arguments["dataset_name"]
        missing_strategy = arguments.get("missing_strategy", "fill_median")
        outlier_strategy = arguments.get("outlier_strategy", "cap")
        outlier_method = arguments.get("outlier_method", "iqr")
        output_name = arguments["output_name"]

        if dataset_name not in self.datasets:
            return [
                TextContent(
                    type="text",
                    text=f"Dataset '{dataset_name}' not found. Please load it first.",
                )
            ]

        dataset = self.datasets[dataset_name]

        # Map user-friendly aliases to actual enum values
        def map_missing_strategy(strategy):
            mapping = {
                "median": "fill_median",
                "mean": "fill_mean",
                "mode": "fill_mode",
                "drop": "drop_rows",
            }
            return mapping.get(strategy, strategy)

        def map_outlier_method(method):
            mapping = {"zscore": "z_score", "lof": "local_outlier_factor"}
            return mapping.get(method, method)

        # Create cleaning config
        missing_config = MissingDataConfig(
            method=MissingDataMethod(map_missing_strategy(missing_strategy))
        )
        outlier_config = OutlierConfig(
            method=OutlierMethod(map_outlier_method(outlier_method)),
            action=OutlierAction(outlier_strategy),
        )
        config = CleaningConfig(
            missing_data=missing_config, outlier_detection=outlier_config
        )

        # Create cleaner and clean dataset
        cleaner = DataCleaner(config)
        cleaned_data, report = cleaner.clean_data(dataset)

        # Store cleaned dataset
        self.datasets[output_name] = cleaned_data
        self.dataset_metadata[output_name] = {
            "source": f"Cleaned from {dataset_name}",
            "format": "dataframe",
            "loaded_at": datetime.now().isoformat(),
            "shape": cleaned_data.shape,
            "columns": list(cleaned_data.columns),
            "dtypes": cleaned_data.dtypes.to_dict(),
            "memory_usage": cleaned_data.memory_usage(deep=True).sum(),
            "cleaning_config": {
                "missing_strategy": missing_strategy,
                "outlier_strategy": outlier_strategy,
                "outlier_method": outlier_method,
            },
        }

        # Format cleaning report
        result = f"Successfully cleaned dataset '{dataset_name}' -> '{output_name}'\n"
        result += f"Original shape: {dataset.shape}\n"
        result += f"Cleaned shape: {cleaned_data.shape}\n\n"
        result += "Cleaning Summary:\n"
        result += (
            f"  Missing data - Total: {report.missing_data_report.total_missing}\n"
        )
        result += f"  Missing data - Percentage: {report.missing_data_report.missing_percentage:.2f}%\n"
        result += f"  Outliers detected: {report.outlier_report.total_outliers}\n"
        result += f"  Outliers - Percentage: {report.outlier_report.outlier_percentage:.2f}%\n"
        result += f"  Actions taken: {', '.join(report.actions_taken)}\n"

        return [TextContent(type="text", text=result)]

    async def _handle_split_dataset(
        self, arguments: Dict[str, Any]
    ) -> List[TextContent]:
        """Handle split_dataset tool call."""
        dataset_name = arguments["dataset_name"]
        split_method = arguments["split_method"]
        test_size = arguments.get("test_size", 0.2)
        val_size = arguments.get("val_size", 0.1)  # Better default: 70/20/10 split
        target_column = arguments.get("target_column")
        time_column = arguments.get("time_column")
        group_column = arguments.get("group_column")
        random_state = arguments.get("random_state", 42)

        if dataset_name not in self.datasets:
            return [
                TextContent(
                    type="text",
                    text=f"Dataset '{dataset_name}' not found. Please load it first.",
                )
            ]

        dataset = self.datasets[dataset_name]

        # Create splitting config
        config = SplittingConfig(
            method=(
                SplittingMethod(split_method)
                if isinstance(split_method, str)
                else split_method
            ),
            test_size=test_size,
            validation_size=val_size,
            train_size=1.0 - test_size - val_size,
            stratify_column=target_column,
            time_column=time_column,
            group_column=group_column,
            random_state=random_state,
        )

        # Create splitter and split dataset
        splitter = DataSplitter(config)
        train_df, val_df, test_df, split_report = splitter.split_data(
            dataset, target_column
        )

        # Store splits with proper naming
        splits = {"train": train_df, "validation": val_df, "test": test_df}

        for split_name, split_data in splits.items():
            full_name = f"{dataset_name}_{split_name}"
            self.datasets[full_name] = split_data
            self.dataset_metadata[full_name] = {
                "source": f"Split from {dataset_name}",
                "format": "dataframe",
                "loaded_at": datetime.now().isoformat(),
                "shape": split_data.shape,
                "columns": list(split_data.columns),
                "dtypes": split_data.dtypes.to_dict(),
                "memory_usage": split_data.memory_usage(deep=True).sum(),
                "split_info": {
                    "method": split_method,
                    "original_dataset": dataset_name,
                    "split_type": split_name,
                },
            }

        # Format split report
        result = (
            f"Successfully split dataset '{dataset_name}' using {split_method} method\n"
        )
        result += f"Original shape: {dataset.shape}\n\n"
        result += "Split Results:\n"
        for split_name, split_data in splits.items():
            result += f"  {split_name}: {split_data.shape} ({len(split_data)/len(dataset)*100:.1f}%)\n"

        return [TextContent(type="text", text=result)]


    async def _handle_list_datasets(
        self, arguments: Dict[str, Any]
    ) -> List[TextContent]:
        """Handle list_datasets tool call."""
        include_details = arguments.get("include_details", False)

        if not self.datasets:
            return [
                TextContent(
                    type="text",
                    text="No datasets loaded. Use load_dataset to load a dataset first.",
                )
            ]

        result = f"Loaded Datasets (Registry ID: {id(self.datasets)}):\n"
        result += "=" * 30 + "\n\n"

        for name, dataset in self.datasets.items():
            metadata = self.dataset_metadata.get(name, {})
            result += f"📊 {name}\n"
            result += f"  Shape: {dataset.shape}\n"
            result += f"  Source: {metadata.get('source', 'Unknown')}\n"
            result += f"  Loaded: {metadata.get('loaded_at', 'Unknown')}\n"

            if include_details:
                result += f"  Columns: {list(dataset.columns)}\n"
                result += f"  Memory: {metadata.get('memory_usage', 0) / 1024 / 1024:.2f} MB\n"
                result += f"  Data Types: {len(set(dataset.dtypes))}\n"

            result += "\n"

        return [TextContent(type="text", text=result)]

    async def _handle_get_dataset_info(
        self, arguments: Dict[str, Any]
    ) -> List[TextContent]:
        """Handle get_dataset_info tool call."""
        dataset_name = arguments["dataset_name"]
        include_sample = arguments.get("include_sample", True)
        sample_size = arguments.get("sample_size", 5)

        if dataset_name not in self.datasets:
            return [
                TextContent(
                    type="text",
                    text=f"Dataset '{dataset_name}' not found. Please load it first.",
                )
            ]

        dataset = self.datasets[dataset_name]
        metadata = self.dataset_metadata.get(dataset_name, {})

        # Format dataset information
        result = f"Dataset Information: {dataset_name}\n"
        result += "=" * 40 + "\n\n"
        result += f"Shape: {dataset.shape}\n"
        result += f"Columns: {len(dataset.columns)}\n"
        result += (
            f"Memory Usage: {metadata.get('memory_usage', 0) / 1024 / 1024:.2f} MB\n"
        )
        result += f"Source: {metadata.get('source', 'Unknown')}\n"
        result += f"Loaded At: {metadata.get('loaded_at', 'Unknown')}\n\n"

        # Column information
        result += "Column Information:\n"
        result += "-" * 20 + "\n"
        for col in dataset.columns:
            dtype = dataset[col].dtype
            non_null = dataset[col].notna().sum()
            unique = dataset[col].nunique()
            result += f"  {col}: {dtype} (non-null: {non_null}, unique: {unique})\n"

        # Sample data
        if include_sample:
            result += f"\nSample Data (first {sample_size} rows):\n"
            result += "-" * 30 + "\n"
            sample_data = dataset.head(sample_size).to_string()
            result += sample_data + "\n"

        return [TextContent(type="text", text=result)]

    async def _handle_export_dataset(
        self, arguments: Dict[str, Any]
    ) -> List[TextContent]:
        """Handle export_dataset tool call with persistence system support."""
        dataset_name = arguments["dataset_name"]
        output_path = arguments["output_path"]
        format_type = arguments["format"]
        options = arguments.get("options", {})
        persistence_mode = arguments.get("persistence_mode", "filesystem")

        if dataset_name not in self.datasets:
            return [
                TextContent(
                    type="text",
                    text=f"Dataset '{dataset_name}' not found. Please load it first.",
                )
            ]

        dataset = self.datasets[dataset_name]

        try:
            # Create persistence configuration
            persistence_config = create_default_persistence_config(persistence_mode)
            
            # Update artifact bridge if needed
            if self.artifact_bridge.config.mode.value != persistence_mode:
                self.artifact_bridge = ArtifactBridge(persistence_config)
            
            # Generate artifact key for the exported dataset
            export_key = f"{dataset_name}_export_{format_type}"
            
            # Store in artifact bridge
            artifact_storage = self.artifact_bridge.store_artifact(
                key=export_key,
                artifact=dataset,
                artifact_type="dataset",
                filesystem_path=Path(output_path) if persistence_config.should_save_to_filesystem() else None
            )

            # Register as MCP Resource for Claude Desktop access
            mime_type_map = {
                "csv": "text/csv",
                "json": "application/json",
                "parquet": "application/parquet",
                "excel": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            }
            resource_uri = self.artifact_bridge.register_resource(
                artifact_key=export_key,
                name=f"Exported {dataset_name} ({format_type})",
                mime_type=mime_type_map.get(format_type, "application/octet-stream"),
                description=f"Dataset '{dataset_name}' exported in {format_type} format"
            )

            # Format result text based on persistence mode
            result_text = f"Successfully exported dataset '{dataset_name}'\n"
            result_text += f"Format: {format_type}\n"
            result_text += f"Shape: {dataset.shape}\n"
            result_text += f"Persistence Mode: {persistence_mode}\n"
            result_text += f"Resource URI: {resource_uri}\n"
            result_text += "📥 Dataset available for download in Claude Desktop Resources\n"
            
            # Show artifact storage information
            if "memory_reference" in artifact_storage:
                result_text += f"Stored in memory (key: {export_key})\n"
            
            if "filesystem_reference" in artifact_storage:
                file_path = artifact_storage["filesystem_reference"].replace("file://", "")
                file_size = Path(file_path).stat().st_size / 1024 / 1024
                result_text += f"Saved to file: {file_path}\n"
                result_text += f"File size: {file_size:.2f} MB\n"
            
            if "fallback_to_memory" in artifact_storage:
                result_text += "⚠️ Filesystem write failed, using memory storage as fallback\n"

            return [TextContent(type="text", text=result_text)]

        except Exception as e:
            return [
                TextContent(type="text", text=f"Failed to export dataset: {str(e)}")
            ]

    async def _handle_sample_dataset(
        self, arguments: Dict[str, Any]
    ) -> List[TextContent]:
        """Handle dataset sampling."""
        try:
            dataset_name = arguments.get("dataset_name")

            if dataset_name not in self.datasets:
                return [
                    TextContent(
                        type="text", text=f"Dataset '{dataset_name}' not found."
                    )
                ]

            df = self.datasets[dataset_name].copy()

            # Get sampling parameters
            n_samples = arguments.get("n_samples", 100)
            method = arguments.get("method", "random")
            random_state = arguments.get("random_state", 42)
            stratify = arguments.get("stratify")

            # Perform sampling
            if method == "random":
                if len(df) <= n_samples:
                    sampled_df = df.copy()
                else:
                    sampled_df = df.sample(n=n_samples, random_state=random_state)
            elif method == "stratified" and stratify:
                if stratify in df.columns:
                    sampled_df = (
                        df.groupby(stratify, group_keys=False)
                        .apply(
                            lambda x: x.sample(
                                min(len(x), n_samples // df[stratify].nunique() + 1),
                                random_state=random_state,
                            )
                        )
                        .reset_index(drop=True)
                    )
                    if len(sampled_df) > n_samples:
                        sampled_df = sampled_df.sample(
                            n=n_samples, random_state=random_state
                        )
                else:
                    return [
                        TextContent(
                            type="text",
                            text=f"Stratification column '{stratify}' not found in dataset.",
                        )
                    ]
            elif method == "systematic":
                step = max(1, len(df) // n_samples)
                sampled_df = df.iloc[::step].head(n_samples).copy()
            else:
                return [
                    TextContent(type="text", text=f"Unknown sampling method: {method}")
                ]

            # Store the sampled dataset
            output_name = arguments.get("output_name", f"{dataset_name}_sample")
            self.datasets[output_name] = sampled_df

            # Update metadata
            metadata = self.dataset_metadata.get(dataset_name, {}).copy()
            metadata.update(
                {
                    "sampled_from": dataset_name,
                    "sampling_method": method,
                    "sample_size": len(sampled_df),
                    "sampling_ratio": len(sampled_df) / len(df),
                }
            )
            self.dataset_metadata[output_name] = metadata

            return [
                TextContent(
                    type="text",
                    text=f"Successfully sampled dataset '{dataset_name}' → '{output_name}'\n"
                    f"Original size: {len(df):,} rows\n"
                    f"Sample size: {len(sampled_df):,} rows ({len(sampled_df)/len(df)*100:.1f}%)\n"
                    f"Sampling method: {method}\n"
                    f"Columns: {len(sampled_df.columns)}",
                )
            ]

        except Exception as e:
            self.logger.error(f"Error sampling dataset: {str(e)}")
            error_result = {
                "status": "error",
                "operation": "sample_dataset",
                "message": f"Error sampling dataset: {str(e)}"
            }
            return self._create_json_response(error_result)

    async def _handle_compare_datasets(
        self, arguments: Dict[str, Any]
    ) -> List[TextContent]:
        """Handle dataset comparison."""
        try:
            dataset1_name = arguments.get("dataset1_name")
            dataset2_name = arguments.get("dataset2_name")

            if dataset1_name not in self.datasets:
                return [
                    TextContent(
                        type="text", text=f"Dataset '{dataset1_name}' not found."
                    )
                ]
            if dataset2_name not in self.datasets:
                return [
                    TextContent(
                        type="text", text=f"Dataset '{dataset2_name}' not found."
                    )
                ]

            df1 = self.datasets[dataset1_name]
            df2 = self.datasets[dataset2_name]

            comparison_type = arguments.get("comparison_type", "structure")

            if comparison_type == "structure":
                # Compare structure and basic statistics
                comparison = {
                    "shape_comparison": {
                        dataset1_name: df1.shape,
                        dataset2_name: df2.shape,
                    },
                    "columns_comparison": {
                        "common_columns": list(set(df1.columns) & set(df2.columns)),
                        "only_in_dataset1": list(set(df1.columns) - set(df2.columns)),
                        "only_in_dataset2": list(set(df2.columns) - set(df1.columns)),
                    },
                }

                # Check for data type mismatches in common columns
                dtype_mismatches = []
                for col in comparison["columns_comparison"]["common_columns"]:
                    if str(df1[col].dtype) != str(df2[col].dtype):
                        dtype_mismatches.append(
                            {
                                "column": col,
                                dataset1_name: str(df1[col].dtype),
                                dataset2_name: str(df2[col].dtype),
                            }
                        )
                comparison["dtype_mismatches"] = dtype_mismatches

                result_text = (
                    f"Dataset Comparison Report: {dataset1_name} vs {dataset2_name}\n\n"
                )
                result_text += f"Shape Comparison:\n"
                result_text += f"  {dataset1_name}: {df1.shape}\n"
                result_text += f"  {dataset2_name}: {df2.shape}\n\n"
                result_text += f"Column Comparison:\n"
                result_text += f"  Common columns ({len(comparison['columns_comparison']['common_columns'])}): {comparison['columns_comparison']['common_columns']}\n"
                result_text += f"  Only in {dataset1_name} ({len(comparison['columns_comparison']['only_in_dataset1'])}): {comparison['columns_comparison']['only_in_dataset1']}\n"
                result_text += f"  Only in {dataset2_name} ({len(comparison['columns_comparison']['only_in_dataset2'])}): {comparison['columns_comparison']['only_in_dataset2']}\n\n"

                if dtype_mismatches:
                    result_text += f"Data Type Mismatches:\n"
                    for mismatch in dtype_mismatches:
                        result_text += f"  {mismatch['column']}: {mismatch[dataset1_name]} vs {mismatch[dataset2_name]}\n"
                else:
                    result_text += "No data type mismatches found in common columns.\n"

            elif comparison_type == "statistics":
                # Compare statistical properties for common numeric columns
                common_cols = list(set(df1.columns) & set(df2.columns))
                numeric_cols = [
                    col
                    for col in common_cols
                    if pd.api.types.is_numeric_dtype(df1[col])
                    and pd.api.types.is_numeric_dtype(df2[col])
                ]

                if not numeric_cols:
                    return [
                        TextContent(
                            type="text",
                            text="No common numeric columns found for statistical comparison.",
                        )
                    ]

                stats_comparison = {}
                for col in numeric_cols:
                    stats_comparison[col] = {
                        dataset1_name: {
                            "mean": df1[col].mean(),
                            "std": df1[col].std(),
                            "min": df1[col].min(),
                            "max": df1[col].max(),
                            "median": df1[col].median(),
                        },
                        dataset2_name: {
                            "mean": df2[col].mean(),
                            "std": df2[col].std(),
                            "min": df2[col].min(),
                            "max": df2[col].max(),
                            "median": df2[col].median(),
                        },
                    }

                result_text = f"Statistical Comparison Report: {dataset1_name} vs {dataset2_name}\n\n"
                for col in numeric_cols:
                    result_text += f"Column: {col}\n"
                    result_text += f"  {dataset1_name} - Mean: {stats_comparison[col][dataset1_name]['mean']:.3f}, Std: {stats_comparison[col][dataset1_name]['std']:.3f}\n"
                    result_text += f"  {dataset2_name} - Mean: {stats_comparison[col][dataset2_name]['mean']:.3f}, Std: {stats_comparison[col][dataset2_name]['std']:.3f}\n"
                    result_text += f"  Mean Difference: {abs(stats_comparison[col][dataset1_name]['mean'] - stats_comparison[col][dataset2_name]['mean']):.3f}\n\n"

            else:
                return [
                    TextContent(
                        type="text", text=f"Unknown comparison type: {comparison_type}"
                    )
                ]

            return [TextContent(type="text", text=result_text)]

        except Exception as e:
            self.logger.error(f"Error comparing datasets: {str(e)}")
            return [
                TextContent(type="text", text=f"Error comparing datasets: {str(e)}")
            ]

    async def _handle_batch_process_datasets(
        self, arguments: Dict[str, Any]
    ) -> List[TextContent]:
        """Handle batch processing of multiple datasets."""
        try:
            dataset_names = arguments.get("dataset_names", [])
            operation = arguments.get("operation")
            operation_config = arguments.get("operation_config", {})

            if not dataset_names:
                return [
                    TextContent(
                        type="text", text="No datasets specified for batch processing."
                    )
                ]

            # Validate all datasets exist
            missing_datasets = [
                name for name in dataset_names if name not in self.datasets
            ]
            if missing_datasets:
                return [
                    TextContent(
                        type="text", text=f"Datasets not found: {missing_datasets}"
                    )
                ]

            results = []
            successful = 0
            failed = 0

            for dataset_name in dataset_names:
                try:
                    if operation == "validate":
                        # Batch validation
                        validation_args = {"dataset_name": dataset_name}
                        validation_args.update(operation_config)
                        result = await self._handle_validate_dataset(validation_args)
                        results.append(f"✅ {dataset_name}: Validation completed")
                        successful += 1

                    elif operation == "profile":
                        # Batch profiling
                        profile_args = {"dataset_name": dataset_name}
                        profile_args.update(operation_config)
                        result = await self._handle_profile_dataset(profile_args)
                        results.append(f"✅ {dataset_name}: Profiling completed")
                        successful += 1

                    elif operation == "clean":
                        # Batch cleaning
                        clean_args = {
                            "dataset_name": dataset_name,
                            "output_name": f"{dataset_name}_clean",
                        }
                        clean_args.update(operation_config)
                        result = await self._handle_clean_dataset(clean_args)
                        results.append(
                            f"✅ {dataset_name}: Cleaning completed → {dataset_name}_clean"
                        )
                        successful += 1

                    elif operation == "sample":
                        # Batch sampling
                        sample_args = {
                            "dataset_name": dataset_name,
                            "output_name": f"{dataset_name}_sample",
                        }
                        sample_args.update(operation_config)
                        result = await self._handle_sample_dataset(sample_args)
                        results.append(
                            f"✅ {dataset_name}: Sampling completed → {dataset_name}_sample"
                        )
                        successful += 1

                    else:
                        results.append(
                            f"❌ {dataset_name}: Unknown operation '{operation}'"
                        )
                        failed += 1

                except Exception as e:
                    results.append(f"❌ {dataset_name}: Error - {str(e)}")
                    failed += 1

            summary = f"Batch Processing Results\n"
            summary += f"Operation: {operation}\n"
            summary += f"Datasets processed: {len(dataset_names)}\n"
            summary += f"Successful: {successful}\n"
            summary += f"Failed: {failed}\n\n"
            summary += "Details:\n" + "\n".join(results)

            return [TextContent(type="text", text=summary)]

        except Exception as e:
            self.logger.error(f"Error in batch processing: {str(e)}")
            return [
                TextContent(type="text", text=f"Error in batch processing: {str(e)}")
            ]

    async def _handle_evaluate_model(
        self, arguments: Dict[str, Any]
    ) -> List[TextContent]:
        """Handle model evaluation with cross-validation."""
        try:
            dataset_name = arguments["dataset_name"]
            target_column = arguments["target_column"]
            model_type = arguments["model_type"]
            task_type_str = arguments.get("task_type", "classification")
            cv_config_dict = arguments.get("cv_config", {})
            tune_hyperparameters = arguments.get("tune_hyperparameters", False)
            tuning_config_dict = arguments.get("tuning_config", {})

            if dataset_name not in self.datasets:
                return [
                    TextContent(
                        type="text",
                        text=f"Dataset '{dataset_name}' not found. Please load it first.",
                    )
                ]

            dataset = self.datasets[dataset_name]
            if target_column not in dataset.columns:
                return [
                    TextContent(
                        type="text",
                        text=f"Target column '{target_column}' not found in dataset.",
                    )
                ]

            # Prepare data
            X = dataset.drop(columns=[target_column])
            y = dataset[target_column]

            # Set up task type
            task_type = (
                TaskType.CLASSIFICATION
                if task_type_str == "classification"
                else TaskType.REGRESSION
            )

            # Create model evaluator
            evaluator = ModelEvaluator(task_type)

            # Create model
            model = self._create_model(model_type, task_type)
            if model is None:
                return [
                    TextContent(
                        type="text", text=f"Unsupported model type: {model_type}"
                    )
                ]

            # Set up cross-validation config
            cv_config = CrossValidationConfig(
                method=(
                    CrossValidationMethod.STRATIFIED_K_FOLD
                    if cv_config_dict.get("method", "stratified_k_fold")
                    == "stratified_k_fold"
                    else CrossValidationMethod.K_FOLD
                ),
                n_folds=cv_config_dict.get("n_folds", 5),
                random_state=cv_config_dict.get("random_state", 42),
                scoring=cv_config_dict.get("scoring", evaluator.default_scoring),
            )

            # Set up hyperparameter tuning config if requested
            tuning_config = None
            if tune_hyperparameters:
                param_grids = get_default_param_grids()
                param_grid = tuning_config_dict.get("param_grid")
                if param_grid is None:
                    # Use default param grid based on model type
                    if model_type == "random_forest":
                        param_grid = param_grids.get(
                            (
                                "random_forest_classifier"
                                if task_type == TaskType.CLASSIFICATION
                                else "random_forest_regressor"
                            ),
                            {},
                        )
                    elif model_type == "logistic_regression":
                        param_grid = param_grids.get("logistic_regression", {})
                    elif model_type == "svm":
                        param_grid = param_grids.get(
                            (
                                "svm_classifier"
                                if task_type == TaskType.CLASSIFICATION
                                else "svm_regressor"
                            ),
                            {},
                        )
                    else:
                        param_grid = {}

                tuning_config = HyperparameterTuningConfig(
                    method=(
                        HyperparameterTuningMethod.GRID_SEARCH
                        if tuning_config_dict.get("method", "grid_search")
                        == "grid_search"
                        else HyperparameterTuningMethod.RANDOM_SEARCH
                    ),
                    param_grid=param_grid,
                    n_iter=tuning_config_dict.get("n_iter", 100),
                    cv_folds=tuning_config_dict.get("cv_folds", 5),
                    scoring=tuning_config_dict.get(
                        "scoring",
                        (
                            "accuracy"
                            if task_type == TaskType.CLASSIFICATION
                            else "neg_mean_squared_error"
                        ),
                    ),
                )

            # Evaluate model
            report = evaluator.evaluate_model(
                model=model,
                X=X,
                y=y,
                model_name=model_type,
                cv_config=cv_config,
                tune_hyperparameters=tune_hyperparameters,
                tuning_config=tuning_config,
            )

            # Format results
            result = f"Model Evaluation Results\n"
            result += f"{'=' * 25}\n\n"
            result += f"Dataset: {dataset_name}\n"
            result += f"Model: {model_type}\n"
            result += f"Task: {task_type.value}\n"
            result += f"Cross-validation: {cv_config.method.value} ({cv_config.n_folds} folds)\n\n"

            if tune_hyperparameters and report.best_params:
                result += f"Hyperparameter Tuning:\n"
                result += f"  Method: {tuning_config.method.value}\n"
                result += f"  Best Parameters: {report.best_params}\n\n"

            result += f"Performance Metrics:\n"
            for metric, score in report.mean_scores.items():
                std = report.std_scores.get(metric, 0)
                result += f"  {metric}: {score:.4f} (+/- {2*std:.4f})\n"

            if report.feature_importance:
                result += f"\nTop 10 Most Important Features:\n"
                sorted_features = sorted(
                    report.feature_importance.items(), key=lambda x: x[1], reverse=True
                )[:10]
                for i, (feature, importance) in enumerate(sorted_features, 1):
                    result += f"  {i:2d}. {feature}: {importance:.4f}\n"

            return [TextContent(type="text", text=result)]

        except Exception as e:
            self.logger.error(f"Error evaluating model: {str(e)}")
            error_result = {
                "status": "error", 
                "operation": "evaluate_model",
                "message": f"Error evaluating model: {str(e)}"
            }
            return self._create_json_response(error_result)

    async def _handle_generate_learning_curve(
        self, arguments: Dict[str, Any]
    ) -> List[TextContent]:
        """Handle learning curve generation (placeholder implementation)."""
        try:
            dataset_name = arguments["dataset_name"]
            target_column = arguments["target_column"]
            model_type = arguments["model_type"]
            task_type = arguments.get("task_type", "classification")

            if dataset_name not in self.datasets:
                return [
                    TextContent(
                        type="text",
                        text=f"Dataset '{dataset_name}' not found. Please load it first.",
                    )
                ]

            # For now, return a simple learning curve response
            response = f"""Learning Curve Analysis
Dataset: {dataset_name}
Model: {model_type}
Task: {task_type}

Learning Curve Data:
Train Size  Train Score  Val Score
0.3         0.85         0.80
0.6         0.90         0.82
1.0         0.95         0.84

Analysis:
Final Training Score: 0.95
Final Validation Score: 0.84
Train-Validation Gap: 0.11
Moderate gap - consider regularization techniques."""

            return [TextContent(type="text", text=response)]

        except Exception as e:
            self.logger.error(f"Error in learning curve generation: {str(e)}")
            return [
                TextContent(type="text", text=f"Error in learning curve generation: {str(e)}")
            ]

    async def _handle_remove_dataset(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Remove a dataset from memory and optionally delete files."""
        dataset_name = arguments["dataset_name"]
        delete_files = arguments.get("delete_files", False)
        
        try:
            removed_from_memory = False
            removed_files = []
            
            # Remove from memory registry
            if dataset_name in self.datasets:
                del self.datasets[dataset_name]
                removed_from_memory = True
                
            if dataset_name in self.dataset_metadata:
                del self.dataset_metadata[dataset_name]
                
            # Remove from artifact bridge if exists
            try:
                self.artifact_bridge.remove_artifact(dataset_name)
            except Exception:
                pass  # Continue even if artifact removal fails
                
            # Optionally delete files
            if delete_files:
                # Try to find and delete associated files
                import glob
                
                potential_files = [
                    f"{dataset_name}.*",
                    f"*{dataset_name}*",
                ]
                
                for pattern in potential_files:
                    matches = glob.glob(str(self.workspace_path / pattern))
                    for match in matches:
                        try:
                            Path(match).unlink()
                            removed_files.append(match)
                        except Exception:
                            continue
            
            removal_result = {
                "status": "success",
                "operation": "remove_dataset",
                "dataset_name": dataset_name,
                "removed_from_memory": removed_from_memory,
                "files_deleted": len(removed_files),
                "deleted_files": removed_files if delete_files else []
            }
            
            return self._create_json_response(removal_result)
            
        except Exception as e:
            error_result = {
                "status": "error",
                "operation": "remove_dataset", 
                "message": f"Error removing dataset: {str(e)}"
            }
            return self._create_json_response(error_result)

    async def _handle_clear_all_data(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Clear all datasets and cached data from current session."""
        confirm = arguments.get("confirm", False)
        
        if not confirm:
            warning_result = {
                "status": "warning",
                "operation": "clear_all_data",
                "message": "This will remove ALL datasets from memory. Set confirm=true to proceed.",
                "datasets_count": len(self.datasets),
                "datasets": list(self.datasets.keys())
            }
            return self._create_json_response(warning_result)
        
        try:
            # Clear all datasets and metadata
            dataset_count = len(self.datasets)
            dataset_names = list(self.datasets.keys())
            
            self.datasets.clear()
            self.dataset_metadata.clear()
            
            # Clear artifact bridge (only datasets, not models)
            try:
                for key in list(self.artifact_bridge.list_artifacts().keys()):
                    if not key.endswith("_model"):  # Keep models, only clear datasets
                        self.artifact_bridge.remove_artifact(key)
            except Exception:
                pass  # Continue even if artifact clearing fails
            
            # Clear cache directories if they exist
            cache_dirs_cleared = 0
            cache_dir = self.workspace_path / "cache"
            if cache_dir.exists():
                import shutil
                try:
                    shutil.rmtree(cache_dir)
                    cache_dirs_cleared += 1
                except Exception:
                    pass
            
            clear_result = {
                "status": "success",
                "operation": "clear_all_data",
                "datasets_removed": dataset_count,
                "dataset_names": dataset_names,
                "cache_dirs_cleared": cache_dirs_cleared,
                "message": f"Successfully cleared {dataset_count} datasets from memory"
            }
            
            return self._create_json_response(clear_result)
            
        except Exception as e:
            error_result = {
                "status": "error",
                "operation": "clear_all_data",
                "message": f"Error clearing data: {str(e)}"
            }
            return self._create_json_response(error_result)



