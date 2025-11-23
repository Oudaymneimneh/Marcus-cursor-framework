"""
Structured Logging for Marcus AI Avatar

Provides JSON-formatted logs for production and human-readable logs for development.
Supports correlation IDs for request tracing and context variables for enriched logs.

Usage:
    from src.infrastructure.logging import setup_logging, get_logger, set_correlation_id

    # Setup logging on application startup
    setup_logging()

    # Get a logger for your module
    logger = get_logger(__name__)

    # Set correlation ID for request tracing
    set_correlation_id("req-12345")

    # Log with automatic context
    logger.info("Processing request", extra={"user_id": "123", "action": "chat"})

Features:
    - JSON format for production (ELK/Datadog compatible)
    - Text format for development (human-readable)
    - Correlation IDs for distributed tracing
    - Context variables (user_id, session_id) in all logs
    - Configurable log level from settings
    - Optional file logging
    - FastAPI middleware for automatic correlation ID handling
"""

import logging
import sys
from contextvars import ContextVar
from datetime import datetime
from typing import Any, Optional
import json

from src.config import get_settings

# Context variables for request-scoped data
correlation_id_var: ContextVar[Optional[str]] = ContextVar("correlation_id", default=None)
user_id_var: ContextVar[Optional[str]] = ContextVar("user_id", default=None)
session_id_var: ContextVar[Optional[str]] = ContextVar("session_id", default=None)

# Track if logging has been set up
_logging_configured = False


class JSONFormatter(logging.Formatter):
    """
    JSON log formatter for production environments.

    Outputs logs as single-line JSON objects for easy parsing by log aggregators
    like ELK Stack, Datadog, or Splunk.
    """

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        log_data = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # Add correlation ID if present
        correlation_id = correlation_id_var.get()
        if correlation_id:
            log_data["correlation_id"] = correlation_id

        # Add user context if present
        user_id = user_id_var.get()
        if user_id:
            log_data["user_id"] = user_id

        session_id = session_id_var.get()
        if session_id:
            log_data["session_id"] = session_id

        # Add any extra fields from the log call
        if hasattr(record, "__dict__"):
            extra_fields = {
                k: v
                for k, v in record.__dict__.items()
                if k not in {
                    "name", "msg", "args", "created", "filename", "funcName",
                    "levelname", "levelno", "lineno", "module", "msecs",
                    "pathname", "process", "processName", "relativeCreated",
                    "stack_info", "exc_info", "exc_text", "thread", "threadName",
                    "message", "asctime",
                }
                and not k.startswith("_")
            }
            if extra_fields:
                log_data["extra"] = extra_fields

        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_data, default=str)


class TextFormatter(logging.Formatter):
    """
    Human-readable log formatter for development environments.

    Outputs colored, easy-to-read logs with context information.
    """

    # ANSI color codes
    COLORS = {
        "DEBUG": "\033[36m",     # Cyan
        "INFO": "\033[32m",      # Green
        "WARNING": "\033[33m",   # Yellow
        "ERROR": "\033[31m",     # Red
        "CRITICAL": "\033[35m",  # Magenta
    }
    RESET = "\033[0m"

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as colored text."""
        # Get color for level
        color = self.COLORS.get(record.levelname, "")

        # Format timestamp
        timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

        # Build context string
        context_parts = []

        correlation_id = correlation_id_var.get()
        if correlation_id:
            context_parts.append(f"cid={correlation_id[:8]}")

        user_id = user_id_var.get()
        if user_id:
            context_parts.append(f"user={user_id}")

        session_id = session_id_var.get()
        if session_id:
            context_parts.append(f"sess={session_id[:8]}")

        context_str = f" [{', '.join(context_parts)}]" if context_parts else ""

        # Build extra fields string
        extra_str = ""
        if hasattr(record, "__dict__"):
            extra_fields = {
                k: v
                for k, v in record.__dict__.items()
                if k not in {
                    "name", "msg", "args", "created", "filename", "funcName",
                    "levelname", "levelno", "lineno", "module", "msecs",
                    "pathname", "process", "processName", "relativeCreated",
                    "stack_info", "exc_info", "exc_text", "thread", "threadName",
                    "message", "asctime",
                }
                and not k.startswith("_")
            }
            if extra_fields:
                extra_str = " | " + " ".join(f"{k}={v}" for k, v in extra_fields.items())

        # Format the log line
        log_line = (
            f"{color}{timestamp} | {record.levelname:8}{self.RESET} | "
            f"{record.name}:{record.lineno}{context_str} | "
            f"{record.getMessage()}{extra_str}"
        )

        # Add exception info if present
        if record.exc_info:
            log_line += "\n" + self.formatException(record.exc_info)

        return log_line


class ContextFilter(logging.Filter):
    """
    Logging filter that adds context variables to log records.

    Ensures correlation_id, user_id, and session_id are available
    in all log records for structured logging.
    """

    def filter(self, record: logging.LogRecord) -> bool:
        """Add context variables to the log record."""
        record.correlation_id = correlation_id_var.get()
        record.user_id = user_id_var.get()
        record.session_id = session_id_var.get()
        return True


def setup_logging() -> None:
    """
    Configure logging based on application settings.

    Sets up formatters, handlers, and log levels according to the
    configuration in src.config.Settings. Should be called once
    during application startup.

    Example:
        >>> from src.infrastructure.logging import setup_logging
        >>> setup_logging()  # Call once at startup
    """
    global _logging_configured

    if _logging_configured:
        return

    settings = get_settings()

    # Get log level from settings
    log_level = getattr(logging, settings.log_level.upper(), logging.INFO)

    # Create formatter based on environment
    if settings.log_format.lower() == "json":
        formatter = JSONFormatter()
    else:
        formatter = TextFormatter()

    # Create context filter
    context_filter = ContextFilter()

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # Remove existing handlers
    root_logger.handlers.clear()

    # Console handler (stdout)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    console_handler.addFilter(context_filter)
    root_logger.addHandler(console_handler)

    # File handler (optional)
    if settings.log_file:
        file_handler = logging.FileHandler(settings.log_file)
        file_handler.setLevel(log_level)
        # Always use JSON format for file logs
        file_handler.setFormatter(JSONFormatter())
        file_handler.addFilter(context_filter)
        root_logger.addHandler(file_handler)

    # Reduce noise from third-party libraries
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("asyncio").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)

    _logging_configured = True

    # Log that logging is configured
    logger = logging.getLogger(__name__)
    logger.info(
        "Logging configured",
        extra={
            "log_level": settings.log_level,
            "log_format": settings.log_format,
            "log_file": settings.log_file,
            "environment": settings.environment,
        },
    )


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance with the given name.

    Ensures logging is configured before returning the logger.

    Args:
        name: Logger name (typically __name__).

    Returns:
        Configured logger instance.

    Example:
        >>> logger = get_logger(__name__)
        >>> logger.info("Hello", extra={"key": "value"})
    """
    if not _logging_configured:
        setup_logging()
    return logging.getLogger(name)


