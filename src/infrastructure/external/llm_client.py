"""
LLM Client Abstraction.

Wraps LLM providers (OpenAI, Claude, etc.) for:
- Testability: Inject MockLLMClient in tests
- Swappability: Easy to add new providers
- Observability: Centralized logging and metrics
"""

import logging
from abc import ABC, abstractmethod
from typing import List, Dict, Optional

from openai import AsyncOpenAI, OpenAIError

from src.config import get_settings
from src.infrastructure.logging import log_latency

logger = logging.getLogger(__name__)


class LLMError(Exception):
    """Base exception for LLM client errors."""
    pass


class LLMClient(ABC):
    """
    Abstract base class for LLM providers.
    
    Implementations must handle:
    - API calls
    - Error handling
    - Response extraction
    """

    @abstractmethod
    async def generate(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 500,
    ) -> str:
        """
        Generate response from conversation messages.

        Args:
            messages: List of message dicts with 'role' and 'content' keys
            temperature: Sampling temperature (0.0 = deterministic, 2.0 = random)
            max_tokens: Maximum tokens to generate

        Returns:
            Generated text response

        Raises:
            LLMError: If generation fails
        """
        pass


class OpenAIClient(LLMClient):
    """
    OpenAI API client implementation.
    
    Supports GPT-4, GPT-3.5-turbo, etc.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        timeout: Optional[float] = None,
    ):
        """
        Initialize OpenAI client.

        Args:
            api_key: OpenAI API key (defaults to settings)
            model: Model name (defaults to settings)
            timeout: Request timeout in seconds (defaults to settings)
        """
        settings = get_settings()
        self.client = AsyncOpenAI(api_key=api_key or settings.openai_api_key)
        self.model = model or settings.openai_model
        self.timeout = timeout or settings.openai_timeout

    @log_latency("llm_generation")
    async def generate(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 500,
    ) -> str:
        """
        Generate response using OpenAI API.

        Args:
            messages: Conversation history
            temperature: Sampling temperature
            max_tokens: Max tokens to generate

        Returns:
            Generated response text

        Raises:
            LLMError: If API call fails
        """
        try:
            logger.debug(
                f"[LLM] Calling OpenAI {self.model} "
                f"(temp={temperature}, max_tokens={max_tokens})"
            )

            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                timeout=self.timeout,
            )

            reply = response.choices[0].message.content
            logger.debug(f"[LLM] Generated {len(reply)} characters")

            return reply

        except OpenAIError as e:
            logger.error(f"[LLM] OpenAI API error: {e}")
            raise LLMError(f"OpenAI API failed: {e}") from e

        except Exception as e:
            logger.error(f"[LLM] Unexpected error: {e}")
            raise LLMError(f"LLM generation failed: {e}") from e


class MockLLMClient(LLMClient):
    """
    Mock LLM client for testing.
    
    Returns predefined responses without making API calls.
    """

    def __init__(
        self,
        mock_response: str = "I am Marcus Aurelius. This is a test response.",
        delay_seconds: float = 0.0,
    ):
        """
        Initialize mock client.

        Args:
            mock_response: Response to return
            delay_seconds: Simulated latency
        """
        self.mock_response = mock_response
        self.delay_seconds = delay_seconds
        self.call_count = 0
        self.last_messages: Optional[List[Dict[str, str]]] = None

    async def generate(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 500,
    ) -> str:
        """
        Return mock response.

        Args:
            messages: Ignored (but stored for inspection in tests)
            temperature: Ignored
            max_tokens: Ignored

        Returns:
            Mock response string
        """
        import asyncio

        self.call_count += 1
        self.last_messages = messages

        if self.delay_seconds > 0:
            await asyncio.sleep(self.delay_seconds)

        logger.debug(f"[MockLLM] Returning mock response (call #{self.call_count})")
        return self.mock_response


