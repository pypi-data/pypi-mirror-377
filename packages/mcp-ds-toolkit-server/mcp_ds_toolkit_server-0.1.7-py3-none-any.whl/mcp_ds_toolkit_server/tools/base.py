"""Base Tool Infrastructure Module

This module provides foundational base classes for all MCP (Model Context Protocol)
tool implementations with common initialization, error handling, and logging.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, List, Optional
import json
import numpy as np

from mcp.types import EmbeddedResource, ImageContent, TextContent, Tool

from mcp_ds_toolkit_server.utils.config import Settings
from mcp_ds_toolkit_server.utils.logger import make_logger
from mcp_ds_toolkit_server.utils.persistence import ArtifactBridge, create_default_persistence_config


class NumpyJSONEncoder(json.JSONEncoder):
    """Custom JSON encoder that handles numpy types and Path objects."""
    
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, (np.bool_, bool)):
            return bool(obj)
        elif isinstance(obj, Path):
            return str(obj)
        return super().default(obj)


class BaseMCPTools(ABC):
    """
    Base class for all MCP tool classes.
    
    Provides common initialization patterns, error handling, and utilities
    to eliminate code duplication across tool implementations.
    """
    
    def __init__(
        self, 
        workspace_path: Path, 
        persistence_mode: str = "memory_only",
        artifact_bridge: Optional[ArtifactBridge] = None
    ):
        """Initialize base MCP tools with common setup.
        
        Args:
            workspace_path: Path to the workspace directory
            persistence_mode: Persistence mode for artifact bridge ("memory_only", "hybrid", "filesystem")
            artifact_bridge: Optional pre-configured artifact bridge
        """
        self.workspace_path = Path(workspace_path)
        self.workspace_path.mkdir(exist_ok=True)
        
        # Initialize settings and logger consistently
        self.settings = Settings()
        self.logger = make_logger(self.__class__.__module__)
        
        # Initialize artifact bridge with consistent pattern
        self.artifact_bridge = artifact_bridge or ArtifactBridge(
            create_default_persistence_config(persistence_mode)
        )
        
    
    def _create_json_response(self, data: Dict[str, Any]) -> List[TextContent]:
        """Create standardized JSON response for MCP tools.
        
        This ensures all tools return clean, parseable JSON without emojis,
        markdown formatting, or human-readable instructions that break parsing.
        
        Args:
            data: Dictionary containing the response data
            
        Returns:
            List containing JSON text content
        """
        try:
            # Ensure clean JSON serialization with numpy type support
            json_response = json.dumps(
                data, 
                indent=None, 
                ensure_ascii=True, 
                separators=(',', ':'),
                cls=NumpyJSONEncoder
            )
            return [TextContent(type="text", text=json_response)]
        except Exception as e:
            self.logger.error(f"JSON serialization failed: {e}")
            # Fallback error response - still valid JSON
            error_data = {
                "status": "error", 
                "message": f"JSON serialization failed: {str(e)}"
            }
            json_response = json.dumps(error_data)
            return [TextContent(type="text", text=json_response)]
    
    def _handle_tool_error(self, tool_name: str, error: Exception) -> List[TextContent]:
        """Standardized error handling for tool calls.
        
        Args:
            tool_name: Name of the tool that failed
            error: The exception that occurred
            
        Returns:
            List containing JSON error response
        """
        self.logger.error(f"Tool call error - {tool_name}: {error}")
        
        error_data = {
            "status": "error",
            "tool": tool_name,
            "message": str(error)
        }
        
        return self._create_json_response(error_data)
    
    @abstractmethod
    def get_tools(self) -> List[Tool]:
        """Get list of available tools for this tool class.
        
        Returns:
            List of MCP Tool instances
        """
        pass
    
    @abstractmethod 
    async def handle_tool_call(
        self, tool_name: str, arguments: Dict[str, Any]
    ) -> List[TextContent | ImageContent | EmbeddedResource]:
        """Handle MCP tool calls.
        
        Args:
            tool_name: Name of the tool to execute
            arguments: Tool arguments from MCP client
            
        Returns:
            List of content items with results
        """
        pass