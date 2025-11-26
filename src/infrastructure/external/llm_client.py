from abc import ABC, abstractmethod
from typing import List, Dict, Optional
from openai import AsyncOpenAI, OpenAIError
from src.config import get_settings
from src.infrastructure.logging import logger

class LLMError(Exception):
    """Base exception for LLM errors."""
    pass

class LLMClient(ABC):
    """Abstract base for LLM providers."""
    
    @abstractmethod
    async def generate(
        self, 
        messages: List[Dict[str, str]], 
        temperature: float = 0.7,
        max_tokens: int = 500
    ) -> str:
        """Generate response from messages."""
        pass

class OpenAIClient(LLMClient):
    """OpenAI implementation."""
    
    def __init__(self, api_key: str = None, model: str = None):
        settings = get_settings()
        self.client = AsyncOpenAI(api_key=api_key or settings.openai_api_key)
        self.model = model or settings.openai_model
        self.timeout = settings.openai_timeout
    
    async def generate(self, messages: List[Dict[str, str]], temperature: float = 0.7, max_tokens: int = 500) -> str:
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                timeout=self.timeout
            )
            content = response.choices[0].message.content
            if content is None:
                 raise LLMError("Received empty response from OpenAI")
            return content
        except OpenAIError as e:
            logger.error(f"OpenAI API error: {e}")
            raise LLMError(f"Failed to generate response: {e}") from e
        except Exception as e:
            logger.error(f"Unexpected error in OpenAIClient: {e}")
            raise LLMError(f"Unexpected error: {e}") from e

class MockLLMClient(LLMClient):
    """Mock for testing."""
    
    def __init__(self, mock_response: str = "I am Marcus."):
        self.mock_response = mock_response
    
    async def generate(self, messages: List[Dict[str, str]], temperature: float = 0.7, max_tokens: int = 500) -> str:
        return self.mock_response


