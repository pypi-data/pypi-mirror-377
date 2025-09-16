"""
Unified Data Resolution System for MCP MLOps Server

This module provides intelligent data discovery and resolution across
different persistence modes, enabling tools to seamlessly access data
regardless of storage location.
"""

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Union, Tuple

import pandas as pd

from mcp_ds_toolkit_server.utils.persistence import ArtifactBridge, PersistenceMode
from mcp_ds_toolkit_server.data import DatasetLoader
from mcp_ds_toolkit_server.exceptions import DataError

# Local storage only - no external versioning dependencies

logger = logging.getLogger(__name__)


@dataclass
class DataReference:
    """Reference to data with location and metadata information."""
    
    name: str
    location_type: str  # "memory", "filesystem", "artifact_bridge"
    persistence_mode: Optional[PersistenceMode] = None
    artifact_key: Optional[str] = None
    file_path: Optional[Path] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class UnifiedDataResolver:
    """
    Unified data resolver that intelligently discovers and loads data
    from multiple sources with priority-based fallback logic.
    """
    
    def __init__(
        self,
        memory_registry: Dict[str, pd.DataFrame],
        artifact_bridge: ArtifactBridge,
        data_loader: Optional[DatasetLoader] = None
    ):
        """Initialize the unified data resolver.

        Args:
            memory_registry: In-memory dataset registry
            artifact_bridge: Artifact bridge for persistence operations
            data_loader: Dataset loader for filesystem operations
        """
        self.memory_registry = memory_registry
        self.artifact_bridge = artifact_bridge
        self.data_loader = data_loader or DatasetLoader()
        self.logger = logging.getLogger(__name__)
    
    def resolve_data(
        self, 
        dataset_name: Optional[str] = None,
        dataset_path: Optional[str] = None,
        artifact_key: Optional[str] = None,
        auto_fallback: bool = True
    ) -> Tuple[pd.DataFrame, DataReference]:
        """
        Resolve data from multiple sources with intelligent fallback.
        
        Priority order:
        1. Explicit artifact_key in artifact bridge
        2. dataset_name in memory registry
        3. dataset_name as artifact_key in artifact bridge
        4. dataset_path from filesystem
        5. Auto-generated variations and fallbacks
        
        Args:
            dataset_name: Name of the dataset
            dataset_path: Path to dataset file
            artifact_key: Explicit artifact key
            auto_fallback: Enable automatic fallback strategies
            
        Returns:
            Tuple of (DataFrame, DataReference with metadata)
            
        Raises:
            DataError: If data cannot be resolved from any source
        """
        resolution_attempts = []
        
        # Strategy 1: Explicit artifact key
        if artifact_key:
            try:
                data = self.artifact_bridge.retrieve_artifact(artifact_key)
                if data is not None and isinstance(data, pd.DataFrame):
                    reference = DataReference(
                        name=artifact_key,
                        location_type="artifact_bridge",
                        persistence_mode=self.artifact_bridge.config.mode,
                        artifact_key=artifact_key,
                        metadata=self.artifact_bridge.artifact_metadata.get(artifact_key, {})
                    )
                    self.logger.info(f"✅ Resolved data via artifact_key: {artifact_key}")
                    return data.copy(), reference
                resolution_attempts.append(f"❌ Artifact key '{artifact_key}' not found")
            except Exception as e:
                resolution_attempts.append(f"❌ Artifact key '{artifact_key}' error: {e}")
        
        # Strategy 2: Memory registry lookup
        if dataset_name and dataset_name in self.memory_registry:
            try:
                data = self.memory_registry[dataset_name]
                reference = DataReference(
                    name=dataset_name,
                    location_type="memory",
                    persistence_mode=PersistenceMode.MEMORY_ONLY,
                    metadata={"shape": data.shape, "columns": list(data.columns)}
                )
                self.logger.info(f"✅ Resolved data from memory registry: {dataset_name}")
                return data.copy(), reference
            except Exception as e:
                resolution_attempts.append(f"❌ Memory registry '{dataset_name}' error: {e}")
        elif dataset_name:
            resolution_attempts.append(f"❌ Dataset '{dataset_name}' not in memory registry")
        
        
        # Strategy 3: Dataset name as artifact key
        if dataset_name and auto_fallback:
            try:
                data = self.artifact_bridge.retrieve_artifact(dataset_name)
                if data is not None and isinstance(data, pd.DataFrame):
                    reference = DataReference(
                        name=dataset_name,
                        location_type="artifact_bridge", 
                        persistence_mode=self.artifact_bridge.config.mode,
                        artifact_key=dataset_name,
                        metadata=self.artifact_bridge.artifact_metadata.get(dataset_name, {})
                    )
                    self.logger.info(f"✅ Resolved data via dataset_name as artifact_key: {dataset_name}")
                    return data.copy(), reference
                resolution_attempts.append(f"❌ Dataset name '{dataset_name}' not found as artifact")
            except Exception as e:
                resolution_attempts.append(f"❌ Dataset name as artifact '{dataset_name}' error: {e}")
        
        # Strategy 4: Filesystem path
        if dataset_path:
            try:
                file_path = Path(dataset_path)
                if file_path.exists():
                    data = self.data_loader.load_dataset(str(file_path))
                    reference = DataReference(
                        name=file_path.stem,
                        location_type="filesystem",
                        persistence_mode=PersistenceMode.FILESYSTEM,
                        file_path=file_path,
                        metadata={"file_size": file_path.stat().st_size, "shape": data.shape}
                    )
                    self.logger.info(f"✅ Resolved data from filesystem: {dataset_path}")
                    return data, reference
                resolution_attempts.append(f"❌ File path '{dataset_path}' does not exist")
            except Exception as e:
                resolution_attempts.append(f"❌ Filesystem path '{dataset_path}' error: {e}")
        
        # Strategy 5: Auto-fallback variations (if enabled)
        if auto_fallback and dataset_name:
            # Try common variations
            variations = [
                f"{dataset_name}_processed",
                f"{dataset_name}_clean", 
                f"{dataset_name}_train",
                f"{dataset_name}_export_csv",
                f"{dataset_name}_export_json"
            ]
            
            for variation in variations:
                try:
                    # Check memory registry
                    if variation in self.memory_registry:
                        data = self.memory_registry[variation]
                        reference = DataReference(
                            name=variation,
                            location_type="memory",
                            persistence_mode=PersistenceMode.MEMORY_ONLY,
                            metadata={"shape": data.shape, "variation_of": dataset_name}
                        )
                        self.logger.info(f"✅ Resolved data via variation in memory: {variation}")
                        return data.copy(), reference
                    
                    # Check artifact bridge
                    data = self.artifact_bridge.retrieve_artifact(variation)
                    if data is not None and isinstance(data, pd.DataFrame):
                        reference = DataReference(
                            name=variation,
                            location_type="artifact_bridge",
                            persistence_mode=self.artifact_bridge.config.mode,
                            artifact_key=variation,
                            metadata={
                                **self.artifact_bridge.artifact_metadata.get(variation, {}),
                                "variation_of": dataset_name
                            }
                        )
                        self.logger.info(f"✅ Resolved data via variation in artifacts: {variation}")
                        return data.copy(), reference
                        
                except Exception:
                    continue  # Silent fail for variations
        
        # Failed to resolve
        available_memory = list(self.memory_registry.keys())
        available_artifacts = list(self.artifact_bridge.list_artifacts().keys())
        
        error_msg = f"Failed to resolve data with the following attempts:\n"
        error_msg += "\n".join(resolution_attempts)
        error_msg += f"\n\nAvailable in memory: {available_memory}"
        error_msg += f"\nAvailable in artifacts: {available_artifacts}"
        
        raise DataError(error_msg)
    
    def list_available_data(self) -> Dict[str, List[DataReference]]:
        """List all available data across all sources.
        
        Returns:
            Dictionary mapping source types to lists of DataReference objects
        """
        available = {
            "memory": [],
            "artifact_bridge": [],
            "filesystem": []
        }
        
        # Memory registry
        for name, data in self.memory_registry.items():
            available["memory"].append(DataReference(
                name=name,
                location_type="memory",
                persistence_mode=PersistenceMode.MEMORY_ONLY,
                metadata={"shape": data.shape, "columns": list(data.columns)}
            ))
        
        # Artifact bridge
        for key, metadata in self.artifact_bridge.list_artifacts().items():
            if metadata.get("type") == "dataset":
                available["artifact_bridge"].append(DataReference(
                    name=key,
                    location_type="artifact_bridge",
                    persistence_mode=self.artifact_bridge.config.mode,
                    artifact_key=key,
                    metadata=metadata
                ))
        
        
        return available
    
    def get_data_info(self, data_reference: DataReference) -> Dict[str, Any]:
        """Get detailed information about a data reference.
        
        Args:
            data_reference: Reference to get info for
            
        Returns:
            Dictionary with detailed information
        """
        info = {
            "name": data_reference.name,
            "location_type": data_reference.location_type,
            "persistence_mode": data_reference.persistence_mode.value if data_reference.persistence_mode else None,
            "metadata": data_reference.metadata
        }
        
        if data_reference.artifact_key:
            info["artifact_key"] = data_reference.artifact_key
        if data_reference.file_path:
            info["file_path"] = str(data_reference.file_path)
            
        return info


# Convenience functions for common use cases
def resolve_dataset_smart(
    dataset_name: Optional[str] = None,
    dataset_path: Optional[str] = None,
    memory_registry: Optional[Dict[str, pd.DataFrame]] = None,
    artifact_bridge: Optional[ArtifactBridge] = None,
    data_loader: Optional[DatasetLoader] = None
) -> Tuple[pd.DataFrame, DataReference]:
    """
    Smart dataset resolution with automatic fallback.
    
    This is a convenience function that creates a temporary resolver
    and performs data resolution.
    """
    if memory_registry is None:
        memory_registry = {}
    
    if artifact_bridge is None:
        from mcp_ds_toolkit_server.utils.persistence import create_default_persistence_config, ArtifactBridge
        artifact_bridge = ArtifactBridge(create_default_persistence_config("memory_only"))
    
    resolver = UnifiedDataResolver(
        memory_registry=memory_registry,
        artifact_bridge=artifact_bridge,
        data_loader=data_loader
    )
    
    return resolver.resolve_data(
        dataset_name=dataset_name,
        dataset_path=dataset_path,
        auto_fallback=True
    )