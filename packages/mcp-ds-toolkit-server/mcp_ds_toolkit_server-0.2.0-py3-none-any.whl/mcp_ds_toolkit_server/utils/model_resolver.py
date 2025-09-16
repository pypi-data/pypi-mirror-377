"""
Unified Model Resolution System for MCP MLOps Server

This module provides intelligent model discovery and resolution across
different persistence modes, enabling deployment tools to seamlessly 
access trained models regardless of storage location.
"""

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Union, Tuple

from sklearn.base import BaseEstimator

from mcp_ds_toolkit_server.utils.persistence import ArtifactBridge, PersistenceMode
from mcp_ds_toolkit_server.exceptions import DataError

# Local storage only - no external registry dependencies

logger = logging.getLogger(__name__)


@dataclass
class ModelReference:
    """Reference to a trained model with location and metadata information."""
    
    name: str
    location_type: str  # "artifact_bridge", "filesystem"
    persistence_mode: Optional[PersistenceMode] = None
    artifact_key: Optional[str] = None
    file_path: Optional[Path] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class UnifiedModelResolver:
    """
    Unified model resolver that intelligently discovers and loads trained models
    from multiple sources with priority-based fallback logic.
    """
    
    def __init__(
        self,
        artifact_bridge: ArtifactBridge
    ):
        """Initialize the unified model resolver.

        Args:
            artifact_bridge: Artifact bridge for persistence operations
        """
        self.artifact_bridge = artifact_bridge
        self.logger = logging.getLogger(__name__)
    
    def resolve_model(
        self, 
        model_name: Optional[str] = None,
        model_path: Optional[str] = None,
        artifact_key: Optional[str] = None,
        auto_fallback: bool = True
    ) -> Tuple[BaseEstimator, ModelReference]:
        """
        Resolve trained model from multiple sources with intelligent fallback.
        
        Priority order:
        1. Explicit artifact_key in artifact bridge
        2. model_name as artifact_key in artifact bridge
        3. model_path from filesystem
        4. Auto-generated variations and fallbacks
        
        Args:
            model_name: Name of the model
            model_path: Path to model file
            artifact_key: Explicit artifact key
            auto_fallback: Enable automatic fallback strategies
            
        Returns:
            Tuple of (Model, ModelReference with metadata)
            
        Raises:
            DataError: If model cannot be resolved from any source
        """
        resolution_attempts = []
        
        # Strategy 1: Explicit artifact key
        if artifact_key:
            try:
                model = self.artifact_bridge.retrieve_artifact(artifact_key)
                if model is not None and isinstance(model, BaseEstimator):
                    reference = ModelReference(
                        name=artifact_key,
                        location_type="artifact_bridge",
                        persistence_mode=self.artifact_bridge.config.mode,
                        artifact_key=artifact_key,
                        metadata=self.artifact_bridge.artifact_metadata.get(artifact_key, {})
                    )
                    self.logger.info(f"✅ Resolved model via artifact_key: {artifact_key}")
                    return model, reference
                resolution_attempts.append(f"❌ Artifact key '{artifact_key}' not found or not a model")
            except Exception as e:
                resolution_attempts.append(f"❌ Artifact key '{artifact_key}' error: {e}")
        
        # Strategy 2: Model name as artifact key
        if model_name:
            try:
                model = self.artifact_bridge.retrieve_artifact(model_name)
                if model is not None and isinstance(model, BaseEstimator):
                    reference = ModelReference(
                        name=model_name,
                        location_type="artifact_bridge",
                        persistence_mode=self.artifact_bridge.config.mode,
                        artifact_key=model_name,
                        metadata=self.artifact_bridge.artifact_metadata.get(model_name, {})
                    )
                    self.logger.info(f"✅ Resolved model via model_name as artifact: {model_name}")
                    return model, reference
                resolution_attempts.append(f"❌ Model name '{model_name}' not found as artifact")
            except Exception as e:
                resolution_attempts.append(f"❌ Model name as artifact '{model_name}' error: {e}")
        
        # Strategy 3: Filesystem path
        if model_path:
            try:
                file_path = Path(model_path)
                if file_path.exists():
                    import pickle
                    with open(file_path, 'rb') as f:
                        model = pickle.load(f)
                    
                    if isinstance(model, BaseEstimator):
                        reference = ModelReference(
                            name=file_path.stem,
                            location_type="filesystem",
                            persistence_mode=PersistenceMode.FILESYSTEM,
                            file_path=file_path,
                            metadata={"file_size": file_path.stat().st_size}
                        )
                        self.logger.info(f"✅ Resolved model from filesystem: {model_path}")
                        return model, reference
                    else:
                        resolution_attempts.append(f"❌ File '{model_path}' is not a valid model")
                else:
                    resolution_attempts.append(f"❌ File path '{model_path}' does not exist")
            except Exception as e:
                resolution_attempts.append(f"❌ Filesystem path '{model_path}' error: {e}")
        
        # Strategy 4: Auto-fallback variations (if enabled)
        if auto_fallback and model_name:
            # Try common model naming patterns
            variations = [
                f"{model_name}_model",
                f"model_{model_name}",
                f"{model_name}_trained",
                f"trained_{model_name}",
            ]
            
            # Also try with common algorithm suffixes and reverse lookup
            algorithms = ["random_forest", "gradient_boosting", "logistic_regression", "svm"]
            if "_" not in model_name:
                for algo in algorithms:
                    variations.extend([
                        f"{model_name}_{algo}",
                        f"{algo}_{model_name}",
                    ])
            
            # Try reverse lookup: find artifacts that might correspond to this output_name
            # For example: rf_model -> look for random_forest_* artifacts
            algorithm_mappings = {
                "rf_model": "random_forest",
                "svm_model": "svm", 
                "lr_model": "logistic_regression",
                "gb_model": "gradient_boosting",
                "xgb_model": "xgboost"
            }
            
            if model_name in algorithm_mappings:
                target_algo = algorithm_mappings[model_name]
                # Find all artifacts that start with this algorithm
                for key in self.artifact_bridge.list_artifacts().keys():
                    if key.startswith(target_algo) and "model" in key:
                        variations.append(key)
            
            for variation in variations:
                try:
                    model = self.artifact_bridge.retrieve_artifact(variation)
                    if model is not None and isinstance(model, BaseEstimator):
                        reference = ModelReference(
                            name=variation,
                            location_type="artifact_bridge",
                            persistence_mode=self.artifact_bridge.config.mode,
                            artifact_key=variation,
                            metadata={
                                **self.artifact_bridge.artifact_metadata.get(variation, {}),
                                "variation_of": model_name
                            }
                        )
                        self.logger.info(f"✅ Resolved model via variation: {variation}")
                        return model, reference
                        
                except Exception:
                    continue  # Silent fail for variations
        
        # Failed to resolve
        available_models = []
        for key, metadata in self.artifact_bridge.list_artifacts().items():
            if metadata.get("type") == "model":
                available_models.append(key)
        
        error_msg = f"Failed to resolve model with the following attempts:\n"
        error_msg += "\n".join(resolution_attempts)
        error_msg += f"\n\nAvailable models in artifacts: {available_models}"
        
        raise DataError(error_msg)
    
    def list_available_models(self) -> List[ModelReference]:
        """List all available models across all sources.
        
        Returns:
            List of ModelReference objects for all available models
        """
        available = []
        
        # Artifact bridge models
        for key, metadata in self.artifact_bridge.list_artifacts().items():
            if metadata.get("type") == "model":
                available.append(ModelReference(
                    name=key,
                    location_type="artifact_bridge",
                    persistence_mode=self.artifact_bridge.config.mode,
                    artifact_key=key,
                    metadata=metadata
                ))
        
        
        return available
    
    def get_model_info(self, model_reference: ModelReference) -> Dict[str, Any]:
        """Get detailed information about a model reference.
        
        Args:
            model_reference: Reference to get info for
            
        Returns:
            Dictionary with detailed information
        """
        info = {
            "name": model_reference.name,
            "location_type": model_reference.location_type,
            "persistence_mode": model_reference.persistence_mode.value if model_reference.persistence_mode else None,
            "metadata": model_reference.metadata
        }
        
        if model_reference.artifact_key:
            info["artifact_key"] = model_reference.artifact_key
        if model_reference.file_path:
            info["file_path"] = str(model_reference.file_path)
            
        return info


# Convenience function for quick model resolution
def resolve_model_smart(
    model_name: Optional[str] = None,
    model_path: Optional[str] = None,
    artifact_bridge: Optional[ArtifactBridge] = None
) -> Tuple[BaseEstimator, ModelReference]:
    """
    Smart model resolution with automatic fallback.
    
    This is a convenience function that creates a temporary resolver
    and performs model resolution.
    """
    if artifact_bridge is None:
        from mcp_ds_toolkit_server.utils.persistence import create_default_persistence_config, ArtifactBridge
        artifact_bridge = ArtifactBridge(create_default_persistence_config("memory_only"))
    
    resolver = UnifiedModelResolver(artifact_bridge=artifact_bridge)
    
    return resolver.resolve_model(
        model_name=model_name,
        model_path=model_path,
        auto_fallback=True
    )