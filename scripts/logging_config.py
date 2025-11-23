"""
Logging Configuration for Marcus AI Avatar
Standardized logging across all services.
"""

import logging
import sys
from pathlib import Path


def setup_logging(
    service_name: str,
    level: int = logging.INFO,
    log_to_file: bool = True,
) -> logging.Logger:
    """
    Configure logging for a service.

    Args:
        service_name: Name of the service (e.g., 'flame', 'tts', 'orchestrator')
        level: Logging level
        log_to_file: Whether to also log to file

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(service_name)
    logger.setLevel(level)

    # Clear existing handlers
    logger.handlers.clear()

    # Format with latency-friendly timestamps
    formatter = logging.Formatter(
        fmt="%(asctime)s.%(msecs)03d | %(name)s | %(levelname)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File handler
    if log_to_file:
        log_dir = Path(__file__).parent.parent / "logs"
        log_dir.mkdir(exist_ok=True)
        file_handler = logging.FileHandler(log_dir / f"{service_name}.log")
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


# Latency logging decorator (from project_config.md)
import functools
import time


def log_latency(stage: str, logger: logging.Logger = None):
    """
    Decorator to log function execution latency.

    Usage:
        @log_latency("flame_inference")
        async def run_inference(audio):
            ...
    """
    def decorator(func):
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            t0 = time.perf_counter()
            result = await func(*args, **kwargs)
            ms = (time.perf_counter() - t0) * 1000
            log = logger or logging.getLogger(func.__module__)
            log.info(f"[LATENCY] {stage}: {ms:.1f}ms")
            return result

        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            t0 = time.perf_counter()
            result = func(*args, **kwargs)
            ms = (time.perf_counter() - t0) * 1000
            log = logger or logging.getLogger(func.__module__)
            log.info(f"[LATENCY] {stage}: {ms:.1f}ms")
            return result

        # Return appropriate wrapper based on function type
        if asyncio_iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper

    return decorator


def asyncio_iscoroutinefunction(func):
    """Check if function is async"""
    import asyncio
    return asyncio.iscoroutinefunction(func)
