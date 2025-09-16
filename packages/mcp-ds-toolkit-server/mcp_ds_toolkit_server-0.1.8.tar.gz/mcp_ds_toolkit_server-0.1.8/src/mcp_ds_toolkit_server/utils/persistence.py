"""
Core persistence and artifact management utilities for the MCP MLOps server.

This module provides the fundamental persistence architecture including:
- Persistence mode definitions and configuration
- Artifact serialization and encoding utilities
- Memory-to-filesystem bridge functionality
- Session-level artifact management

The persistence system supports three modes:
1. MEMORY_ONLY: All artifacts stored in memory (default, MCP-friendly)
2. FILESYSTEM: Traditional filesystem storage (MLOps standard)
3. HYBRID: Both memory and filesystem storage (best of both worlds)
"""

import base64
import json
import pickle
import hashlib
import tempfile
from dataclasses import asdict, dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
import logging

import pandas as pd
import numpy as np
from sklearn.base import BaseEstimator

logger = logging.getLogger(__name__)


class PersistenceMode(Enum):
    """Enumeration of persistence modes for artifacts and data."""
    
    MEMORY_ONLY = "memory_only"    # Store everything in memory (default, MCP-friendly)
    FILESYSTEM = "filesystem"      # Store everything on filesystem (traditional MLOps)
    HYBRID = "hybrid"              # Store in both memory and filesystem


class ArtifactEncoding(Enum):
    """Enumeration of artifact encoding methods for memory storage."""
    
    BASE64 = "base64"             # Base64 encoding for binary data
    JSON = "json"                 # JSON serialization for structured data
    PICKLE_B64 = "pickle_b64"     # Pickled then base64 encoded


@dataclass
class PersistenceConfig:
    """Configuration for persistence behavior across the MCP MLOps server.
    
    This class centralizes all persistence-related configuration, allowing
    fine-grained control over where and how artifacts are stored.
    
    Attributes:
        mode: Primary persistence mode (memory_only, filesystem, hybrid)
        export_artifacts: Whether to return artifacts in tool responses
        artifact_encoding: How to encode artifacts for memory storage
        filesystem_fallback: Whether to fallback to filesystem if memory fails
        max_memory_size_mb: Maximum size of artifacts to keep in memory
        compress_artifacts: Whether to compress artifacts in memory
    """
    
    mode: PersistenceMode = PersistenceMode.MEMORY_ONLY
    export_artifacts: bool = True
    artifact_encoding: ArtifactEncoding = ArtifactEncoding.BASE64
    filesystem_fallback: bool = True
    max_memory_size_mb: int = 100
    compress_artifacts: bool = True
    
    def should_save_to_filesystem(self) -> bool:
        """Check if artifacts should be saved to filesystem."""
        return self.mode in [PersistenceMode.FILESYSTEM, PersistenceMode.HYBRID]
    
    def should_store_in_memory(self) -> bool:
        """Check if artifacts should be stored in memory."""
        return self.mode in [PersistenceMode.MEMORY_ONLY, PersistenceMode.HYBRID]
    
    def should_return_artifacts(self) -> bool:
        """Check if artifacts should be returned in tool responses."""
        return self.export_artifacts and self.should_store_in_memory()


