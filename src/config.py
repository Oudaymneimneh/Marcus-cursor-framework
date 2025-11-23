"""
Configuration Management for Marcus AI Avatar

Loads all settings from environment variables with type validation.
Uses Pydantic Settings for type-safe configuration with automatic .env file loading.

Usage:
    from src.config import get_settings

    settings = get_settings()
    print(settings.openai_model)  # Type-safe access with IDE autocomplete
    print(settings.database_url)  # Required settings validated on startup

Features:
    - Type-safe configuration with full IDE support
    - Automatic validation on startup (fail fast)
    - Environment-specific settings (development, staging, production)
    - Cached singleton pattern for performance
    - Sensible defaults for development

Raises:
    ValidationError: If required settings are missing or have invalid types.
        Example: Missing OPENAI_API_KEY will raise:
        "pydantic_core._pydantic_core.ValidationError: 1 validation error for Settings
         openai_api_key
           Field required [type=missing, input_value={...}]"
"""

from functools import lru_cache
from typing import List, Optional, Union

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application configuration loaded from environment variables.

    All settings are loaded from .env file or environment variables.
    Required settings (no default) will raise ValidationError if missing.
    Settings are immutable after loading (frozen=True).

    Configuration Sections:
        1. Environment - Runtime environment and debug mode
        2. Database - PostgreSQL connection and pool settings
        3. Redis - Redis connection and pool settings
        4. OpenAI - LLM configuration for dialogue generation
        5. Behavioral Config - Path to behavior YAML configuration
        6. Observability - Logging configuration
        7. Metrics - Prometheus metrics settings
        8. API - FastAPI server configuration
    """

    model_config = SettingsConfigDict(
        env_file=(".env", ".env.local", "project.env"),
        env_file_encoding="utf-8",
        case_sensitive=False,
        frozen=True,  # Immutable after loading
        extra="ignore",  # Ignore extra env vars
        populate_by_name=True,  # Allow both field name and alias
    )

    # =========================================================================
    # 1. Environment Settings
    # =========================================================================

    environment: str = Field(
        default="development",
        description="Runtime environment: development, staging, or production",
    )

    debug: bool = Field(
        default=False,
        description="Enable debug mode with verbose logging and hot reload",
    )

    # =========================================================================
    # 2. Database Settings (PostgreSQL)
    # =========================================================================

    database_url: str = Field(
        description="PostgreSQL connection URL (required). "
        "Format: postgresql+asyncpg://user:password@host:port/database",
    )

    database_pool_size: int = Field(
        default=10,
        ge=1,
        le=100,
        description="Database connection pool size. "
        "Higher values support more concurrent queries.",
    )

    database_max_overflow: int = Field(
        default=20,
        ge=0,
        le=100,
        description="Maximum overflow connections beyond pool_size. "
        "Used for burst traffic handling.",
    )

    database_echo: bool = Field(
        default=False,
        description="Echo SQL queries to logs. Enable for debugging, disable in production.",
    )

    # =========================================================================
    # 3. Redis Settings
    # =========================================================================

    redis_url: str = Field(
        description="Redis connection URL (required). "
        "Format: redis://[[username]:[password]@]host:port/database",
    )

    redis_max_connections: int = Field(
        default=50,
        ge=1,
        le=500,
        description="Maximum Redis connection pool size for concurrent operations.",
    )

    # =========================================================================
    # 4. OpenAI Settings
    # =========================================================================

    openai_api_key: str = Field(
        description="OpenAI API key (required). Get from https://platform.openai.com/api-keys",
    )

    openai_model: str = Field(
        default="gpt-4o-mini",
        description="OpenAI model to use for dialogue generation. "
        "Options: gpt-4o, gpt-4o-mini, gpt-4-turbo, gpt-3.5-turbo",
    )

    openai_temperature: float = Field(
        default=0.7,
        ge=0.0,
        le=2.0,
        description="Response creativity/randomness (0.0-2.0). "
        "Lower = more deterministic, higher = more creative.",
    )

    openai_max_tokens: int = Field(
        default=500,
        ge=1,
        le=4096,
        description="Maximum tokens in generated response. "
        "Controls response length.",
    )

    openai_timeout: int = Field(
        default=30,
        ge=1,
        le=300,
        description="OpenAI API request timeout in seconds.",
    )

    # =========================================================================
    # 5. Behavioral Config Settings
    # =========================================================================

    behavior_config_path: str = Field(
        default="src/behavior/behavior_config.yaml",
        description="Path to Marcus behavioral configuration YAML file. "
        "Contains personality traits, emotional states, and response patterns.",
    )

    # =========================================================================
    # 6. Observability Settings
    # =========================================================================

    log_level: str = Field(
        default="INFO",
        description="Logging level: DEBUG, INFO, WARNING, ERROR, CRITICAL. "
        "Use DEBUG for development, INFO or WARNING for production.",
    )

    log_format: str = Field(
        default="json",
        description="Log output format: 'json' for structured logging (production), "
        "'text' for human-readable (development).",
    )

    log_file: Optional[str] = Field(
        default=None,
        description="Log file path. None for stdout only. "
        "Set to path like '/var/log/marcus/app.log' for file logging.",
    )

    @field_validator("log_file", mode="before")
    @classmethod
    def parse_log_file(cls, v: Union[str, None]) -> Union[str, None]:
        """Convert empty string to None for log_file."""
        if isinstance(v, str) and not v.strip():
            return None
        return v

    # =========================================================================
    # 7. Metrics Settings
    # =========================================================================

    metrics_enabled: bool = Field(
        default=True,
        description="Enable Prometheus metrics endpoint for monitoring.",
    )

    metrics_port: int = Field(
        default=9090,
        ge=1024,
        le=65535,
        description="Port for Prometheus metrics endpoint.",
    )

    # =========================================================================
    # 8. API Settings
    # =========================================================================

    api_host: str = Field(
        default="0.0.0.0",
        description="API server bind host. Use 0.0.0.0 for all interfaces, "
        "127.0.0.1 for localhost only.",
    )

    api_port: int = Field(
        default=8000,
        ge=1024,
        le=65535,
        description="API server bind port.",
    )

    api_reload: bool = Field(
        default=True,
        description="Enable hot reload for development. Disable in production.",
    )

    cors_origins_str: str = Field(
        default="http://localhost:3000",
        alias="cors_origins",
        description="Allowed CORS origins (comma-separated). Use specific origins in production, "
        "avoid '*' for security.",
    )

    api_request_timeout: int = Field(
        default=30,
        ge=1,
        le=300,
        description="API request timeout in seconds. "
        "Should accommodate LLM + TTS + FLAME pipeline latency.",
    )

    # =========================================================================
    # Computed Properties
    # =========================================================================

    @property
    def cors_origins(self) -> List[str]:
        """
        Get CORS origins as a list.

        Parses the comma-separated cors_origins_str into a list of origins.
        """
        if not self.cors_origins_str.strip():
            return ["http://localhost:3000"]
        return [origin.strip() for origin in self.cors_origins_str.split(",") if origin.strip()]

    @property
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.environment == "development"

    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.environment == "production"

    @property
    def database_url_sync(self) -> str:
        """
        Get synchronous database URL (psycopg2 driver).

        Converts asyncpg URL to psycopg2 for sync operations like migrations.
        """
        return self.database_url.replace("+asyncpg", "").replace("+aiopg", "")

    @property
    def database_url_async(self) -> str:
        """
        Get asynchronous database URL (asyncpg driver).

        Ensures URL uses asyncpg driver for async SQLAlchemy operations.
        """
        if "+asyncpg" in self.database_url:
            return self.database_url
        return self.database_url.replace("postgresql://", "postgresql+asyncpg://")


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance.

    Settings are loaded once and cached for performance.
    Subsequent calls return the same instance (singleton pattern).

    Returns:
        Settings: Application configuration with validated values.

    Raises:
        ValidationError: If required settings are missing or invalid.
            - Missing required env vars (database_url, redis_url, openai_api_key)
            - Invalid types (e.g., non-integer for database_pool_size)
            - Values outside allowed ranges (e.g., temperature > 2.0)

    Example:
        >>> settings = get_settings()
        >>> settings.openai_model
        'gpt-4o-mini'
        >>> settings.is_production
        False
    """
    return Settings()


def clear_settings_cache() -> None:
    """
    Clear the settings cache.

    Use this only in testing to reload settings between tests.
    Not intended for production use.
    """
    get_settings.cache_clear()
