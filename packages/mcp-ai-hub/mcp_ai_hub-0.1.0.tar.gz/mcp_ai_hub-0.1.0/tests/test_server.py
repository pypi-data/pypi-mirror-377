"""Integration tests for MCP server."""

from unittest.mock import MagicMock, patch

import pytest

from mcp_ai_hub.config import AIHubConfig, ModelConfig
from mcp_ai_hub.server import create_mcp_server, initialize_client


class TestMCPIntegration:
    """Test MCP server integration."""

    def setup_method(self):
        """Set up test fixtures."""
        self.config = AIHubConfig(
            model_list=[
                ModelConfig(
                    model_name="gpt-4",
                    litellm_params={
                        "model": "openai/gpt-4",
                        "api_key": "test-key",
                        "max_tokens": 2048,
                        "temperature": 0.7,
                    },
                ),
                ModelConfig(
                    model_name="claude-sonnet",
                    litellm_params={
                        "model": "anthropic/claude-3-5-sonnet-20241022",
                        "api_key": "test-key",
                    },
                ),
            ]
        )

    @pytest.mark.asyncio
    async def test_create_mcp_server(self):
        """Test creating MCP server instance."""
        mcp = create_mcp_server()
        assert mcp.name == "ai-hub"
        tools = await mcp.list_tools()
        assert len(tools) == 3  # chat, list_models, get_model_info

    async def get_tool_by_name(self, mcp, tool_name: str):
        """Helper method to get a tool by name from the MCP server."""
        tools = await mcp.list_tools()
        for tool in tools:
            if tool.name == tool_name:
                return tool
        return None

    @pytest.mark.asyncio
    async def test_chat_tool_success(self):
        """Test chat tool with successful response."""
        mcp = create_mcp_server()

        # Mock the AI client
        mock_client = MagicMock()
        mock_client.chat = MagicMock(return_value="Test response")

        # Import the server module to patch the global variable
        import mcp_ai_hub.server as server_module

        with patch.object(server_module, "ai_client", mock_client):
            # Call the chat tool using call_tool method
            result = await mcp.call_tool("chat", {"model": "gpt-4", "inputs": "Hello!"})

            # The result should be a tuple of (content, metadata)
            content, metadata = result
            assert len(content) == 1
            assert content[0].text == "Test response"
            mock_client.chat.assert_called_once_with("gpt-4", "Hello!")

    @pytest.mark.asyncio
    async def test_chat_tool_not_initialized(self):
        """Test chat tool when AI client is not initialized."""
        mcp = create_mcp_server()

        # Import the server module to patch the global variable
        import mcp_ai_hub.server as server_module

        with patch.object(server_module, "ai_client", None):
            # Call the chat tool should raise error (wrapped in ToolError)
            with pytest.raises(Exception) as exc_info:
                await mcp.call_tool("chat", {"model": "gpt-4", "inputs": "Hello!"})
            assert "AI client not initialized" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_list_models_tool(self):
        """Test list_models tool."""
        mcp = create_mcp_server()

        # Mock the AI client
        mock_client = MagicMock()
        mock_client.list_models = MagicMock(return_value=["gpt-4", "claude-sonnet"])

        # Import the server module to patch the global variable
        import mcp_ai_hub.server as server_module

        with patch.object(server_module, "ai_client", mock_client):
            # Call the list_models tool
            result = await mcp.call_tool("list_models", {})

            # The result should be a tuple of (content, metadata)
            content, metadata = result
            # MCP framework converts list items to separate TextContent objects
            assert len(content) == 2
            model_names = [item.text for item in content]
            assert "gpt-4" in model_names
            assert "claude-sonnet" in model_names
            mock_client.list_models.assert_called_once()

    @pytest.mark.asyncio
    async def test_list_models_tool_not_initialized(self):
        """Test list_models tool when AI client is not initialized."""
        mcp = create_mcp_server()

        # Import the server module to patch the global variable
        import mcp_ai_hub.server as server_module

        with patch.object(server_module, "ai_client", None):
            # Call the list_models tool should raise error (wrapped in ToolError)
            with pytest.raises(Exception) as exc_info:
                await mcp.call_tool("list_models", {})
            assert "AI client not initialized" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_get_model_info_tool(self):
        """Test get_model_info tool."""
        mcp = create_mcp_server()

        # Mock the AI client
        mock_client = MagicMock()
        model_info = {
            "model_name": "gpt-4",
            "provider_model": "openai/gpt-4",
            "configured_params": ["api_key", "max_tokens", "temperature"],
        }
        mock_client.get_model_info = MagicMock(return_value=model_info)

        # Import the server module to patch the global variable
        import mcp_ai_hub.server as server_module

        with patch.object(server_module, "ai_client", mock_client):
            # Call the get_model_info tool
            result = await mcp.call_tool("get_model_info", {"model": "gpt-4"})

            # The result should be a tuple of (content, metadata)
            content, metadata = result
            assert len(content) == 1
            # The info should be JSON serialized
            import json

            info = json.loads(content[0].text)
            assert info == model_info
            mock_client.get_model_info.assert_called_once_with("gpt-4")

    @pytest.mark.asyncio
    async def test_get_model_info_tool_not_initialized(self):
        """Test get_model_info tool when AI client is not initialized."""
        mcp = create_mcp_server()

        # Import the server module to patch the global variable
        import mcp_ai_hub.server as server_module

        with patch.object(server_module, "ai_client", None):
            # Call the get_model_info tool should raise error (wrapped in ToolError)
            with pytest.raises(Exception) as exc_info:
                await mcp.call_tool("get_model_info", {"model": "gpt-4"})
            assert "AI client not initialized" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_initialize_client_success(self):
        """Test successful client initialization."""
        with (
            patch(
                "mcp_ai_hub.server.AIHubConfig.load_config", return_value=self.config
            ) as mock_load,
            patch("mcp_ai_hub.server.AIClient") as mock_client_class,
        ):
            mock_client = MagicMock()
            mock_client_class.return_value = mock_client

            await initialize_client()

            mock_load.assert_called_once()
            mock_client_class.assert_called_once_with(self.config)

    @pytest.mark.asyncio
    async def test_initialize_client_with_config_path(self):
        """Test client initialization with custom config path."""
        custom_path = MagicMock()

        with (
            patch(
                "mcp_ai_hub.server.AIHubConfig.load_config", return_value=self.config
            ) as mock_load,
            patch("mcp_ai_hub.server.AIClient") as mock_client_class,
        ):
            mock_client = MagicMock()
            mock_client_class.return_value = mock_client

            await initialize_client(custom_path)

            mock_load.assert_called_once_with(custom_path)
            mock_client_class.assert_called_once_with(self.config)

    @pytest.mark.asyncio
    async def test_initialize_client_failure(self):
        """Test client initialization failure."""
        with (
            patch(
                "mcp_ai_hub.server.AIHubConfig.load_config",
                side_effect=Exception("Config error"),
            ),
            pytest.raises(Exception, match="Config error"),
        ):
            await initialize_client()

    @pytest.mark.asyncio
    async def test_server_tools_metadata(self):
        """Test that server tools have correct metadata."""
        mcp = create_mcp_server()

        # Check that all expected tools are present
        tools = await mcp.list_tools()
        tool_names = [tool.name for tool in tools]
        assert "chat" in tool_names
        assert "list_models" in tool_names
        assert "get_model_info" in tool_names

        # Check chat tool description
        chat_tool = next(tool for tool in tools if tool.name == "chat")
        assert "Chat with specified AI model" in chat_tool.description

        # Check list_models tool description
        list_models_tool = next(tool for tool in tools if tool.name == "list_models")
        assert "List all available AI models" in list_models_tool.description

        # Check get_model_info tool description
        get_model_info_tool = next(
            tool for tool in tools if tool.name == "get_model_info"
        )
        assert (
            "Get information about a specific model" in get_model_info_tool.description
        )

    def test_server_host_port_configuration(self):
        """Test server host and port configuration."""
        # Note: The host and port are used when running the server, but not stored as attributes
        # The FastMCP constructor accepts these parameters for when the server is run
        mcp = create_mcp_server(host="0.0.0.0", port=8080)
        assert mcp.name == "ai-hub"
        # The host and port are configuration for running the server, not attributes

    def test_default_server_configuration(self):
        """Test default server configuration."""
        mcp = create_mcp_server()
        assert mcp.name == "ai-hub"
        # The host and port are configuration for running the server, not attributes


