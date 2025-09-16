"""Experiment Tracking Tools Module

This module provides MCP tools for local experiment tracking operations
including experiment management, run tracking, and model artifact logging.
"""


import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Union

from mcp.types import (
    EmbeddedResource,
    ImageContent,
    LoggingLevel,
    TextContent,
    Tool,
)

from mcp_ds_toolkit_server.tools.base import BaseMCPTools
from mcp_ds_toolkit_server.exceptions import TrackingError, ValidationError
from mcp_ds_toolkit_server.tracking import get_tracker
from mcp_ds_toolkit_server.utils.config import Settings


class TrackingTools(BaseMCPTools):
    """MCP tools for local experiment tracking operations."""

    def __init__(self, workspace_path: Path, artifact_bridge=None):
        """Initialize tracking tools.

        Args:
            workspace_path: Path to the workspace directory.
            artifact_bridge: Shared artifact bridge for persistence operations.
        """
        # Use base class initialization to eliminate redundancy
        super().__init__(
            workspace_path=workspace_path,
            persistence_mode="memory_only",
            artifact_bridge=artifact_bridge
        )

    def _get_tracker(self):
        """Get the local experiment tracker."""
        return get_tracker()

    def get_tools(self) -> List[Tool]:
        """Get list of available tracking tools.

        Returns:
            List of MCP tools for tracking operations.
        """
        return [
            Tool(
                name="create_experiment",
                description="Create a new experiment for organizing runs",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": "string",
                            "description": "Name of the experiment",
                        },
                        "description": {
                            "type": "string",
                            "description": "Optional description of the experiment",
                        },
                        "tags": {
                            "type": "object",
                            "description": "Optional tags as key-value pairs",
                            "additionalProperties": {"type": "string"},
                        },
                        "artifact_location": {
                            "type": "string",
                            "description": "Optional custom artifact location",
                        },
                    },
                    "required": ["name"],
                },
            ),
            Tool(
                name="start_run",
                description="Start a new run within an experiment",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "experiment_name": {
                            "type": "string",
                            "description": "Name of the experiment to run in",
                        },
                        "run_name": {
                            "type": "string",
                            "description": "Optional name for the run",
                        },
                        "description": {
                            "type": "string",
                            "description": "Optional description of the run",
                        },
                        "tags": {
                            "type": "object",
                            "description": "Optional tags as key-value pairs",
                            "additionalProperties": {"type": "string"},
                        },
                    },
                    "required": ["experiment_name"],
                },
            ),
            Tool(
                name="log_params",
                description="Log parameters to the current run",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "params": {
                            "type": "object",
                            "description": "Parameters as key-value pairs",
                            "additionalProperties": {
                                "type": ["string", "number", "boolean"]
                            },
                        }
                    },
                    "required": ["params"],
                },
            ),
            Tool(
                name="log_metrics",
                description="Log metrics to the current run",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "metrics": {
                            "type": "object",
                            "description": "Metrics as key-value pairs",
                            "additionalProperties": {"type": "number"},
                        },
                        "step": {
                            "type": "integer",
                            "description": "Optional step number for tracking metrics over time",
                        },
                    },
                    "required": ["metrics"],
                },
            ),
            Tool(
                name="log_artifact",
                description="Log an artifact (file) to the current run",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "artifact_path": {
                            "type": "string",
                            "description": "Path to the artifact file to log",
                        },
                        "artifact_name": {
                            "type": "string",
                            "description": "Optional name for the artifact",
                        },
                    },
                    "required": ["artifact_path"],
                },
            ),
            Tool(
                name="end_run",
                description="End the current run",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "status": {
                            "type": "string",
                            "enum": ["FINISHED", "FAILED", "KILLED"],
                            "description": "Status of the run completion",
                            "default": "FINISHED",
                        }
                    },
                },
            ),
            Tool(
                name="list_experiments",
                description="List all experiments",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "limit": {
                            "type": "integer",
                            "minimum": 1,
                            "maximum": 100,
                            "description": "Maximum number of experiments to return",
                            "default": 20,
                        }
                    },
                },
            ),
            Tool(
                name="get_experiment",
                description="Get details of a specific experiment",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "experiment_name": {
                            "type": "string",
                            "description": "Name of the experiment to retrieve",
                        }
                    },
                    "required": ["experiment_name"],
                },
            ),
            Tool(
                name="list_runs",
                description="List runs from an experiment",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "experiment_name": {
                            "type": "string",
                            "description": "Name of the experiment",
                        },
                        "limit": {
                            "type": "integer",
                            "minimum": 1,
                            "maximum": 100,
                            "description": "Maximum number of runs to return",
                            "default": 20,
                        },
                    },
                    "required": ["experiment_name"],
                },
            ),
            Tool(
                name="compare_runs",
                description="Compare multiple runs",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "run_ids": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "List of run IDs to compare",
                            "minItems": 2,
                            "maxItems": 10,
                        },
                        "metrics": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Specific metrics to compare (optional)",
                        },
                    },
                    "required": ["run_ids"],
                },
            ),
        ]

    async def handle_tool_call(
        self, tool_name: str, arguments: Dict[str, Any]
    ) -> List[TextContent | ImageContent | EmbeddedResource]:
        """Handle MCP tool calls for tracking operations.

        Args:
            tool_name: Name of the tool to execute.
            arguments: Tool arguments.

        Returns:
            List of content items with results.
        """
        try:
            # Get local tracker
            tracker = self._get_tracker()

            if tool_name == "create_experiment":
                return await self._create_experiment(arguments)
            elif tool_name == "start_run":
                return await self._start_run(arguments)
            elif tool_name == "log_params":
                return await self._log_params(arguments)
            elif tool_name == "log_metrics":
                return await self._log_metrics(arguments)
            elif tool_name == "log_artifact":
                return await self._log_artifact(arguments)
            elif tool_name == "end_run":
                return await self._end_run(arguments)
            elif tool_name == "list_experiments":
                return await self._list_experiments(arguments)
            elif tool_name == "get_experiment":
                return await self._get_experiment(arguments)
            elif tool_name == "list_runs":
                return await self._list_runs(arguments)
            elif tool_name == "compare_runs":
                return await self._compare_runs(arguments)
            else:
                raise ValueError(f"Unknown tool: {tool_name}")

        except Exception as e:
            return self._handle_tool_error(tool_name, e)

    async def _create_experiment(self, args: Dict[str, Any]) -> List[TextContent]:
        """Create a new experiment."""
        try:
            tracker = self._get_tracker()
            
            name = args["name"]
            experiment_id = tracker.create_experiment(name)

            experiment_result = {
                "status": "success",
                "operation": "create_experiment",
                "experiment_details": {
                    "name": name,
                    "experiment_id": experiment_id,
                    "storage_type": "Local SQLite database"
                },
                "next_steps": [
                    f"Start a run: start_run with experiment_name=\"{name}\"",
                    "Log parameters and metrics during your ML workflow",
                    "Track model artifacts and results"
                ],
                "usage_example": f"start_run experiment_name=\"{name}\" run_name=\"baseline_model\""
            }

            return self._create_json_response(experiment_result)

        except Exception as e:
            raise TrackingError(f"Failed to create experiment: {str(e)}") from e

    async def _start_run(self, args: Dict[str, Any]) -> List[TextContent]:
        """Start a new run."""
        try:
            tracker = self._get_tracker()

            experiment_name = args["experiment_name"]
            run_name = args.get("run_name")
            
            # Get or create experiment
            experiment = tracker.get_experiment_by_name(experiment_name)
            if not experiment:
                experiment_id = tracker.create_experiment(experiment_name)
            else:
                experiment_id = experiment["experiment_id"]

            run_id = tracker.start_run(experiment_id, run_name)

            run_result = {
                "status": "success",
                "operation": "start_run",
                "run_details": {
                    "run_id": run_id,
                    "experiment_name": experiment_name,
                    "run_name": run_name or 'Unnamed'
                },
                "active_status": {
                    "ready_for_logging": True,
                    "accepts_parameters": True,
                    "accepts_metrics": True,
                    "accepts_artifacts": True
                },
                "common_next_steps": [
                    "Log parameters: log_params params={\"algorithm\": \"random_forest\", \"n_estimators\": 100}",
                    "Log metrics: log_metrics metrics={\"accuracy\": 0.95, \"f1_score\": 0.92}",
                    "Log artifacts: log_artifact artifact_path=\"model.pkl\"",
                    "End run: end_run status=\"FINISHED\""
                ],
                "reminder": "Remember to end the run when your experiment is complete"
            }

            return self._create_json_response(run_result)

        except Exception as e:
            raise TrackingError(f"Failed to start run: {str(e)}") from e

    async def _log_params(self, args: Dict[str, Any]) -> List[TextContent]:
        """Log parameters to the current run."""
        try:
            tracker = self._get_tracker()
            params = args["params"]
            tracker.log_params(params)

            logged_params = {}
            for key, value in params.items():
                logged_params[key] = value

            params_result = {
                "status": "success",
                "operation": "log_params",
                "logged_parameters": {
                    "count": len(params),
                    "parameters": logged_params
                },
                "benefits": [
                    "Retrieved for run comparison and analysis",
                    "Used for experiment filtering",
                    "Accessed via the local tracking API"
                ],
                "next_suggestion": "Continue logging metrics and artifacts to complete your experiment tracking"
            }

            return self._create_json_response(params_result)

        except Exception as e:
            raise TrackingError(f"Failed to log parameters: {str(e)}") from e

    async def _log_metrics(self, args: Dict[str, Any]) -> List[TextContent]:
        """Log metrics to the current run."""
        try:
            tracker = self._get_tracker()
            metrics = args["metrics"]
            step = args.get("step", 0)

            tracker.log_metrics(metrics, step)

            logged_metrics = {}
            for key, value in metrics.items():
                logged_metrics[key] = {
                    "value": round(value, 4),
                    "step": step
                }

            metrics_result = {
                "status": "success",
                "operation": "log_metrics",
                "logged_metrics": {
                    "count": len(metrics),
                    "metrics": logged_metrics
                },
                "benefits": [
                    "Track model performance over time",
                    "Compare different runs and experiments",
                    "Analyze trends and improvements",
                    "Support automated model selection"
                ],
                "next_suggestion": "Continue your experiment or compare with other runs"
            }

            return self._create_json_response(metrics_result)

        except Exception as e:
            raise TrackingError(f"Failed to log metrics: {str(e)}") from e

    async def _log_artifact(self, args: Dict[str, Any]) -> List[TextContent]:
        """Log an artifact to the current run."""
        try:
            tracker = self._get_tracker()
            artifact_path = Path(args["artifact_path"])
            artifact_name = args.get("artifact_name")

            if not artifact_path.exists():
                raise ValidationError(f"Artifact file not found: {artifact_path}")

            tracker.log_artifact(str(artifact_path), artifact_name)

            artifact_result = {
                "status": "success",
                "operation": "log_artifact",
                "artifact_details": {
                    "file_name": artifact_path.name,
                    "file_path": str(artifact_path),
                    "size_kb": round(artifact_path.stat().st_size / 1024, 1),
                    "artifact_name": artifact_name or artifact_path.name
                },
                "benefits": [
                    "Permanent local storage linked to this run",
                    "Version control for models and data",
                    "Easy retrieval and deployment",
                    "Reproducible experiments"
                ],
                "message": "Artifact is now safely stored and linked to this run"
            }

            return self._create_json_response(artifact_result)

        except Exception as e:
            raise TrackingError(f"Failed to log artifact: {str(e)}") from e

    async def _end_run(self, args: Dict[str, Any]) -> List[TextContent]:
        """End the current run."""
        try:
            tracker = self._get_tracker()
            status = args.get("status", "FINISHED")
            tracker.end_run(status=status)

            end_run_result = {
                "status": "success",
                "operation": "end_run",
                "run_status": status,
                "completion_details": [
                    "All logged data has been saved locally",
                    "Run is now immutable and preserved",
                    "Artifacts are stored and accessible",
                    "Metrics and parameters are finalized"
                ],
                "next_steps": [
                    "Compare with other runs using compare_runs",
                    "Start a new run for further experiments",
                    "Use logged artifacts for model deployment",
                    "Analyze results programmatically"
                ],
                "data_access": [
                    "Local SQLite database stores all data",
                    "Programmatic access via local tracking API",
                    "Artifacts available in local filesystem"
                ]
            }

            return self._create_json_response(end_run_result)

        except Exception as e:
            raise TrackingError(f"Failed to end run: {str(e)}") from e

    async def _list_experiments(self, args: Dict[str, Any]) -> List[TextContent]:
        """List all experiments."""
        try:
            tracker = self._get_tracker()
            limit = args.get("limit", 20)
            experiments = tracker.list_experiments()

            if not experiments:
                no_experiments_result = {
                    "status": "success",
                    "operation": "list_experiments",
                    "message": "No experiments exist yet",
                    "suggestion": "Create your first experiment with create_experiment",
                    "experiment_count": 0,
                    "experiments": []
                }
                return self._create_json_response(no_experiments_result)

            # Limit results
            experiments = experiments[:limit]

            experiments_list = []
            for exp in experiments:
                experiments_list.append({
                    "name": exp.get('name', 'Unnamed'),
                    "experiment_id": exp.get('experiment_id', 'Unknown'),
                    "lifecycle_stage": exp.get('lifecycle_stage', 'Unknown'),
                    "creation_time": exp.get('creation_time', 'Unknown')
                })

            list_experiments_result = {
                "status": "success",
                "operation": "list_experiments",
                "experiment_count": len(experiments_list),
                "showing_count": len(experiments_list),
                "experiments": experiments_list,
                "available_actions": [
                    "Get details: get_experiment experiment_name=\"<name>\"",
                    "Start run: start_run experiment_name=\"<name>\"",
                    "List runs: list_runs experiment_name=\"<name>\""
                ]
            }

            return self._create_json_response(list_experiments_result)

        except Exception as e:
            raise TrackingError(f"Failed to list experiments: {str(e)}") from e

    async def _get_experiment(self, args: Dict[str, Any]) -> List[TextContent]:
        """Get details of a specific experiment."""
        try:
            tracker = self._get_tracker()
            experiment_name = args["experiment_name"]
            experiment = tracker.get_experiment_by_name(experiment_name)

            if not experiment:
                error_result = {
                    "status": "error",
                    "operation": "get_experiment",
                    "message": f"Experiment '{experiment_name}' does not exist",
                    "experiment_name": experiment_name
                }
                return self._create_json_response(error_result)

            experiment_details_result = {
                "status": "success",
                "operation": "get_experiment",
                "experiment_name": experiment_name,
                "basic_information": {
                    "experiment_id": experiment.get('experiment_id'),
                    "name": experiment.get('name'),
                    "lifecycle_stage": experiment.get('lifecycle_stage'),
                    "artifact_location": experiment.get('artifact_location')
                },
                "usage_commands": [
                    f"Start new run: start_run experiment_name=\"{experiment_name}\"",
                    f"View runs: list_runs experiment_name=\"{experiment_name}\"",
                    "Local storage in SQLite database"
                ],
                "message": "This experiment is ready for new runs and tracking"
            }

            return self._create_json_response(experiment_details_result)

        except Exception as e:
            raise TrackingError(f"Failed to get experiment: {str(e)}") from e

    async def _list_runs(self, args: Dict[str, Any]) -> List[TextContent]:
        """List runs from an experiment."""
        try:
            tracker = self._get_tracker()
            experiment_name = args["experiment_name"]
            limit = args.get("limit", 20)

            experiment = tracker.get_experiment_by_name(experiment_name)
            if not experiment:
                error_result = {
                    "status": "error",
                    "operation": "list_runs",
                    "message": f"Experiment '{experiment_name}' does not exist",
                    "experiment_name": experiment_name
                }
                return self._create_json_response(error_result)

            runs = tracker.list_runs(experiment["experiment_id"])[:limit]

            if not runs:
                no_runs_result = {
                    "status": "success",
                    "operation": "list_runs",
                    "experiment_name": experiment_name,
                    "message": f"No runs exist for experiment '{experiment_name}'",
                    "suggestion": "Start a new run with start_run",
                    "run_count": 0,
                    "runs": []
                }
                return self._create_json_response(no_runs_result)

            runs_list = []
            for run in runs:
                runs_list.append({
                    "run_id": run.get('run_id', 'Unknown'),
                    "run_id_short": run.get('run_id', 'Unknown')[:8],
                    "status": run.get('status', 'Unknown'),
                    "start_time": run.get('start_time', 'Unknown'),
                    "run_name": run.get('run_name', 'Unnamed')
                })

            list_runs_result = {
                "status": "success",
                "operation": "list_runs",
                "experiment_name": experiment_name,
                "run_count": len(runs_list),
                "showing_count": len(runs_list),
                "runs": runs_list,
                "available_actions": [
                    "Compare runs: compare_runs run_ids=[\"run1\", \"run2\"]",
                    f"Start new run: start_run experiment_name=\"{experiment_name}\""
                ]
            }

            return self._create_json_response(list_runs_result)

        except Exception as e:
            raise TrackingError(f"Failed to list runs: {str(e)}") from e

    async def _compare_runs(self, args: Dict[str, Any]) -> List[TextContent]:
        """Compare multiple runs."""
        try:
            tracker = self._get_tracker()
            run_ids = args["run_ids"]
            metrics = args.get("metrics")

            comparison_data = []
            for run_id in run_ids:
                run_data = tracker.get_run(run_id)
                if run_data:
                    comparison_data.append(run_data)

            if not comparison_data:
                error_result = {
                    "status": "error",
                    "operation": "compare_runs",
                    "message": "None of the specified run IDs exist",
                    "requested_run_ids": run_ids,
                    "found_runs_count": 0
                }
                return self._create_json_response(error_result)

            compared_runs = []
            for run_data in comparison_data:
                compared_runs.append({
                    "run_id": run_data.get('run_id', 'Unknown'),
                    "run_id_short": run_data.get('run_id', 'Unknown')[:8],
                    "status": run_data.get('status', 'Unknown'),
                    "parameters_count": len(run_data.get('params', {})),
                    "metrics_count": len(run_data.get('metrics', {})),
                    "parameters": run_data.get('params', {}),
                    "metrics": run_data.get('metrics', {})
                })

            comparison_result = {
                "status": "success",
                "operation": "compare_runs",
                "compared_runs_count": len(comparison_data),
                "requested_runs_count": len(run_ids),
                "runs": compared_runs,
                "comparison_features": [
                    "All runs retrieved from local database",
                    "Parameters and metrics available for analysis",
                    "Artifact locations tracked",
                    "Programmatic access via local tracking API"
                ]
            }

            return self._create_json_response(comparison_result)

        except Exception as e:
            raise TrackingError(f"Failed to compare runs: {str(e)}") from e
