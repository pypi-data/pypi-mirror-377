"""Unit tests for AI client (LiteLM integration)."""

from unittest.mock import MagicMock, patch

import pytest

from mcp_ai_hub.ai_client import AIClient
from mcp_ai_hub.config import AIHubConfig, ModelConfig


class TestAIClient:
    """Test AIClient class."""

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
        self.client = AIClient(self.config)

    def test_init(self):
        """Test AIClient initialization."""
        assert self.client.config == self.config

    def test_chat_with_string_input(self):
        """Test chat with string input."""
        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message=MagicMock(content="Test response"))]

        with patch(
            "mcp_ai_hub.ai_client.litellm.completion",
            return_value=mock_response,
        ) as mock_completion:
            response = self.client.chat("gpt-4", "Hello, world!")

            assert response == "Test response"
            mock_completion.assert_called_once_with(
                model="openai/gpt-4",
                messages=[{"role": "user", "content": "Hello, world!"}],
                api_key="test-key",
                max_tokens=2048,
                temperature=0.7,
                stream=False,
            )

    def test_chat_with_messages_input(self):
        """Test chat with messages input."""
        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message=MagicMock(content="Test response"))]

        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Hello!"},
        ]

        with patch(
            "mcp_ai_hub.ai_client.litellm.completion",
            return_value=mock_response,
        ) as mock_completion:
            response = self.client.chat("gpt-4", messages)

            assert response == "Test response"
            mock_completion.assert_called_once_with(
                model="openai/gpt-4",
                messages=messages,
                api_key="test-key",
                max_tokens=2048,
                temperature=0.7,
                stream=False,
            )

    def test_chat_with_non_existing_model(self):
        """Test chat with non-existing model."""
        with pytest.raises(
            ValueError, match="Model 'non-existing' not found in configuration"
        ):
            self.client.chat("non-existing", "Hello!")

    def test_chat_missing_model_parameter(self):
        """Test chat with model config missing model parameter."""
        config = AIHubConfig(
            model_list=[
                ModelConfig(
                    model_name="bad-model",
                    litellm_params={"api_key": "test-key"},  # Missing 'model' parameter
                )
            ]
        )
        client = AIClient(config)

        with pytest.raises(RuntimeError, match="Failed to get response from bad-model"):
            client.chat("bad-model", "Hello!")

    def test_chat_api_error(self):
        """Test chat when API call fails."""
        with (
            patch(
                "mcp_ai_hub.ai_client.litellm.completion",
                side_effect=Exception("API Error"),
            ),
            pytest.raises(RuntimeError, match="Failed to get response from gpt-4"),
        ):
            self.client.chat("gpt-4", "Hello!")

    def test_chat_empty_response(self):
        """Test chat with empty response."""
        mock_response = MagicMock()
        mock_response.choices = []  # Empty choices

        with patch(
            "mcp_ai_hub.ai_client.litellm.completion",
            return_value=mock_response,
        ):
            response = self.client.chat("gpt-4", "Hello!")
            assert response == ""

    def test_chat_missing_content(self):
        """Test chat with response missing content."""
        mock_response = MagicMock()
        mock_response.choices = [
            MagicMock(message=MagicMock(content=None))  # No content
        ]

        with patch(
            "mcp_ai_hub.ai_client.litellm.completion",
            return_value=mock_response,
        ):
            response = self.client.chat("gpt-4", "Hello!")
            assert response == ""

    def test_prepare_messages_string_input(self):
        """Test preparing messages from string input."""
        messages = self.client._prepare_messages("Hello, world!")
        assert messages == [{"role": "user", "content": "Hello, world!"}]

    def test_prepare_messages_valid_list_input(self):
        """Test preparing messages from valid list input."""
        input_messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Hello!"},
        ]
        messages = self.client._prepare_messages(input_messages)
        assert messages == input_messages

    def test_prepare_messages_invalid_list_input(self):
        """Test preparing messages from invalid list input."""
        invalid_messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"invalid": "message"},  # Missing role and content
        ]

        with pytest.raises(ValueError, match="Invalid message format"):
            self.client._prepare_messages(invalid_messages)

    def test_prepare_messages_invalid_input_type(self):
        """Test preparing messages from invalid input type."""
        with pytest.raises(
            ValueError,
            match="Inputs must be either a string or a list of message dictionaries",
        ):
            self.client._prepare_messages(123)  # Invalid type

    def test_list_models(self):
        """Test listing available models."""
        models = self.client.list_models()
        assert len(models) == 2
        assert "gpt-4" in models
        assert "claude-sonnet" in models

    def test_get_model_info_existing(self):
        """Test getting model info for existing model."""
        info = self.client.get_model_info("gpt-4")
        assert info["model_name"] == "gpt-4"
        assert info["provider_model"] == "openai/gpt-4"
        assert "api_key" in info["configured_params"]
        assert "max_tokens" in info["configured_params"]
        assert "temperature" in info["configured_params"]

    def test_get_model_info_non_existing(self):
        """Test getting model info for non-existing model."""
        with pytest.raises(
            ValueError, match="Model 'non-existing' not found in configuration"
        ):
            self.client.get_model_info("non-existing")

    def test_litellm_suppress_debug_info(self):
        """Test that LiteLM debug info is suppressed."""
        with patch("mcp_ai_hub.ai_client.litellm") as mock_litellm:
            AIClient(self.config)
            assert mock_litellm.suppress_debug_info is True
