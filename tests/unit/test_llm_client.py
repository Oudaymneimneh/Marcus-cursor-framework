"""
Unit tests for LLM client abstraction.

Tests OpenAIClient wrapper and MockLLMClient.
"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from src.infrastructure.external import (
    LLMClient,
    OpenAIClient,
    MockLLMClient,
    LLMError,
)


class TestMockLLMClient:
    """Test MockLLMClient for testing purposes."""

    @pytest.mark.asyncio
    async def test_returns_mock_response(self):
        """Test that MockLLMClient returns configured response."""
        mock_client = MockLLMClient(mock_response="Test response")

        result = await mock_client.generate(
            messages=[{"role": "user", "content": "Hello"}]
        )

        assert result == "Test response"

    @pytest.mark.asyncio
    async def test_tracks_call_count(self):
        """Test that call count is tracked."""
        mock_client = MockLLMClient()

        await mock_client.generate(messages=[])
        await mock_client.generate(messages=[])
        await mock_client.generate(messages=[])

        assert mock_client.call_count == 3

    @pytest.mark.asyncio
    async def test_stores_last_messages(self):
        """Test that last messages are stored for inspection."""
        mock_client = MockLLMClient()
        messages = [
            {"role": "system", "content": "You are helpful"},
            {"role": "user", "content": "Hello"},
        ]

        await mock_client.generate(messages=messages)

        assert mock_client.last_messages == messages

    @pytest.mark.asyncio
    async def test_simulated_delay(self):
        """Test that delay is simulated."""
        import time

        mock_client = MockLLMClient(delay_seconds=0.1)

        start = time.perf_counter()
        await mock_client.generate(messages=[])
        elapsed = time.perf_counter() - start

        assert elapsed >= 0.1


class TestOpenAIClient:
    """Test OpenAIClient wrapper."""

    @pytest.mark.asyncio
    async def test_generate_success(self):
        """Test successful generation."""
        # Mock the OpenAI response
        mock_response = MagicMock()
        mock_response.choices = [
            MagicMock(message=MagicMock(content="Generated response"))
        ]

        with patch("src.infrastructure.external.llm_client.AsyncOpenAI") as mock_openai, \
             patch("src.infrastructure.external.llm_client.get_settings") as mock_settings:
            # Mock settings
            mock_settings.return_value = MagicMock(
                openai_api_key="test-key",
                openai_model="gpt-4",
                openai_timeout=30.0
            )
            
            mock_client_instance = AsyncMock()
            mock_client_instance.chat.completions.create = AsyncMock(
                return_value=mock_response
            )
            mock_openai.return_value = mock_client_instance

            client = OpenAIClient(api_key="test-key", model="gpt-4")
            result = await client.generate(
                messages=[{"role": "user", "content": "Hello"}]
            )

            assert result == "Generated response"
            mock_client_instance.chat.completions.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_generate_with_parameters(self):
        """Test that generation parameters are passed correctly."""
        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message=MagicMock(content="Response"))]

        with patch("src.infrastructure.external.llm_client.AsyncOpenAI") as mock_openai, \
             patch("src.infrastructure.external.llm_client.get_settings") as mock_settings:
            # Mock settings
            mock_settings.return_value = MagicMock(
                openai_api_key="test-key",
                openai_model="gpt-4",
                openai_timeout=30.0
            )
            
            mock_client_instance = AsyncMock()
            mock_client_instance.chat.completions.create = AsyncMock(
                return_value=mock_response
            )
            mock_openai.return_value = mock_client_instance

            client = OpenAIClient(api_key="test-key", model="gpt-4")
            await client.generate(
                messages=[{"role": "user", "content": "Test"}],
                temperature=0.9,
                max_tokens=1000,
            )

            # Verify parameters were passed
            call_kwargs = mock_client_instance.chat.completions.create.call_args[1]
            assert call_kwargs["temperature"] == 0.9
            assert call_kwargs["max_tokens"] == 1000
            assert call_kwargs["model"] == "gpt-4"

    @pytest.mark.asyncio
    async def test_handles_openai_error(self):
        """Test that OpenAI errors are wrapped in LLMError."""
        from openai import OpenAIError

        with patch("src.infrastructure.external.llm_client.AsyncOpenAI") as mock_openai, \
             patch("src.infrastructure.external.llm_client.get_settings") as mock_settings:
            # Mock settings
            mock_settings.return_value = MagicMock(
                openai_api_key="test-key",
                openai_model="gpt-4",
                openai_timeout=30.0
            )
            
            mock_client_instance = AsyncMock()
            mock_client_instance.chat.completions.create = AsyncMock(
                side_effect=OpenAIError("API error")
            )
            mock_openai.return_value = mock_client_instance

            client = OpenAIClient(api_key="test-key")

            with pytest.raises(LLMError) as exc_info:
                await client.generate(messages=[])

            assert "OpenAI API failed" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_handles_unexpected_error(self):
        """Test that unexpected errors are wrapped in LLMError."""
        with patch("src.infrastructure.external.llm_client.AsyncOpenAI") as mock_openai, \
             patch("src.infrastructure.external.llm_client.get_settings") as mock_settings:
            # Mock settings
            mock_settings.return_value = MagicMock(
                openai_api_key="test-key",
                openai_model="gpt-4",
                openai_timeout=30.0
            )
            
            mock_client_instance = AsyncMock()
            mock_client_instance.chat.completions.create = AsyncMock(
                side_effect=RuntimeError("Unexpected error")
            )
            mock_openai.return_value = mock_client_instance

            client = OpenAIClient(api_key="test-key")

            with pytest.raises(LLMError) as exc_info:
                await client.generate(messages=[])

            assert "LLM generation failed" in str(exc_info.value)


class TestLLMClientInterface:
    """Test that clients conform to LLMClient interface."""

    def test_mock_client_is_llm_client(self):
        """Test MockLLMClient implements LLMClient."""
        client = MockLLMClient()
        assert isinstance(client, LLMClient)

    def test_openai_client_is_llm_client(self):
        """Test OpenAIClient implements LLMClient."""
        with patch("src.infrastructure.external.llm_client.AsyncOpenAI"), \
             patch("src.infrastructure.external.llm_client.get_settings") as mock_settings:
            # Mock settings
            mock_settings.return_value = MagicMock(
                openai_api_key="test",
                openai_model="gpt-4",
                openai_timeout=30.0
            )
            client = OpenAIClient(api_key="test")
            assert isinstance(client, LLMClient)


