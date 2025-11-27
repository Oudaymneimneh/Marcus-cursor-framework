"""
Pytest configuration and fixtures.

Sets up test environment variables.
"""

import os
import pytest


@pytest.fixture(scope="session", autouse=True)
def setup_test_env():
    """Set up test environment variables for all tests."""
    # Set minimal required environment variables for tests
    os.environ["DATABASE_URL"] = "postgresql+asyncpg://test:test@localhost/test_db"
    os.environ["REDIS_URL"] = "redis://localhost:6379/1"
    os.environ["OPENAI_API_KEY"] = "sk-test-key-for-testing"
    os.environ["OPENAI_MODEL"] = "gpt-4"
    os.environ["OPENAI_TEMPERATURE"] = "0.7"
    os.environ["OPENAI_MAX_TOKENS"] = "500"
    os.environ["OPENAI_TIMEOUT"] = "30.0"
    
    yield
    
    # Cleanup not necessary for tests, but good practice
    # (pytest runs in isolated process anyway)


