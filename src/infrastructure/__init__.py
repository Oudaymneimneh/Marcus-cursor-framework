"""
Infrastructure Layer for Marcus AI Avatar

Provides core infrastructure services:
- Database connectivity (async SQLAlchemy)
- Redis caching and pub/sub
- Structured logging with correlation IDs
- Metrics collection (Prometheus)
"""

from src.infrastructure.database import (
    check_database_health,
    close_db,
    get_db,
    get_engine,
    get_session_factory,
    init_db,
)
from src.infrastructure.logging import (
    LoggingMiddleware,
    clear_context,
    generate_correlation_id,
    get_correlation_id,
    get_logger,
    log_latency,
    set_correlation_id,
    set_user_context,
    setup_logging,
)
from src.infrastructure.redis import (
    cache_delete,
    cache_exists,
    cache_get,
    cache_get_many,
    cache_set,
    cache_set_many,
    check_redis_health,
    close_redis,
    get_redis_client,
    init_redis,
    publish_event,
    subscribe_events,
)
from src.infrastructure.metrics import (
    REQUEST_COUNT,
    REQUEST_LATENCY,
    track_time,
    update_pad_metrics,
    generate_metrics_response,
)

__all__ = [
    # Database
    "get_engine",
    "get_session_factory",
    "get_db",
    "check_database_health",
    "init_db",
    "close_db",
    # Redis
    "get_redis_client",
    "cache_get",
    "cache_set",
    "cache_delete",
    "cache_exists",
    "cache_get_many",
    "cache_set_many",
    "publish_event",
    "subscribe_events",
    "check_redis_health",
    "init_redis",
    "close_redis",
    # Logging
    "setup_logging",
    "get_logger",
    "set_correlation_id",
    "get_correlation_id",
    "set_user_context",
    "clear_context",
    "generate_correlation_id",
    "log_latency",
    "LoggingMiddleware",
    # Metrics
    "REQUEST_COUNT",
    "REQUEST_LATENCY",
    "track_time",
    "update_pad_metrics",
    "generate_metrics_response",
]
