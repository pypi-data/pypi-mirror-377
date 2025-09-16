"""Tests for the main MCP server."""

from unittest.mock import Mock, patch

import pytest

from mcp_ds_toolkit_server.server import MCPDataScienceServer, mcp_server
from mcp_ds_toolkit_server.utils.config import Settings


@pytest.fixture(scope="module", autouse=True)
def initialize_global_server():
    """Initialize the global server instance for testing."""
    import mcp_ds_toolkit_server.server as server_module
    if server_module.mcp_server is None:
        server_module.mcp_server = MCPDataScienceServer()
    yield
    # Cleanup after tests
    server_module.mcp_server = None


class TestMCPDataScienceServer:
    """Test cases for the MCPDataScienceServer class."""

    def test_server_initialization(self):
        """Test that the server initializes correctly."""
        server = MCPDataScienceServer()

        assert server.settings is not None
        assert server.server is not None
        assert server.logger is not None
        assert isinstance(server.tool_handlers, dict)
        # Server initializes with data management tools already registered
        assert len(server.tool_handlers) > 0

    def test_register_tool_handler(self):
        """Test registering a tool handler."""
        server = MCPDataScienceServer()

        def dummy_handler(args):
            return "test result"

        server.register_tool_handler("test_tool", dummy_handler)

        assert "test_tool" in server.tool_handlers
        assert server.tool_handlers["test_tool"] == dummy_handler

    def test_global_server_instance(self):
        """Test that the global server instance is available."""
        import mcp_ds_toolkit_server.server as server_module
        assert server_module.mcp_server is not None
        assert isinstance(server_module.mcp_server, MCPDataScienceServer)


class TestServerConfiguration:
    """Test cases for server configuration."""

    def test_settings_initialization(self):
        """Test that settings initialize with correct defaults."""
        settings = Settings()

        assert settings.app_name == "mcp-mlops-server"
        assert settings.app_version == "0.1.0"
        assert settings.default_random_state == 42
        assert settings.default_test_size == 0.2
        assert settings.default_cv_folds == 5

    def test_settings_with_env_vars(self):
        """Test that settings can be overridden with environment variables."""
        with patch.dict("os.environ", {"DEBUG": "true", "LOG_LEVEL": "DEBUG"}):
            settings = Settings()

            assert settings.debug is True
            assert settings.log_level == "DEBUG"


@pytest.mark.asyncio
class TestServerEndpoints:
    """Test cases for server endpoints."""

    async def test_list_prompts(self):
        """Test the list_prompts endpoint."""
        from mcp_ds_toolkit_server.server import list_prompts

        prompts = await list_prompts()

        assert isinstance(prompts, list)
        assert len(prompts) >= 2

        # Check that required prompts are present
        prompt_names = [p.name for p in prompts]
        assert "ml_workflow_guide" in prompt_names
        assert "model_comparison" in prompt_names

    async def test_list_tools_empty(self):
        """Test the list_tools endpoint returns data management tools."""
        from mcp_ds_toolkit_server.server import list_tools

        tools = await list_tools()

        assert isinstance(tools, list)
        # Server has data management tools registered by default
        assert len(tools) > 0

    async def test_list_resources_empty(self):
        """Test the list_resources endpoint returns empty list initially."""
        from mcp_ds_toolkit_server.server import list_resources

        resources = await list_resources()

        assert isinstance(resources, list)
        assert len(resources) == 0

    async def test_call_tool_not_found(self):
        """Test calling a non-existent tool raises ValueError."""
        from mcp_ds_toolkit_server.server import call_tool

        with pytest.raises(ValueError, match="Tool nonexistent_tool not found"):
            await call_tool("nonexistent_tool", {})

    async def test_read_resource_not_found(self):
        """Test reading a non-existent resource raises ValueError."""
        from mcp_ds_toolkit_server.server import read_resource

        with pytest.raises(ValueError, match="Resource test://resource not found"):
            await read_resource("test://resource")