class ArtifactSerializer:
    """Handles serialization and deserialization of various artifact types.
    
    This class provides a unified interface for converting artifacts between
    different formats (pickle, base64, JSON) and storage modes.
    """
    
    @staticmethod
    def serialize_model(model: BaseEstimator, encoding: ArtifactEncoding) -> str:
        """Serialize a scikit-learn model for storage or transmission.
        
        Args:
            model: The scikit-learn model to serialize
            encoding: How to encode the serialized model
            
        Returns:
            Serialized model as a string
            
        Raises:
            ValueError: If encoding method is unsupported
        """
        if encoding == ArtifactEncoding.PICKLE_B64:
            model_bytes = pickle.dumps(model)
            return base64.b64encode(model_bytes).decode('utf-8')
        elif encoding == ArtifactEncoding.BASE64:
            # For backwards compatibility
            model_bytes = pickle.dumps(model)
            return base64.b64encode(model_bytes).decode('utf-8')
        else:
            raise ValueError(f"Unsupported encoding for model: {encoding}")
    
    @staticmethod
    def deserialize_model(data: str, encoding: ArtifactEncoding) -> BaseEstimator:
        """Deserialize a model from encoded data.
        
        Args:
            data: Encoded model data
            encoding: Encoding method used
            
        Returns:
            Deserialized scikit-learn model
        """
        if encoding in [ArtifactEncoding.PICKLE_B64, ArtifactEncoding.BASE64]:
            model_bytes = base64.b64decode(data.encode('utf-8'))
            return pickle.loads(model_bytes)
        else:
            raise ValueError(f"Unsupported encoding for model: {encoding}")
    
    @staticmethod
    def serialize_dataset(dataset: pd.DataFrame, encoding: ArtifactEncoding) -> str:
        """Serialize a pandas DataFrame for storage or transmission.
        
        Args:
            dataset: The DataFrame to serialize
            encoding: How to encode the dataset
            
        Returns:
            Serialized dataset as a string
        """
        if encoding == ArtifactEncoding.JSON:
            return dataset.to_json(orient='records', date_format='iso')
        elif encoding == ArtifactEncoding.BASE64:
            csv_bytes = dataset.to_csv(index=False).encode('utf-8')
            return base64.b64encode(csv_bytes).decode('utf-8')
        else:
            raise ValueError(f"Unsupported encoding for dataset: {encoding}")
    
    @staticmethod
    def deserialize_dataset(data: str, encoding: ArtifactEncoding) -> pd.DataFrame:
        """Deserialize a DataFrame from encoded data.
        
        Args:
            data: Encoded dataset data
            encoding: Encoding method used
            
        Returns:
            Deserialized pandas DataFrame
        """
        if encoding == ArtifactEncoding.JSON:
            return pd.read_json(data, orient='records')
        elif encoding == ArtifactEncoding.BASE64:
            csv_bytes = base64.b64decode(data.encode('utf-8'))
            csv_str = csv_bytes.decode('utf-8')
            from io import StringIO
            return pd.read_csv(StringIO(csv_str))
        else:
            raise ValueError(f"Unsupported encoding for dataset: {encoding}")
    
    @staticmethod
    def serialize_metrics(metrics: Dict[str, Any], encoding: ArtifactEncoding) -> str:
        """Serialize metrics dictionary.
        
        Args:
            metrics: Dictionary of metrics to serialize
            encoding: How to encode the metrics
            
        Returns:
            Serialized metrics as a string
        """
        if encoding == ArtifactEncoding.JSON:
            return json.dumps(metrics, indent=2, default=str)
        elif encoding == ArtifactEncoding.BASE64:
            json_bytes = json.dumps(metrics, default=str).encode('utf-8')
            return base64.b64encode(json_bytes).decode('utf-8')
        else:
            raise ValueError(f"Unsupported encoding for metrics: {encoding}")
    
    @staticmethod
    def deserialize_metrics(data: str, encoding: ArtifactEncoding) -> Dict[str, Any]:
        """Deserialize metrics from encoded data.
        
        Args:
            data: Encoded metrics data
            encoding: Encoding method used
            
        Returns:
            Deserialized metrics dictionary
        """
        if encoding == ArtifactEncoding.JSON:
            return json.loads(data)
        elif encoding == ArtifactEncoding.BASE64:
            json_bytes = base64.b64decode(data.encode('utf-8'))
            json_str = json_bytes.decode('utf-8')
            return json.loads(json_str)
        else:
            raise ValueError(f"Unsupported encoding for metrics: {encoding}")


