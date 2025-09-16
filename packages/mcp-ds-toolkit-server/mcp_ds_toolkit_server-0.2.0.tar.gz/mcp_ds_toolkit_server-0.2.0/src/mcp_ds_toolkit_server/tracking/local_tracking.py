"""
Local experiment tracking system using SQLite.

A lightweight local tracking system that provides basic experiment tracking
capabilities for the MCP MLOps server without external dependencies.
"""

import json
import sqlite3
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import joblib
import pandas as pd


class LocalExperimentTracker:
    """
    Local experiment tracking using SQLite.

    Provides basic experiment tracking functionality for experiments,
    runs, parameters, metrics, and artifacts locally.
    """

    def __init__(self, db_path: Optional[Path] = None, artifacts_path: Optional[Path] = None):
        """
        Initialize the local experiment tracker.
        
        Args:
            db_path: Path to SQLite database file
            artifacts_path: Path to store artifacts
        """
        self.db_path = db_path or Path.home() / ".mcp-mlops" / "experiments.db"
        self.artifacts_path = artifacts_path or Path.home() / ".mcp-mlops" / "artifacts"
        
        # Ensure directories exist
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.artifacts_path.mkdir(parents=True, exist_ok=True)
        
        # Initialize database
        self._init_database()
        
        # Current experiment and run
        self._current_experiment_id: Optional[str] = None
        self._current_run_id: Optional[str] = None

    def _init_database(self) -> None:
        """Initialize the SQLite database with required tables."""
        with sqlite3.connect(self.db_path) as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS experiments (
                    experiment_id TEXT PRIMARY KEY,
                    name TEXT UNIQUE NOT NULL,
                    artifact_location TEXT,
                    lifecycle_stage TEXT DEFAULT 'active',
                    creation_time INTEGER,
                    last_update_time INTEGER
                );
                
                CREATE TABLE IF NOT EXISTS runs (
                    run_id TEXT PRIMARY KEY,
                    experiment_id TEXT,
                    run_name TEXT,
                    status TEXT DEFAULT 'RUNNING',
                    start_time INTEGER,
                    end_time INTEGER,
                    lifecycle_stage TEXT DEFAULT 'active',
                    artifact_uri TEXT,
                    FOREIGN KEY (experiment_id) REFERENCES experiments (experiment_id)
                );
                
                CREATE TABLE IF NOT EXISTS run_params (
                    run_id TEXT,
                    key TEXT,
                    value TEXT,
                    PRIMARY KEY (run_id, key),
                    FOREIGN KEY (run_id) REFERENCES runs (run_id)
                );
                
                CREATE TABLE IF NOT EXISTS run_metrics (
                    run_id TEXT,
                    key TEXT,
                    value REAL,
                    timestamp INTEGER,
                    step INTEGER DEFAULT 0,
                    FOREIGN KEY (run_id) REFERENCES runs (run_id)
                );
                
                CREATE TABLE IF NOT EXISTS run_tags (
                    run_id TEXT,
                    key TEXT,
                    value TEXT,
                    PRIMARY KEY (run_id, key),
                    FOREIGN KEY (run_id) REFERENCES runs (run_id)
                );
                
                CREATE INDEX IF NOT EXISTS idx_runs_experiment_id ON runs(experiment_id);
                CREATE INDEX IF NOT EXISTS idx_metrics_run_id ON run_metrics(run_id);
                CREATE INDEX IF NOT EXISTS idx_params_run_id ON run_params(run_id);
            """)

    def create_experiment(self, name: str) -> str:
        """
        Create a new experiment.
        
        Args:
            name: Experiment name
            
        Returns:
            Experiment ID
        """
        experiment_id = f"exp_{int(time.time() * 1000)}"
        current_time = int(time.time() * 1000)
        artifact_location = str(self.artifacts_path / experiment_id)
        
        with sqlite3.connect(self.db_path) as conn:
            try:
                conn.execute("""
                    INSERT INTO experiments 
                    (experiment_id, name, artifact_location, creation_time, last_update_time)
                    VALUES (?, ?, ?, ?, ?)
                """, (experiment_id, name, artifact_location, current_time, current_time))
                
                # Create artifact directory
                Path(artifact_location).mkdir(parents=True, exist_ok=True)
                
                return experiment_id
            except sqlite3.IntegrityError:
                # Experiment name already exists, get existing ID
                cursor = conn.execute(
                    "SELECT experiment_id FROM experiments WHERE name = ?", (name,)
                )
                result = cursor.fetchone()
                return result[0] if result else experiment_id

    def get_experiment_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """Get experiment by name."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT * FROM experiments WHERE name = ?", (name,)
            )
            result = cursor.fetchone()
            if result:
                columns = [desc[0] for desc in cursor.description]
                return dict(zip(columns, result))
        return None

    def list_experiments(self) -> List[Dict[str, Any]]:
        """List all experiments."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT * FROM experiments WHERE lifecycle_stage = 'active' ORDER BY creation_time DESC"
            )
            columns = [desc[0] for desc in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]

    def start_run(self, experiment_id: Optional[str] = None, run_name: Optional[str] = None) -> str:
        """
        Start a new run.
        
        Args:
            experiment_id: Experiment ID (creates default if None)
            run_name: Optional run name
            
        Returns:
            Run ID
        """
        if experiment_id is None:
            # Create default experiment if none exists
            default_exp = self.get_experiment_by_name("Default")
            if default_exp is None:
                experiment_id = self.create_experiment("Default")
            else:
                experiment_id = default_exp["experiment_id"]
        
        run_id = f"run_{int(time.time() * 1000)}"
        current_time = int(time.time() * 1000)
        artifact_uri = str(self.artifacts_path / experiment_id / run_id)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO runs 
                (run_id, experiment_id, run_name, start_time, artifact_uri)
                VALUES (?, ?, ?, ?, ?)
            """, (run_id, experiment_id, run_name, current_time, artifact_uri))
        
        # Create run artifact directory
        Path(artifact_uri).mkdir(parents=True, exist_ok=True)
        
        self._current_experiment_id = experiment_id
        self._current_run_id = run_id
        
        return run_id

    def end_run(self, run_id: Optional[str] = None, status: str = "FINISHED") -> None:
        """End a run."""
        run_id = run_id or self._current_run_id
        if not run_id:
            return
        
        current_time = int(time.time() * 1000)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                UPDATE runs 
                SET status = ?, end_time = ?
                WHERE run_id = ?
            """, (status, current_time, run_id))
        
        if run_id == self._current_run_id:
            self._current_run_id = None

    def log_param(self, key: str, value: Any, run_id: Optional[str] = None) -> None:
        """Log a parameter."""
        run_id = run_id or self._current_run_id
        if not run_id:
            raise ValueError("No active run. Start a run first.")
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO run_params (run_id, key, value)
                VALUES (?, ?, ?)
            """, (run_id, key, str(value)))

    def log_metric(self, key: str, value: float, step: int = 0, run_id: Optional[str] = None) -> None:
        """Log a metric."""
        run_id = run_id or self._current_run_id
        if not run_id:
            raise ValueError("No active run. Start a run first.")
        
        current_time = int(time.time() * 1000)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO run_metrics (run_id, key, value, timestamp, step)
                VALUES (?, ?, ?, ?, ?)
            """, (run_id, key, value, current_time, step))

    def log_metrics(self, metrics: Dict[str, float], step: int = 0, run_id: Optional[str] = None) -> None:
        """Log multiple metrics."""
        for key, value in metrics.items():
            self.log_metric(key, value, step, run_id)

    def log_params(self, params: Dict[str, Any], run_id: Optional[str] = None) -> None:
        """Log multiple parameters."""
        for key, value in params.items():
            self.log_param(key, value, run_id)

    def log_artifact(self, local_path: Union[str, Path], artifact_path: Optional[str] = None, run_id: Optional[str] = None) -> None:
        """
        Log an artifact (file).
        
        Args:
            local_path: Local file path to log
            artifact_path: Optional path within artifact directory
            run_id: Run ID (uses current run if None)
        """
        run_id = run_id or self._current_run_id
        if not run_id:
            raise ValueError("No active run. Start a run first.")
        
        local_path = Path(local_path)
        if not local_path.exists():
            raise FileNotFoundError(f"File not found: {local_path}")
        
        # Get run artifact directory
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT artifact_uri FROM runs WHERE run_id = ?", (run_id,))
            result = cursor.fetchone()
            if not result:
                raise ValueError(f"Run not found: {run_id}")
            
            artifact_uri = Path(result[0])
        
        # Determine destination path
        if artifact_path:
            dest_path = artifact_uri / artifact_path
        else:
            dest_path = artifact_uri / local_path.name
        
        # Create destination directory
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Copy file
        import shutil
        shutil.copy2(local_path, dest_path)

    def log_model(self, model: Any, artifact_path: str = "model", run_id: Optional[str] = None) -> None:
        """
        Log a trained model.
        
        Args:
            model: Trained model object
            artifact_path: Path within artifacts directory
            run_id: Run ID (uses current run if None)
        """
        run_id = run_id or self._current_run_id
        if not run_id:
            raise ValueError("No active run. Start a run first.")
        
        # Get run artifact directory
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT artifact_uri FROM runs WHERE run_id = ?", (run_id,))
            result = cursor.fetchone()
            if not result:
                raise ValueError(f"Run not found: {run_id}")
            
            artifact_uri = Path(result[0])
        
        # Save model using joblib
        model_dir = artifact_uri / artifact_path
        model_dir.mkdir(parents=True, exist_ok=True)
        
        model_path = model_dir / "model.pkl"
        joblib.dump(model, model_path)
        
        # Save model metadata
        metadata = {
            "model_type": type(model).__name__,
            "timestamp": datetime.now().isoformat(),
            "path": str(model_path)
        }
        
        metadata_path = model_dir / "metadata.json"
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)

    def get_run(self, run_id: str) -> Optional[Dict[str, Any]]:
        """Get run information."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT * FROM runs WHERE run_id = ?", (run_id,))
            result = cursor.fetchone()
            if result:
                columns = [desc[0] for desc in cursor.description]
                run_data = dict(zip(columns, result))
                
                # Get parameters
                cursor = conn.execute("SELECT key, value FROM run_params WHERE run_id = ?", (run_id,))
                run_data["params"] = dict(cursor.fetchall())
                
                # Get metrics
                cursor = conn.execute("""
                    SELECT key, value, timestamp, step 
                    FROM run_metrics WHERE run_id = ? 
                    ORDER BY timestamp
                """, (run_id,))
                metrics = {}
                for key, value, timestamp, step in cursor.fetchall():
                    if key not in metrics:
                        metrics[key] = []
                    metrics[key].append({"value": value, "timestamp": timestamp, "step": step})
                run_data["metrics"] = metrics
                
                return run_data
        return None

    def list_runs(self, experiment_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """List runs for an experiment."""
        with sqlite3.connect(self.db_path) as conn:
            if experiment_id:
                cursor = conn.execute(
                    "SELECT * FROM runs WHERE experiment_id = ? ORDER BY start_time DESC",
                    (experiment_id,)
                )
            else:
                cursor = conn.execute("SELECT * FROM runs ORDER BY start_time DESC")
            
            columns = [desc[0] for desc in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]

    def search_runs(self, experiment_ids: Optional[List[str]] = None, filter_string: Optional[str] = None) -> List[Dict[str, Any]]:
        """Search runs with basic filtering."""
        # Simple implementation - can be enhanced with proper query parsing
        runs = []
        
        if experiment_ids:
            for exp_id in experiment_ids:
                runs.extend(self.list_runs(exp_id))
        else:
            runs = self.list_runs()
        
        # Basic filtering by status if provided
        if filter_string and "status" in filter_string.lower():
            if "finished" in filter_string.lower():
                runs = [r for r in runs if r.get("status") == "FINISHED"]
            elif "running" in filter_string.lower():
                runs = [r for r in runs if r.get("status") == "RUNNING"]
        
        return runs

    def delete_run(self, run_id: str) -> None:
        """Delete a run and its associated data."""
        with sqlite3.connect(self.db_path) as conn:
            # Delete from all related tables
            conn.execute("DELETE FROM run_metrics WHERE run_id = ?", (run_id,))
            conn.execute("DELETE FROM run_params WHERE run_id = ?", (run_id,))
            conn.execute("DELETE FROM run_tags WHERE run_id = ?", (run_id,))
            conn.execute("DELETE FROM runs WHERE run_id = ?", (run_id,))
        
        # Clean up artifacts directory
        import shutil
        for path in self.artifacts_path.glob(f"*/{run_id}"):
            if path.is_dir():
                shutil.rmtree(path)

    @property
    def active_run_id(self) -> Optional[str]:
        """Get the current active run ID."""
        return self._current_run_id

    @property
    def active_experiment_id(self) -> Optional[str]:
        """Get the current active experiment ID."""
        return self._current_experiment_id


# Global tracker instance
_tracker: Optional[LocalExperimentTracker] = None


def get_tracker() -> LocalExperimentTracker:
    """Get the global tracker instance."""
    global _tracker
    if _tracker is None:
        _tracker = LocalExperimentTracker()
    return _tracker


# Convenience functions for local tracking API
def create_experiment(name: str) -> str:
    """Create a new experiment."""
    return get_tracker().create_experiment(name)


def start_run(experiment_id: Optional[str] = None, run_name: Optional[str] = None) -> str:
    """Start a new run."""
    return get_tracker().start_run(experiment_id, run_name)


def end_run(status: str = "FINISHED") -> None:
    """End the current run."""
    get_tracker().end_run(status=status)


def log_param(key: str, value: Any) -> None:
    """Log a parameter."""
    get_tracker().log_param(key, value)


def log_metric(key: str, value: float, step: int = 0) -> None:
    """Log a metric."""
    get_tracker().log_metric(key, value, step)


def log_metrics(metrics: Dict[str, float], step: int = 0) -> None:
    """Log multiple metrics."""
    get_tracker().log_metrics(metrics, step)


def log_params(params: Dict[str, Any]) -> None:
    """Log multiple parameters."""
    get_tracker().log_params(params)


def log_artifact(local_path: Union[str, Path], artifact_path: Optional[str] = None) -> None:
    """Log an artifact."""
    get_tracker().log_artifact(local_path, artifact_path)


def log_model(model: Any, artifact_path: str = "model") -> None:
    """Log a model."""
    get_tracker().log_model(model, artifact_path)


def get_experiment_by_name(name: str) -> Optional[Dict[str, Any]]:
    """Get experiment by name."""
    return get_tracker().get_experiment_by_name(name)


def list_experiments() -> List[Dict[str, Any]]:
    """List all experiments."""
    return get_tracker().list_experiments()


def get_run(run_id: str) -> Optional[Dict[str, Any]]:
    """Get run information."""
    return get_tracker().get_run(run_id)


def list_runs(experiment_id: Optional[str] = None) -> List[Dict[str, Any]]:
    """List runs."""
    return get_tracker().list_runs(experiment_id)


def search_runs(experiment_ids: Optional[List[str]] = None, filter_string: Optional[str] = None) -> List[Dict[str, Any]]:
    """Search runs."""
    return get_tracker().search_runs(experiment_ids, filter_string)


def active_run() -> Optional[Dict[str, Any]]:
    """Get the active run."""
    tracker = get_tracker()
    if tracker.active_run_id:
        return tracker.get_run(tracker.active_run_id)
    return None