def set_correlation_id(correlation_id: str) -> None:
    """
    Set the correlation ID for the current request context.

    The correlation ID will be included in all subsequent log messages
    within the same async context (request).

    Args:
        correlation_id: Unique identifier for the request.

    Example:
        >>> set_correlation_id("req-abc123")
        >>> logger.info("Processing")  # Includes correlation_id
    """
    correlation_id_var.set(correlation_id)


def get_correlation_id() -> Optional[str]:
    """
    Get the current correlation ID.

    Returns:
        Current correlation ID or None if not set.
    """
    return correlation_id_var.get()


def set_user_context(user_id: Optional[str] = None, session_id: Optional[str] = None) -> None:
    """
    Set user context for the current request.

    User context will be included in all subsequent log messages
    within the same async context.

    Args:
        user_id: User identifier.
        session_id: Session identifier.

    Example:
        >>> set_user_context(user_id="user-123", session_id="sess-456")
        >>> logger.info("User action")  # Includes user_id and session_id
    """
    if user_id is not None:
        user_id_var.set(user_id)
    if session_id is not None:
        session_id_var.set(session_id)


def clear_context() -> None:
    """
    Clear all context variables.

    Should be called at the end of request processing to prevent
    context leakage between requests.
    """
    correlation_id_var.set(None)
    user_id_var.set(None)
    session_id_var.set(None)


def generate_correlation_id() -> str:
    """
    Generate a unique correlation ID.

    Returns:
        Unique correlation ID string.
    """
    import uuid
    return f"req-{uuid.uuid4().hex[:12]}"


class LoggingMiddleware:
    """
    FastAPI/Starlette middleware for automatic correlation ID handling.

    Generates correlation ID for each request and includes it in response headers.

    Usage:
        >>> from fastapi import FastAPI
        >>> from src.infrastructure.logging import LoggingMiddleware
        >>> app = FastAPI()
        >>> app.add_middleware(LoggingMiddleware)
    """

    def __init__(self, app: Any) -> None:
        self.app = app

    async def __call__(self, scope: dict, receive: Any, send: Any) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        # Generate or extract correlation ID
        headers = dict(scope.get("headers", []))
        correlation_id = headers.get(b"x-correlation-id", b"").decode() or generate_correlation_id()

        # Set context
        set_correlation_id(correlation_id)

        # Log request start
        logger = get_logger("marcus.request")
        logger.info(
            "Request started",
            extra={
                "method": scope.get("method"),
                "path": scope.get("path"),
                "query_string": scope.get("query_string", b"").decode(),
            },
        )

        import time
        start_time = time.perf_counter()

        async def send_wrapper(message: dict) -> None:
            if message["type"] == "http.response.start":
                # Add correlation ID to response headers
                headers = list(message.get("headers", []))
                headers.append((b"x-correlation-id", correlation_id.encode()))
                message["headers"] = headers
            await send(message)

        try:
            await self.app(scope, receive, send_wrapper)
        finally:
            # Log request completion
            duration_ms = (time.perf_counter() - start_time) * 1000
            logger.info(
                "Request completed",
                extra={
                    "duration_ms": round(duration_ms, 2),
                    "method": scope.get("method"),
                    "path": scope.get("path"),
                },
            )
            # Clear context
            clear_context()


def log_latency(stage: str):
    """
    Decorator for logging function execution latency.

    Logs the execution time of async functions with the specified stage name.

    Args:
        stage: Name of the processing stage (e.g., "llm_response", "tts_synthesis").

    Example:
        >>> @log_latency("database_query")
        ... async def fetch_user(user_id: str):
        ...     return await db.get_user(user_id)
    """
    def decorator(func):
        import functools
        import time

        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            logger = get_logger(func.__module__)
            start = time.perf_counter()

            try:
                result = await func(*args, **kwargs)
                duration_ms = (time.perf_counter() - start) * 1000

                logger.info(
                    f"[LATENCY] {stage}",
                    extra={
                        "stage": stage,
                        "duration_ms": round(duration_ms, 2),
                        "function": func.__name__,
                    },
                )
                return result

            except Exception as e:
                duration_ms = (time.perf_counter() - start) * 1000
                logger.error(
                    f"[LATENCY] {stage} failed",
                    extra={
                        "stage": stage,
                        "duration_ms": round(duration_ms, 2),
                        "function": func.__name__,
                        "error": str(e),
                        "error_type": type(e).__name__,
                    },
                )
                raise

        return wrapper
    return decorator