class ArtifactBridge:
    """Bridge between memory artifacts and filesystem storage.
    
    This class manages the storage and retrieval of artifacts according to
    the configured persistence mode, providing seamless integration between
    memory-only and filesystem-based workflows.
    
    Attributes:
        config: Persistence configuration
        memory_artifacts: In-memory artifact storage
        artifact_metadata: Metadata for stored artifacts
    """
    
    def __init__(self, config: PersistenceConfig):
        """Initialize the artifact bridge.
        
        Args:
            config: Persistence configuration to use
        """
        self.config = config
        self.memory_artifacts: Dict[str, Any] = {}
        self.artifact_metadata: Dict[str, Dict[str, Any]] = {}
        self.resource_registry: Dict[str, Dict[str, Any]] = {}  # URI -> Resource info mapping
        self.serializer = ArtifactSerializer()

        logger.info(f"ArtifactBridge initialized with mode: {config.mode.value}")
    
    def store_artifact(self, key: str, artifact: Any, artifact_type: str, 
                      filesystem_path: Optional[Path] = None) -> Dict[str, Any]:
        """Store artifact according to persistence configuration.
        
        Args:
            key: Unique identifier for the artifact
            artifact: The artifact to store
            artifact_type: Type of artifact (model, dataset, metrics, etc.)
            filesystem_path: Optional filesystem path for FILESYSTEM mode
            
        Returns:
            Dictionary containing artifact reference information
        """
        metadata = {
            "key": key,
            "type": artifact_type,
            "stored_at": datetime.now().isoformat(),
            "size_estimate": self._estimate_size(artifact),
            "encoding": self.config.artifact_encoding.value
        }
        
        result = {"metadata": metadata}
        
        if self.config.should_store_in_memory():
            # Store in memory
            self.memory_artifacts[key] = artifact
            self.artifact_metadata[key] = metadata
            
            if self.config.should_return_artifacts():
                # Serialize for return in tool response
                try:
                    if artifact_type == "model":
                        result["artifact_data"] = self.serializer.serialize_model(
                            artifact, self.config.artifact_encoding
                        )
                    elif artifact_type == "dataset":
                        result["artifact_data"] = self.serializer.serialize_dataset(
                            artifact, self.config.artifact_encoding
                        )
                    elif artifact_type == "metrics":
                        result["artifact_data"] = self.serializer.serialize_metrics(
                            artifact, self.config.artifact_encoding
                        )
                    
                    result["memory_reference"] = f"memory://{key}"
                    
                except Exception as e:
                    logger.warning(f"Failed to serialize artifact {key}: {e}")
                    result["serialization_error"] = str(e)
        
        if self.config.should_save_to_filesystem():
            # Auto-generate filesystem path if not provided
            if filesystem_path is None:
                # Use project-relative paths with temp fallback
                try:
                    from mcp_ds_toolkit_server.utils.config import Settings
                    settings = Settings()
                    
                    if artifact_type == "model":
                        workspace_artifacts_dir = settings.models_dir
                        filesystem_path = workspace_artifacts_dir / f"{key}_model.pkl"
                    elif artifact_type == "dataset":
                        workspace_artifacts_dir = settings.data_dir
                        filesystem_path = workspace_artifacts_dir / f"{key}_dataset.csv"
                    elif artifact_type == "metrics":
                        workspace_artifacts_dir = settings.experiments_dir / "metrics"
                        filesystem_path = workspace_artifacts_dir / f"{key}_metrics.json"
                    else:
                        workspace_artifacts_dir = settings.workspace_path
                        filesystem_path = workspace_artifacts_dir / f"{key}.pkl"
                    
                    # Ensure directory exists
                    workspace_artifacts_dir.mkdir(parents=True, exist_ok=True)
                    
                except Exception as e:
                    # Fallback to temp directory if config fails
                    logger.warning(f"Failed to use project paths, falling back to temp: {e}")
                    workspace_artifacts_dir = Path(tempfile.gettempdir()) / "mcp_mlops_artifacts"
                    workspace_artifacts_dir.mkdir(exist_ok=True)
                    
                    if artifact_type == "model":
                        filesystem_path = workspace_artifacts_dir / f"{key}_model.pkl"
                    elif artifact_type == "dataset":
                        filesystem_path = workspace_artifacts_dir / f"{key}_dataset.csv"
                    elif artifact_type == "metrics":
                        filesystem_path = workspace_artifacts_dir / f"{key}_metrics.json"
                    else:
                        filesystem_path = workspace_artifacts_dir / f"{key}.pkl"
            # Save to filesystem
            try:
                filesystem_path.parent.mkdir(parents=True, exist_ok=True)
                
                if artifact_type == "model":
                    with open(filesystem_path, "wb") as f:
                        pickle.dump(artifact, f)
                elif artifact_type == "dataset":
                    artifact.to_csv(filesystem_path, index=False)
                elif artifact_type == "metrics":
                    with open(filesystem_path, "w") as f:
                        json.dump(artifact, f, indent=2, default=str)
                
                result["filesystem_reference"] = f"file://{filesystem_path}"
                metadata["filesystem_path"] = str(filesystem_path)
                
                logger.info(f"Artifact {key} saved to {filesystem_path}")
                
            except Exception as e:
                logger.error(f"Failed to save artifact {key} to filesystem: {e}")
                if not self.config.should_store_in_memory():
                    # If filesystem-only mode fails, try memory as fallback
                    if self.config.filesystem_fallback:
                        logger.warning(f"Falling back to memory storage for {key}")
                        self.memory_artifacts[key] = artifact
                        result["fallback_to_memory"] = True
                    else:
                        result["filesystem_error"] = str(e)
        
        return result
    
    def retrieve_artifact(self, key: str) -> Optional[Any]:
        """Retrieve artifact by key.
        
        Args:
            key: Unique identifier for the artifact
            
        Returns:
            The stored artifact, or None if not found
        """
        # First try memory cache
        if key in self.memory_artifacts:
            return self.memory_artifacts[key]
        
        # Try filesystem retrieval for hybrid/filesystem modes
        if key in self.artifact_metadata:
            metadata = self.artifact_metadata[key]
            filesystem_path = metadata.get("filesystem_path")
            artifact_type = metadata.get("type")
            
            if filesystem_path and Path(filesystem_path).exists():
                try:
                    if artifact_type == "model":
                        with open(filesystem_path, "rb") as f:
                            artifact = pickle.load(f)
                            # Cache in memory if hybrid mode
                            if self.config.should_store_in_memory():
                                self.memory_artifacts[key] = artifact
                            return artifact
                    elif artifact_type == "dataset":
                        if filesystem_path.endswith('.pkl'):
                            with open(filesystem_path, "rb") as f:
                                artifact = pickle.load(f)
                        elif filesystem_path.endswith('.parquet'):
                            artifact = pd.read_parquet(filesystem_path)
                        else:
                            # Fallback to CSV
                            artifact = pd.read_csv(filesystem_path)
                        # Cache in memory if hybrid mode
                        if self.config.should_store_in_memory():
                            self.memory_artifacts[key] = artifact
                        return artifact
                    elif artifact_type == "metrics":
                        with open(filesystem_path, "r") as f:
                            artifact = json.load(f)
                            # Cache in memory if hybrid mode
                            if self.config.should_store_in_memory():
                                self.memory_artifacts[key] = artifact
                            return artifact
                except Exception as e:
                    logger.warning(f"Failed to load artifact {key} from filesystem: {e}")
        
        return None
    
    def list_artifacts(self) -> Dict[str, Dict[str, Any]]:
        """List all stored artifacts with their metadata.
        
        Returns:
            Dictionary mapping artifact keys to their metadata
        """
        return self.artifact_metadata.copy()
    
    def export_session_to_filesystem(self, output_dir: Path, 
                                    include_types: Optional[List[str]] = None) -> Dict[str, Any]:
        """Export entire in-memory session to filesystem.
        
        Args:
            output_dir: Directory to export artifacts to
            include_types: Optional list of artifact types to include
            
        Returns:
            Export manifest with details of exported artifacts
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        manifest = {
            "export_timestamp": datetime.now().isoformat(),
            "source_session_id": id(self),
            "artifacts": [],
            "config": asdict(self.config)
        }
        
        exported_count = 0
        
        for key, artifact in self.memory_artifacts.items():
            metadata = self.artifact_metadata.get(key, {})
            artifact_type = metadata.get("type", "unknown")
            
            # Filter by type if specified
            if include_types and artifact_type not in include_types:
                continue
            
            try:
                # Determine output filename
                if artifact_type == "model":
                    output_file = output_dir / f"{key}_model.pkl"
                    with open(output_file, "wb") as f:
                        pickle.dump(artifact, f)
                elif artifact_type == "dataset":
                    output_file = output_dir / f"{key}_dataset.csv"
                    artifact.to_csv(output_file, index=False)
                elif artifact_type == "metrics":
                    output_file = output_dir / f"{key}_metrics.json"
                    with open(output_file, "w") as f:
                        json.dump(artifact, f, indent=2, default=str)
                else:
                    # Generic artifact - try JSON serialization
                    output_file = output_dir / f"{key}_{artifact_type}.json"
                    with open(output_file, "w") as f:
                        json.dump(artifact, f, indent=2, default=str)
                
                artifact_info = {
                    "key": key,
                    "type": artifact_type,
                    "original_metadata": metadata,
                    "exported_path": str(output_file),
                    "exported_size_bytes": output_file.stat().st_size
                }
                
                manifest["artifacts"].append(artifact_info)
                exported_count += 1
                
                logger.info(f"Exported artifact {key} to {output_file}")
                
            except Exception as e:
                logger.error(f"Failed to export artifact {key}: {e}")
                manifest["artifacts"].append({
                    "key": key,
                    "type": artifact_type,
                    "export_error": str(e)
                })
        
        # Save export manifest
        manifest_path = output_dir / "session_export_manifest.json"
        with open(manifest_path, "w") as f:
            json.dump(manifest, f, indent=2)
        
        manifest["export_summary"] = {
            "total_artifacts": len(self.memory_artifacts),
            "exported_successfully": exported_count,
            "export_directory": str(output_dir),
            "manifest_path": str(manifest_path)
        }
        
        logger.info(f"Session export completed: {exported_count} artifacts exported to {output_dir}")
        
        return manifest
    
    def _estimate_size(self, artifact: Any) -> int:
        """Estimate the memory size of an artifact in bytes.
        
        Args:
            artifact: The artifact to estimate
            
        Returns:
            Estimated size in bytes
        """
        try:
            if isinstance(artifact, pd.DataFrame):
                return artifact.memory_usage(deep=True).sum()
            elif hasattr(artifact, '__sizeof__'):
                return artifact.__sizeof__()
            else:
                # Fallback: pickle size as rough estimate
                return len(pickle.dumps(artifact))
        except Exception:
            # If estimation fails, return 0
            return 0

    def register_resource(self, artifact_key: str, name: str, mime_type: str,
                         description: Optional[str] = None) -> str:
        """Register an artifact as an MCP Resource.

        Args:
            artifact_key: Key of the stored artifact
            name: Human-readable name for the resource
            mime_type: MIME type of the resource (e.g., 'text/csv', 'image/png')
            description: Optional description of the resource

        Returns:
            str: Generated URI for the resource

        Raises:
            KeyError: If artifact_key is not found in stored artifacts
        """
        if artifact_key not in self.artifact_metadata:
            raise KeyError(f"Artifact '{artifact_key}' not found in storage")

        # Generate URI using ds-toolkit scheme
        uri = f"ds-toolkit://artifacts/{artifact_key}"

        # Store resource information
        self.resource_registry[uri] = {
            "uri": uri,
            "name": name,
            "description": description or f"Artifact: {name}",
            "mime_type": mime_type,
            "artifact_key": artifact_key,
            "registered_at": datetime.now().isoformat()
        }

        logger.debug(f"Registered resource: {uri} -> {artifact_key}")
        return uri

    def get_all_resources(self) -> List[Dict[str, str]]:
        """Get all registered resources for MCP list_resources.

        Returns:
            List of resource dictionaries with uri, name, description, mime_type
        """
        return [
            {
                "uri": resource_info["uri"],
                "name": resource_info["name"],
                "description": resource_info["description"],
                "mimeType": resource_info["mime_type"]
            }
            for resource_info in self.resource_registry.values()
        ]

    def get_resource_content(self, uri: str) -> bytes:
        """Get the content of a resource by URI.

        Args:
            uri: URI of the resource to retrieve

        Returns:
            bytes: Content of the resource

        Raises:
            KeyError: If URI is not found in resource registry
            ValueError: If artifact content cannot be retrieved
        """
        if uri not in self.resource_registry:
            raise KeyError(f"Resource URI '{uri}' not found")

        resource_info = self.resource_registry[uri]
        artifact_key = resource_info["artifact_key"]

        # Get the artifact content
        artifact_data = self.get_artifact(artifact_key)
        if artifact_data is None:
            raise ValueError(f"Artifact data for '{artifact_key}' not found")

        # Convert to bytes based on artifact type
        if isinstance(artifact_data, bytes):
            return artifact_data
        elif isinstance(artifact_data, str):
            return artifact_data.encode('utf-8')
        elif isinstance(artifact_data, pd.DataFrame):
            # Convert DataFrame to CSV bytes
            return artifact_data.to_csv(index=False).encode('utf-8')
        else:
            # Try to serialize as JSON
            import json
            return json.dumps(artifact_data, default=str).encode('utf-8')


def create_default_persistence_config(mode: str = "memory_only") -> PersistenceConfig:
    """Create a default persistence configuration.
    
    Args:
        mode: Persistence mode string (memory_only, filesystem, hybrid)
        
    Returns:
        PersistenceConfig instance with sensible defaults
        
    Raises:
        ValueError: If mode is invalid
    """
    try:
        persistence_mode = PersistenceMode(mode)
    except ValueError:
        raise ValueError(f"Invalid persistence mode: {mode}. Valid modes: {[m.value for m in PersistenceMode]}")
    
    return PersistenceConfig(
        mode=persistence_mode,
        export_artifacts=True,
        artifact_encoding=ArtifactEncoding.BASE64,
        filesystem_fallback=True,
        max_memory_size_mb=100,
        compress_artifacts=False  # Disable by default for simplicity
    )