class TestErrorHandling:
    """Test error handling in server."""

    async def get_tool_by_name(self, mcp, tool_name: str):
        """Helper method to get a tool by name from the MCP server."""
        tools = await mcp.list_tools()
        for tool in tools:
            if tool.name == tool_name:
                return tool
        return None

    @pytest.mark.asyncio
    async def test_chat_tool_error_handling(self):
        """Test chat tool error handling."""
        mcp = create_mcp_server()

        # Mock the AI client to raise an exception
        mock_client = MagicMock()
        mock_client.chat = MagicMock(side_effect=Exception("API Error"))

        # Import the server module to patch the global variable
        import mcp_ai_hub.server as server_module

        with (
            patch.object(server_module, "ai_client", mock_client),
            pytest.raises(Exception, match="API Error"),
        ):
            # The error should be raised when calling the tool
            await mcp.call_tool("chat", {"model": "gpt-4", "inputs": "Hello!"})

    @pytest.mark.asyncio
    async def test_get_model_info_tool_error_handling(self):
        """Test get_model_info tool error handling."""
        mcp = create_mcp_server()

        # Mock the AI client to raise an exception
        mock_client = MagicMock()
        mock_client.get_model_info = MagicMock(side_effect=Exception("Model Error"))

        # Import the server module to patch the global variable
        import mcp_ai_hub.server as server_module

        with (
            patch.object(server_module, "ai_client", mock_client),
            pytest.raises(Exception, match="Model Error"),
        ):
            # The error should be raised when calling the tool
            await mcp.call_tool("get_model_info", {"model": "gpt-4"})
