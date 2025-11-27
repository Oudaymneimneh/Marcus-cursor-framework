"""
External service clients.

This module wraps external dependencies (LLMs, APIs) for:
- Testability (inject mocks)
- Swappability (switch providers)
- Observability (centralized logging/metrics)
"""

from src.infrastructure.external.llm_client import (
    LLMClient,
    OpenAIClient,
    MockLLMClient,
    LLMError,
)

__all__ = [
    "LLMClient",
    "OpenAIClient", 
    "MockLLMClient",
    "LLMError",
]


