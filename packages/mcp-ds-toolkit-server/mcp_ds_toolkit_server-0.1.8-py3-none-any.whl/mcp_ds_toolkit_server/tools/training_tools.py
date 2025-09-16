"""Model Training Tools Module

This module provides MCP tools for comprehensive model training operations
including model training, hyperparameter tuning, and evaluation.
"""

import json
import logging
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

from mcp_ds_toolkit_server.tools.base import BaseMCPTools
from mcp_ds_toolkit_server.data import DatasetLoader
from mcp_ds_toolkit_server.exceptions import DataError, TrainingError, ValidationError
from mcp_ds_toolkit_server.training import (
    EvaluationConfig,
    ModelEvaluator,
    ModelTrainer,
    TrainingConfig,
)
from mcp_ds_toolkit_server.utils.config import Settings
from mcp_ds_toolkit_server.utils.persistence import (
    ArtifactBridge,
    PersistenceConfig,
    create_default_persistence_config,
)
from mcp_ds_toolkit_server.tracking import get_tracker
from mcp_ds_toolkit_server.utils.data_resolver import UnifiedDataResolver
from mcp_ds_toolkit_server.utils.model_resolver import UnifiedModelResolver


class TrainingTools(BaseMCPTools):
    """MCP tools for model training operations."""

    def __init__(self, workspace_path: Path, datasets=None, dataset_metadata=None, artifact_bridge=None):
        """Initialize training tools.

        Args:
            workspace_path: Path to the workspace directory.
            datasets: Shared in-memory datasets registry.
            dataset_metadata: Shared dataset metadata registry.
            artifact_bridge: Artifact bridge for persistence operations.
        """
        # Use base class initialization to eliminate redundancy
        super().__init__(
            workspace_path=workspace_path,
            persistence_mode="memory_only", 
            artifact_bridge=artifact_bridge
        )
        
        # Tool-specific initialization
        self.datasets = datasets if datasets is not None else {}
        self.dataset_metadata = dataset_metadata if dataset_metadata is not None else {}
            
        self.logger.info(f"TrainingTools initialized - Registry ID: {id(self.datasets)}, Keys: {list(self.datasets.keys())}")
        
        # Initialize unified data resolver
        self.data_resolver = UnifiedDataResolver(
            memory_registry=self.datasets,
            artifact_bridge=self.artifact_bridge,
            data_loader=DatasetLoader(str(self.settings.data_dir))
        )
        
        # Initialize unified model resolver
        self.model_resolver = UnifiedModelResolver(
            artifact_bridge=self.artifact_bridge
        )

        # Initialize components with artifact bridge
        self.trainer = ModelTrainer(self.settings, self.artifact_bridge)
        self.evaluator = ModelEvaluator(self.settings)
        self.data_loader = DatasetLoader(str(self.settings.data_dir))
        
        # Local tracking is initialized globally via get_tracker()

    def get_tools(self) -> List[Tool]:
        """Get list of available training tools.

        Returns:
            List of MCP tools for training operations.
        """
        return [
            Tool(
                name="train_model",
                description="Train a machine learning model with configurable persistence (memory-only, filesystem, or hybrid storage)",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "dataset_name": {
                            "type": "string",
                            "description": "Name of the loaded dataset (use list_datasets to see available datasets)",
                        },
                        "dataset_path": {
                            "type": "string",
                            "description": "Path to the dataset file (CSV, JSON, Parquet) - alternative to dataset_name",
                        },
                        "target_column": {
                            "type": "string",
                            "description": "Name of the target/label column",
                        },
                        "algorithm": {
                            "type": "string",
                            "enum": [
                                "random_forest",
                                "gradient_boosting",
                                "extra_trees",
                                "logistic_regression",
                                "linear_regression",
                                "ridge",
                                "lasso",
                                "elastic_net",
                                "svm",
                                "knn",
                                "gaussian_nb",
                                "multinomial_nb",
                                "bernoulli_nb",
                                "decision_tree",
                            ],
                            "description": "Machine learning algorithm to use",
                            "default": "random_forest",
                        },
                        "model_type": {
                            "type": "string",
                            "enum": ["auto", "classification", "regression"],
                            "description": "Type of machine learning problem",
                            "default": "auto",
                        },
                        "test_size": {
                            "type": "number",
                            "minimum": 0.1,
                            "maximum": 0.5,
                            "description": "Proportion of data to use for testing",
                            "default": 0.2,
                        },
                        "enable_tuning": {
                            "type": "boolean",
                            "description": "Enable hyperparameter tuning",
                            "default": False,
                        },
                        "cv_folds": {
                            "type": "integer",
                            "minimum": 2,
                            "maximum": 10,
                            "description": "Number of cross-validation folds",
                            "default": 5,
                        },
                        "random_state": {
                            "type": "integer",
                            "description": "Random state for reproducibility",
                            "default": 42,
                        },
                        "feature_columns": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Specific feature columns to use (optional)",
                        },
                        "output_name": {
                            "type": "string",
                            "description": "Name for the trained model (optional)",
                        },
                        "persistence_mode": {
                            "type": "string",
                            "enum": ["memory_only", "filesystem", "hybrid"],
                            "description": "How to store artifacts: memory_only (in-memory, MCP-friendly), filesystem (traditional files), hybrid (both)",
                            "default": "memory_only",
                        },
                    },
                    "required": ["target_column"],
                },
            ),
            Tool(
                name="evaluate_model",
                description="Evaluate a trained model or compare multiple models with comprehensive metrics",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "model_path": {
                            "type": "string",
                            "description": "Path to the trained model file (.pkl)",
                        },
                        "dataset_name": {
                            "type": "string",
                            "description": "Name of the loaded dataset for evaluation",
                        },
                        "dataset_path": {
                            "type": "string",
                            "description": "Path to the evaluation dataset file - alternative to dataset_name",
                        },
                        "target_column": {
                            "type": "string",
                            "description": "Name of the target/label column",
                        },
                        "cv_folds": {
                            "type": "integer",
                            "minimum": 2,
                            "maximum": 10,
                            "description": "Number of cross-validation folds",
                            "default": 5,
                        },
                        "metrics": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Specific metrics to calculate (optional)",
                        },
                        "generate_learning_curves": {
                            "type": "boolean",
                            "description": "Generate learning curves",
                            "default": False,
                        },
                        "detailed_metrics": {
                            "type": "boolean",
                            "description": "Calculate detailed metrics and reports",
                            "default": True,
                        },
                    },
                    "required": ["model_path", "target_column"],
                },
            ),
            Tool(
                name="compare_models",
                description="Compare multiple trained models on the same dataset with statistical significance testing",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "model_paths": {
                            "type": "object",
                            "description": "Dictionary mapping model names to file paths",
                            "additionalProperties": {"type": "string"},
                        },
                        "dataset_name": {
                            "type": "string",
                            "description": "Name of the loaded dataset for model comparison",
                        },
                        "dataset_path": {
                            "type": "string",
                            "description": "Path to the evaluation dataset file - alternative to dataset_name",
                        },
                        "target_column": {
                            "type": "string",
                            "description": "Name of the target/label column",
                        },
                        "cv_folds": {
                            "type": "integer",
                            "minimum": 2,
                            "maximum": 10,
                            "description": "Number of cross-validation folds",
                            "default": 5,
                        },
                        "enable_statistical_tests": {
                            "type": "boolean",
                            "description": "Perform statistical significance tests",
                            "default": True,
                        },
                        "significance_level": {
                            "type": "number",
                            "minimum": 0.01,
                            "maximum": 0.1,
                            "description": "Significance level for statistical tests",
                            "default": 0.05,
                        },
                    },
                    "required": ["model_paths", "target_column"],
                },
            ),
            Tool(
                name="tune_hyperparameters",
                description="Perform comprehensive hyperparameter tuning for a model with various search strategies",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "dataset_name": {
                            "type": "string",
                            "description": "Name of the loaded dataset for hyperparameter tuning",
                        },
                        "dataset_path": {
                            "type": "string",
                            "description": "Path to the dataset file - alternative to dataset_name",
                        },
                        "target_column": {
                            "type": "string",
                            "description": "Name of the target/label column",
                        },
                        "algorithm": {
                            "type": "string",
                            "enum": [
                                "random_forest",
                                "gradient_boosting",
                                "extra_trees",
                                "logistic_regression",
                                "linear_regression",
                                "ridge",
                                "lasso",
                                "elastic_net",
                                "svm",
                                "knn",
                                "gaussian_nb",
                                "multinomial_nb",
                                "bernoulli_nb",
                                "decision_tree",
                            ],
                            "description": "Machine learning algorithm to tune",
                        },
                        "tuning_method": {
                            "type": "string",
                            "enum": ["grid_search", "random_search"],
                            "description": "Hyperparameter search method",
                            "default": "grid_search",
                        },
                        "cv_folds": {
                            "type": "integer",
                            "minimum": 2,
                            "maximum": 10,
                            "description": "Number of cross-validation folds for tuning",
                            "default": 3,
                        },
                        "scoring": {
                            "type": "string",
                            "description": "Scoring metric for optimization (optional)",
                        },
                        "test_size": {
                            "type": "number",
                            "minimum": 0.1,
                            "maximum": 0.5,
                            "description": "Proportion of data to hold out for final evaluation",
                            "default": 0.2,
                        },
                        "custom_param_grid": {
                            "type": "object",
                            "description": "Custom parameter grid (optional)",
                            "additionalProperties": {"type": "array"},
                        },
                    },
                    "required": ["target_column", "algorithm"],
                },
            ),
            Tool(
                name="get_model_info",
                description="Get detailed information about a trained model including metadata and performance",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "model_path": {
                            "type": "string",
                            "description": "Path to the trained model file",
                        },
                        "include_feature_importance": {
                            "type": "boolean",
                            "description": "Include feature importance analysis",
                            "default": True,
                        },
                    },
                    "required": ["model_path"],
                },
            ),
            Tool(
                name="list_algorithms",
                description="List all available machine learning algorithms with descriptions",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "model_type": {
                            "type": "string",
                            "enum": ["all", "classification", "regression"],
                            "description": "Filter algorithms by model type",
                            "default": "all",
                        }
                    },
                },
            ),
        ]

    async def handle_tool_call(
        self, tool_name: str, arguments: Dict[str, Any]
    ) -> List[TextContent | ImageContent | EmbeddedResource]:
        """Handle MCP tool calls for training operations.

        Args:
            tool_name: Name of the tool to execute.
            arguments: Tool arguments.

        Returns:
            List of content items with results.
        """
        try:
            if tool_name == "train_model":
                return await self._train_model(arguments)
            elif tool_name == "evaluate_model":
                return await self._evaluate_model(arguments)
            elif tool_name == "compare_models":
                return await self._compare_models(arguments)
            elif tool_name == "tune_hyperparameters":
                return await self._tune_hyperparameters(arguments)
            elif tool_name == "get_model_info":
                return await self._get_model_info(arguments)
            elif tool_name == "list_algorithms":
                return await self._list_algorithms(arguments)
            else:
                raise ValueError(f"Unknown tool: {tool_name}")

        except Exception as e:
            return self._handle_tool_error(tool_name, e)

    async def _train_model(self, args: Dict[str, Any]) -> List[TextContent]:
        """Train a machine learning model."""
        try:
            # Use unified data resolver for intelligent data discovery
            try:
                df, data_reference = self.data_resolver.resolve_data(
                    dataset_name=args.get("dataset_name"),
                    dataset_path=args.get("dataset_path"),
                    auto_fallback=True
                )
                
                self.logger.info(f"✅ Resolved dataset: {data_reference.name} from {data_reference.location_type}")
                self.logger.info(f"   Persistence mode: {data_reference.persistence_mode}")
                self.logger.info(f"   Metadata: {data_reference.metadata}")
                
            except DataError as e:
                # Provide helpful error with available data
                available_data = self.data_resolver.list_available_data()
                error_data = {
                    "status": "error",
                    "operation": "train_model",
                    "message": f"Failed to resolve dataset: {str(e)}",
                    "available_data_sources": {}
                }
                
                for source_type, references in available_data.items():
                    if references:
                        error_data["available_data_sources"][source_type] = [ref.name for ref in references]
                
                return self._create_json_response(error_data)

            # Prepare features and target
            target_column = args["target_column"]
            if target_column not in df.columns:
                raise ValidationError(
                    f"Target column '{target_column}' not found in dataset"
                )

            if "feature_columns" in args and args["feature_columns"]:
                feature_columns = args["feature_columns"]
                missing_cols = set(feature_columns) - set(df.columns)
                if missing_cols:
                    raise ValidationError(f"Feature columns not found: {missing_cols}")
                X = df[feature_columns]
            else:
                X = df.drop(columns=[target_column])

            y = df[target_column]

            # Create persistence configuration
            persistence_mode = args.get("persistence_mode", "memory_only")
            persistence_config = create_default_persistence_config(persistence_mode)
            
            # Update trainer's artifact bridge if needed
            if self.trainer.artifact_bridge.config.mode.value != persistence_mode:
                self.trainer.update_persistence_config(persistence_config)

            # Create training configuration
            config = TrainingConfig(
                algorithm=args.get("algorithm", "random_forest"),
                model_type=args.get("model_type", "auto"),
                test_size=args.get("test_size", 0.2),
                enable_tuning=args.get("enable_tuning", False),
                cv_folds=args.get("cv_folds", 5),
                random_state=args.get("random_state", 42),
                persistence=persistence_config,
            )


            # Train model using the configured persistence mode
            results = self.trainer.train_model(X, y, config)
            

            # Create structured JSON response
            artifact_storage = {}
            if results.artifact_storage:
                for artifact_type, storage_info in results.artifact_storage.items():
                    storage_data = {}
                    if "memory_reference" in storage_info:
                        storage_data["memory_key"] = storage_info['metadata']['key']
                    if "filesystem_reference" in storage_info:
                        storage_data["filesystem_path"] = storage_info["filesystem_reference"].replace("file://", "")
                    artifact_storage[artifact_type] = storage_data

            training_result = {
                "status": "success",
                "operation": "train_model",
                "model_details": {
                    "algorithm": results.algorithm,
                    "model_type": results.model_type,
                    "training_time_seconds": round(results.training_time, 2),
                    "persistence_mode": persistence_mode
                },
                "performance_metrics": {
                    "training_score": round(results.train_score, 4),
                    "test_score": round(results.test_score, 4),
                    "cross_validation_mean": round(results.cv_mean, 4) if results.cv_scores else None,
                    "cross_validation_std": round(results.cv_std, 4) if results.cv_scores else None
                },
                "artifact_storage": artifact_storage,
                "legacy_paths": {
                    "model_path": results.model_path,
                    "metrics_path": results.metrics_path
                },
                "detailed_metrics": {k: round(v, 4) if isinstance(v, (int, float)) else v for k, v in results.metrics.items()} if results.metrics else {},
                "tracking_database": str(get_tracker().db_path) if hasattr(get_tracker(), 'db_path') else None
            }

            return self._create_json_response(training_result)

        except Exception as e:
            raise TrainingError(f"Model training failed: {str(e)}") from e


    async def _evaluate_model(self, args: Dict[str, Any]) -> List[TextContent]:
        """Evaluate a trained model using unified resolvers."""
        try:
            # Use unified model resolver for intelligent model discovery
            try:
                model_path_input = args.get("model_path")
                model, model_reference = self.model_resolver.resolve_model(
                    model_name=model_path_input,  # Try as model name first (artifact key)
                    model_path=model_path_input,  # Also try as file path
                    auto_fallback=True
                )
                
                self.logger.info(f"✅ Resolved model: {model_reference.name} from {model_reference.location_type}")
                self.logger.info(f"   Persistence mode: {model_reference.persistence_mode}")
                
            except DataError as e:
                # Provide helpful error with available models
                available_models = self.model_resolver.list_available_models()
                error_data = {
                    "status": "error",
                    "operation": "evaluate_model",
                    "message": f"Failed to resolve model: {str(e)}",
                    "available_models": []
                }
                
                if available_models:
                    for model_ref in available_models:
                        error_data["available_models"].append({
                            "name": model_ref.name,
                            "location_type": model_ref.location_type
                        })
                else:
                    error_data["message"] += ". No models found. Train a model first using train_model tool."
                
                return self._create_json_response(error_data)

            # Use unified data resolver for intelligent data discovery
            try:
                df, data_reference = self.data_resolver.resolve_data(
                    dataset_name=args.get("dataset_name"),
                    dataset_path=args.get("dataset_path"),
                    auto_fallback=True
                )
                
                self.logger.info(f"✅ Resolved dataset: {data_reference.name} from {data_reference.location_type}")
                
            except DataError as e:
                # Provide helpful error with available data
                available_data = self.data_resolver.list_available_data()
                error_data = {
                    "status": "error",
                    "operation": "evaluate_model",
                    "message": f"Failed to resolve dataset: {str(e)}",
                    "available_data_sources": {}
                }
                
                for source_type, references in available_data.items():
                    if references:
                        error_data["available_data_sources"][source_type] = [ref.name for ref in references]
                
                return self._create_json_response(error_data)

            # Prepare features and target
            target_column = args["target_column"]
            if target_column not in df.columns:
                raise ValidationError(f"Target column '{target_column}' not found")

            X = df.drop(columns=[target_column])
            y = df[target_column]

            # Create evaluation configuration
            config = EvaluationConfig(
                cv_folds=args.get("cv_folds", 5),
                generate_learning_curves=args.get("generate_learning_curves", False),
                detailed_metrics=args.get("detailed_metrics", True),
            )

            # Evaluate model
            evaluation = self.evaluator.evaluate_model(
                model, X, y, model_reference.name, config
            )

            # Create structured JSON response
            cv_scores_data = {}
            for metric, mean_score in evaluation.cv_means.items():
                std_score = evaluation.cv_stds.get(metric, 0)
                cv_scores_data[metric] = {
                    "mean": round(mean_score, 4),
                    "std": round(std_score, 4)
                }

            evaluation_result = {
                "status": "success",
                "operation": "evaluate_model",
                "model_details": {
                    "name": evaluation.model_name,
                    "type": evaluation.model_type
                },
                "cross_validation_scores": cv_scores_data,
                "test_scores": {k: round(v, 4) for k, v in evaluation.test_scores.items()} if evaluation.test_scores else {},
                "has_detailed_metrics": bool(evaluation.detailed_metrics)
            }

            return self._create_json_response(evaluation_result)

        except Exception as e:
            raise TrainingError(f"Model evaluation failed: {str(e)}") from e

    async def _compare_models(self, args: Dict[str, Any]) -> List[TextContent]:
        """Compare multiple trained models using unified resolvers."""
        try:
            # Load models using unified model resolver
            model_paths = args["model_paths"]
            models = {}
            model_references = {}

            for name, path_str in model_paths.items():
                try:
                    model, model_reference = self.model_resolver.resolve_model(
                        model_name=name,  # Try as model name first (artifact key)
                        model_path=path_str,  # Also try as file path
                        auto_fallback=True
                    )
                    models[name] = model
                    model_references[name] = model_reference
                    
                    self.logger.info(f"✅ Resolved model '{name}': {model_reference.name} from {model_reference.location_type}")
                    
                except DataError as e:
                    # Provide helpful error with available models
                    available_models = self.model_resolver.list_available_models()
                    error_data = {
                        "status": "error",
                        "operation": "compare_models",
                        "message": f"Failed to resolve model '{name}': {str(e)}",
                        "available_models": []
                    }
                    
                    if available_models:
                        for model_ref in available_models:
                            error_data["available_models"].append({
                                "name": model_ref.name,
                                "location_type": model_ref.location_type
                            })
                    else:
                        error_data["message"] += ". No models found. Train models first using train_model tool."
                    
                    return self._create_json_response(error_data)

            # Use unified data resolver for intelligent data discovery
            try:
                df, data_reference = self.data_resolver.resolve_data(
                    dataset_name=args.get("dataset_name"),
                    dataset_path=args.get("dataset_path"),
                    auto_fallback=True
                )
                
                self.logger.info(f"✅ Resolved dataset: {data_reference.name} from {data_reference.location_type}")
                
            except DataError as e:
                # Provide helpful error with available data
                available_data = self.data_resolver.list_available_data()
                error_data = {
                    "status": "error",
                    "operation": "compare_models",
                    "message": f"Failed to resolve dataset: {str(e)}",
                    "available_data_sources": {}
                }
                
                for source_type, references in available_data.items():
                    if references:
                        error_data["available_data_sources"][source_type] = [ref.name for ref in references]
                
                return self._create_json_response(error_data)

            # Prepare features and target
            target_column = args["target_column"]
            if target_column not in df.columns:
                raise ValidationError(f"Target column '{target_column}' not found")

            X = df.drop(columns=[target_column])
            y = df[target_column]

            # Create evaluation configuration
            config = EvaluationConfig(
                cv_folds=args.get("cv_folds", 5),
                enable_statistical_tests=args.get("enable_statistical_tests", True),
                significance_level=args.get("significance_level", 0.05),
            )

            # Compare models
            comparison = self.evaluator.compare_models(models, X, y, config)

            # Create structured JSON response
            performance_summary = {}
            for evaluation in comparison.evaluations:
                performance_summary[evaluation.model_name] = {
                    "model_type": evaluation.model_type,
                    "cv_scores": {
                        metric: {
                            "mean": round(score, 4),
                            "std": round(evaluation.cv_stds.get(metric, 0), 4)
                        } for metric, score in evaluation.cv_means.items()
                    }
                }

            comparison_result = {
                "status": "success",
                "operation": "compare_models",
                "comparison_details": {
                    "models_compared": len(models),
                    "dataset_name": data_reference.name
                },
                "best_models_by_metric": comparison.best_models,
                "performance_summary": performance_summary,
                "has_statistical_tests": bool(comparison.statistical_tests),
                "has_summary_table": comparison.summary_table is not None and not comparison.summary_table.empty
            }

            return self._create_json_response(comparison_result)

        except Exception as e:
            raise TrainingError(f"Model comparison failed: {str(e)}") from e

    async def _tune_hyperparameters(self, args: Dict[str, Any]) -> List[TextContent]:
        """Tune hyperparameters for a model."""
        try:
            # Use unified data resolver for intelligent data discovery
            try:
                df, data_reference = self.data_resolver.resolve_data(
                    dataset_name=args.get("dataset_name"),
                    dataset_path=args.get("dataset_path"),
                    auto_fallback=True
                )
                
                self.logger.info(f"✅ Resolved dataset: {data_reference.name} from {data_reference.location_type}")
                
            except DataError as e:
                # Provide helpful error with available data
                available_data = self.data_resolver.list_available_data()
                error_data = {
                    "status": "error",
                    "operation": "tune_hyperparameters",
                    "message": f"Failed to resolve dataset: {str(e)}",
                    "available_data_sources": {}
                }
                
                for source_type, references in available_data.items():
                    if references:
                        error_data["available_data_sources"][source_type] = [ref.name for ref in references]
                
                return self._create_json_response(error_data)

            # Prepare features and target
            target_column = args["target_column"]
            if target_column not in df.columns:
                raise ValidationError(f"Target column '{target_column}' not found")

            X = df.drop(columns=[target_column])
            y = df[target_column]

            # Create training configuration with tuning enabled
            config = TrainingConfig(
                algorithm=args["algorithm"],
                enable_tuning=True,
                tuning_method=args.get("tuning_method", "grid_search"),
                tuning_cv=args.get("cv_folds", 3),
                tuning_scoring=args.get("scoring"),
                test_size=args.get("test_size", 0.2),
            )

            # Train model with tuning
            results = self.trainer.train_model(X, y, config)

            # Create structured JSON response
            tuning_result = {
                "status": "success",
                "operation": "tune_hyperparameters",
                "tuning_details": {
                    "algorithm": results.algorithm,
                    "tuning_method": config.tuning_method,
                    "search_cv_folds": config.tuning_cv
                },
                "performance_metrics": {
                    "training_score": round(results.train_score, 4),
                    "test_score": round(results.test_score, 4)
                },
                "training_time_seconds": round(results.training_time, 2),
                "model_path": results.model_path,
                "best_hyperparameters_applied": True
            }

            if results.cv_scores:
                tuning_result["performance_metrics"]["cross_validation_mean"] = round(results.cv_mean, 4)
                tuning_result["performance_metrics"]["cross_validation_std"] = round(results.cv_std, 4)

            return self._create_json_response(tuning_result)

        except Exception as e:
            raise TrainingError(f"Hyperparameter tuning failed: {str(e)}") from e

    async def _get_model_info(self, args: Dict[str, Any]) -> List[TextContent]:
        """Get information about a trained model using unified resolver."""
        try:
            # Use unified model resolver for intelligent model discovery
            try:
                model_path_input = args.get("model_path")
                model, model_reference = self.model_resolver.resolve_model(
                    model_name=model_path_input,  # Try as model name first (artifact key)
                    model_path=model_path_input,  # Also try as file path
                    auto_fallback=True
                )
                
                self.logger.info(f"✅ Resolved model: {model_reference.name} from {model_reference.location_type}")
                
            except DataError as e:
                # Provide helpful error with available models
                available_models = self.model_resolver.list_available_models()
                error_data = {
                    "status": "error",
                    "operation": "get_model_info",
                    "message": f"Failed to resolve model: {str(e)}",
                    "available_models": []
                }
                
                if available_models:
                    for model_ref in available_models:
                        error_data["available_models"].append({
                            "name": model_ref.name,
                            "location_type": model_ref.location_type
                        })
                else:
                    error_data["message"] += ". No models found. Train a model first using train_model tool."
                
                return self._create_json_response(error_data)

            # Prepare structured model info
            model_info_data = {
                "status": "success",
                "operation": "get_model_info",
                "model_details": {
                    "name": model_reference.name,
                    "location_type": model_reference.location_type,
                    "model_class": type(model).__name__,
                    "module": type(model).__module__
                },
                "parameters": {},
                "feature_analysis": {},
                "associated_metrics": {}
            }

            # Get model parameters
            try:
                params = model.get_params()
                model_info_data["parameters"] = params
            except Exception:
                model_info_data["parameters"] = None

            # Get feature importance if available
            if args.get("include_feature_importance", True):
                if hasattr(model, "feature_importances_"):
                    importances = model.feature_importances_
                    model_info_data["feature_analysis"]["type"] = "feature_importances"
                    model_info_data["feature_analysis"]["values"] = [round(float(imp), 4) for imp in importances[:10]]
                    model_info_data["feature_analysis"]["total_features"] = len(importances)
                elif hasattr(model, "coef_"):
                    coefficients = model.coef_
                    if coefficients.ndim == 1:
                        model_info_data["feature_analysis"]["type"] = "coefficients"
                        model_info_data["feature_analysis"]["values"] = [round(float(coef), 4) for coef in coefficients[:10]]
                        model_info_data["feature_analysis"]["total_features"] = len(coefficients)

            # Try to load associated metrics
            metrics = {}
            if model_reference.location_type == "filesystem" and model_reference.file_path:
                metrics_path = model_reference.file_path.parent / f"{model_reference.file_path.stem}_metrics.json"
                if metrics_path.exists():
                    try:
                        with open(metrics_path, "r") as f:
                            metrics = json.load(f)
                    except Exception:
                        metrics = {}
            else:
                # For artifact bridge models, look for metrics in metadata
                metrics = model_reference.metadata.get("metrics", {})
                
            # Add metrics to response
            if metrics:
                model_info_data["associated_metrics"] = {
                    k: round(v, 4) if isinstance(v, (int, float)) else v
                    for k, v in metrics.items()
                }

            return self._create_json_response(model_info_data)

        except Exception as e:
            raise TrainingError(f"Failed to get model info: {str(e)}") from e

    async def _list_algorithms(self, args: Dict[str, Any]) -> List[TextContent]:
        """List available machine learning algorithms."""
        try:
            model_type = args.get("model_type", "all")
            algorithms = self.trainer.get_available_algorithms(model_type)

            # Add descriptions for common algorithms
            descriptions = {
                "random_forest": "Ensemble of decision trees with random feature selection",
                "gradient_boosting": "Sequential ensemble that learns from previous errors",
                "extra_trees": "Extremely randomized trees ensemble",
                "logistic_regression": "Linear model for classification with logistic function",
                "linear_regression": "Simple linear relationship modeling",
                "ridge": "Linear regression with L2 regularization",
                "lasso": "Linear regression with L1 regularization (feature selection)",
                "elastic_net": "Linear regression with L1 and L2 regularization",
                "svm": "Support Vector Machine for classification/regression",
                "knn": "K-Nearest Neighbors - instance-based learning",
                "gaussian_nb": "Gaussian Naive Bayes classifier",
                "multinomial_nb": "Multinomial Naive Bayes for discrete features",
                "bernoulli_nb": "Bernoulli Naive Bayes for binary features",
                "decision_tree": "Single decision tree model",
            }

            algorithms_with_descriptions = {}
            for algo_type, algo_list in algorithms.items():
                algorithms_with_descriptions[algo_type] = {}
                for algo in algo_list:
                    algorithms_with_descriptions[algo_type][algo] = descriptions.get(algo, "Machine learning algorithm")

            algorithms_result = {
                "status": "success",
                "operation": "list_algorithms",
                "filter": model_type,
                "algorithms": algorithms_with_descriptions,
                "usage_note": "Specify the algorithm name in the algorithm parameter when training models"
            }

            return self._create_json_response(algorithms_result)

        except Exception as e:
            raise TrainingError(f"Failed to list algorithms: {str(e)}") from e

