"""
Redis Service Layer for Marcus AI Avatar

Provides async Redis connectivity for caching and pub/sub event broadcasting.
All operations are async with graceful error handling (never crashes on Redis errors).

Usage - Caching:
    from src.infrastructure.redis import cache_get, cache_set, cache_delete

    # Store user context with 1-hour TTL
    await cache_set("user:123:context", {"name": "John", "mood": "contemplative"}, ttl=3600)

    # Retrieve user context
    context = await cache_get("user:123:context")

    # Delete cached data
    await cache_delete("user:123:context")

Usage - Pub/Sub:
    from src.infrastructure.redis import publish_event, subscribe_events

    # Publish PAD emotional state update
    await publish_event("pad_update", {
        "user_id": "123",
        "pleasure": 0.5,
        "arousal": -0.2,
        "dominance": 0.3,
        "quadrant": "contemplative"
    })

    # Subscribe to events (typically in background task)
    async def handle_event(event_type: str, data: dict):
        print(f"Received {event_type}: {data}")

    await subscribe_events(handle_event)

Features:
    - Async connection pooling for high concurrency
    - JSON serialization for complex objects
    - Graceful degradation (returns None/False on errors)
    - Pub/Sub for real-time dashboard updates
    - Configurable TTL for cache entries
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Any, Callable, Optional

import redis.asyncio as redis
from redis.asyncio import Redis
from redis.exceptions import RedisError

from src.config import get_settings

logger = logging.getLogger(__name__)

# Global Redis client (initialized in init_redis)
_redis_client: Optional[Redis] = None

# Pub/Sub channel name for Marcus events
EVENTS_CHANNEL = "marcus:events"


class DateTimeEncoder(json.JSONEncoder):
    """Custom JSON encoder that handles datetime objects."""

    def default(self, obj: Any) -> Any:
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)


def _serialize(value: Any) -> str:
    """
    Serialize value to JSON string.

    Args:
        value: Any JSON-serializable value.

    Returns:
        JSON string representation.
    """
    return json.dumps(value, cls=DateTimeEncoder)


def _deserialize(value: str) -> Any:
    """
    Deserialize JSON string to Python object.

    Args:
        value: JSON string.

    Returns:
        Deserialized Python object.
    """
    return json.loads(value)


def get_redis_client() -> Redis:
    """
    Get or create Redis client with connection pooling.

    Creates a singleton Redis client configured from application settings.
    The client uses connection pooling for efficient concurrent operations.

    Returns:
        Redis: Async Redis client with connection pooling.

    Example:
        >>> client = get_redis_client()
        >>> await client.ping()
        True
    """
    global _redis_client

    if _redis_client is None:
        settings = get_settings()
        _redis_client = redis.from_url(
            settings.redis_url,
            max_connections=settings.redis_max_connections,
            decode_responses=True,  # Return strings instead of bytes
            socket_connect_timeout=5,
            socket_timeout=5,
        )
        logger.info(
            "Redis client created",
            extra={
                "url": _mask_url(settings.redis_url),
                "max_connections": settings.redis_max_connections,
            },
        )

    return _redis_client


async def cache_get(key: str) -> Optional[Any]:
    """
    Get value from Redis cache.

    Automatically deserializes JSON. Returns None if key not found
    or on any error (graceful degradation).

    Args:
        key: Cache key to retrieve.

    Returns:
        Cached value or None if not found/error.

    Example:
        >>> context = await cache_get("user:123:context")
        >>> if context:
        ...     print(f"User name: {context['name']}")
    """
    try:
        client = get_redis_client()
        value = await client.get(key)

        if value is None:
            logger.debug(f"Cache miss", extra={"key": key})
            return None

        result = _deserialize(value)
        logger.debug(f"Cache hit", extra={"key": key})
        return result

    except json.JSONDecodeError as e:
        logger.warning(
            "Failed to deserialize cached value",
            extra={"key": key, "error": str(e)},
        )
        return None
    except RedisError as e:
        logger.error(
            "Redis error on cache get",
            extra={"key": key, "error": str(e), "error_type": type(e).__name__},
        )
        return None
    except Exception as e:
        logger.error(
            "Unexpected error on cache get",
            extra={"key": key, "error": str(e), "error_type": type(e).__name__},
        )
        return None


async def cache_set(key: str, value: Any, ttl: int = 3600) -> bool:
    """
    Set value in Redis cache with TTL.

    Automatically serializes value to JSON. Default TTL is 1 hour.
    Returns False on any error (graceful degradation).

    Args:
        key: Cache key.
        value: Value to cache (must be JSON-serializable).
        ttl: Time-to-live in seconds (default: 3600 = 1 hour).

    Returns:
        True on success, False on error.

    Example:
        >>> success = await cache_set(
        ...     "user:123:context",
        ...     {"name": "Marcus", "state": "contemplative"},
        ...     ttl=3600
        ... )
        >>> print(f"Cached: {success}")
    """
    try:
        client = get_redis_client()
        serialized = _serialize(value)
        await client.setex(key, ttl, serialized)

        logger.debug(
            "Cache set",
            extra={"key": key, "ttl": ttl, "size_bytes": len(serialized)},
        )
        return True

    except (TypeError, ValueError) as e:
        logger.error(
            "Failed to serialize value for cache",
            extra={"key": key, "error": str(e), "value_type": type(value).__name__},
        )
        return False
    except RedisError as e:
        logger.error(
            "Redis error on cache set",
            extra={"key": key, "error": str(e), "error_type": type(e).__name__},
        )
        return False
    except Exception as e:
        logger.error(
            "Unexpected error on cache set",
            extra={"key": key, "error": str(e), "error_type": type(e).__name__},
        )
        return False


async def cache_delete(key: str) -> bool:
    """
    Delete key from Redis cache.

    Args:
        key: Cache key to delete.

    Returns:
        True if key was deleted, False if not found or error.

    Example:
        >>> deleted = await cache_delete("user:123:context")
        >>> print(f"Deleted: {deleted}")
    """
    try:
        client = get_redis_client()
        result = await client.delete(key)

        deleted = result > 0
        logger.debug(
            "Cache delete",
            extra={"key": key, "deleted": deleted},
        )
        return deleted

    except RedisError as e:
        logger.error(
            "Redis error on cache delete",
            extra={"key": key, "error": str(e), "error_type": type(e).__name__},
        )
        return False
    except Exception as e:
        logger.error(
            "Unexpected error on cache delete",
            extra={"key": key, "error": str(e), "error_type": type(e).__name__},
        )
        return False


async def cache_exists(key: str) -> bool:
    """
    Check if key exists in Redis cache.

    Args:
        key: Cache key to check.

    Returns:
        True if key exists, False otherwise.

    Example:
        >>> if await cache_exists("user:123:context"):
        ...     context = await cache_get("user:123:context")
    """
    try:
        client = get_redis_client()
        result = await client.exists(key)
        return result > 0

    except RedisError as e:
        logger.error(
            "Redis error on cache exists check",
            extra={"key": key, "error": str(e), "error_type": type(e).__name__},
        )
        return False
    except Exception as e:
        logger.error(
            "Unexpected error on cache exists check",
            extra={"key": key, "error": str(e), "error_type": type(e).__name__},
        )
        return False


async def publish_event(event_type: str, data: dict) -> bool:
    """
    Publish event to Marcus events channel.

    Events are published to the 'marcus:events' channel for real-time
    dashboard updates and inter-service communication.

    Args:
        event_type: Type of event (e.g., "pad_update", "session_start").
        data: Event payload dictionary.

    Returns:
        True on success, False on error.

    Example:
        >>> await publish_event("pad_update", {
        ...     "user_id": "123",
        ...     "pleasure": 0.5,
        ...     "arousal": -0.2,
        ...     "dominance": 0.3,
        ... })
    """
    try:
        client = get_redis_client()

        event = {
            "type": event_type,
            "data": data,
            "timestamp": datetime.utcnow().isoformat(),
        }
        message = _serialize(event)

        num_subscribers = await client.publish(EVENTS_CHANNEL, message)

        logger.debug(
            "Event published",
            extra={
                "event_type": event_type,
                "channel": EVENTS_CHANNEL,
                "subscribers": num_subscribers,
            },
        )
        return True

    except (TypeError, ValueError) as e:
        logger.error(
            "Failed to serialize event",
            extra={"event_type": event_type, "error": str(e)},
        )
        return False
    except RedisError as e:
        logger.error(
            "Redis error on event publish",
            extra={
                "event_type": event_type,
                "error": str(e),
                "error_type": type(e).__name__,
            },
        )
        return False
    except Exception as e:
        logger.error(
            "Unexpected error on event publish",
            extra={
                "event_type": event_type,
                "error": str(e),
                "error_type": type(e).__name__,
            },
        )
        return False


async def subscribe_events(
    callback: Callable[[str, dict], Any],
    channel: str = EVENTS_CHANNEL,
) -> None:
    """
    Subscribe to Marcus events channel and process messages.

    Runs continuously, calling the callback for each received event.
    Should be run in a background task.

    Args:
        callback: Async or sync function called with (event_type, data) for each event.
        channel: Channel to subscribe to (default: marcus:events).

    Example:
        >>> async def handle_event(event_type: str, data: dict):
        ...     print(f"Event: {event_type}, Data: {data}")
        ...
        >>> # Run in background task
        >>> asyncio.create_task(subscribe_events(handle_event))
    """
    try:
        client = get_redis_client()
        pubsub = client.pubsub()

        await pubsub.subscribe(channel)
        logger.info(f"Subscribed to channel", extra={"channel": channel})

        async for message in pubsub.listen():
            if message["type"] == "message":
                try:
                    event = _deserialize(message["data"])
                    event_type = event.get("type", "unknown")
                    data = event.get("data", {})

                    # Call callback (handle both sync and async)
                    if asyncio.iscoroutinefunction(callback):
                        await callback(event_type, data)
                    else:
                        callback(event_type, data)

                except json.JSONDecodeError as e:
                    logger.warning(
                        "Failed to deserialize event",
                        extra={"error": str(e), "raw_message": message["data"][:100]},
                    )
                except Exception as e:
                    logger.error(
                        "Error processing event",
                        extra={"error": str(e), "error_type": type(e).__name__},
                    )

    except RedisError as e:
        logger.error(
            "Redis error in event subscription",
            extra={"channel": channel, "error": str(e), "error_type": type(e).__name__},
        )
    except Exception as e:
        logger.error(
            "Unexpected error in event subscription",
            extra={"channel": channel, "error": str(e), "error_type": type(e).__name__},
        )


async def check_redis_health() -> bool:
    """
    Test Redis connectivity with PING command.

    Used by health check endpoints for monitoring.

    Returns:
        True if Redis is healthy and responsive, False otherwise.

    Example:
        >>> healthy = await check_redis_health()
        >>> if not healthy:
        ...     logger.error("Redis health check failed")
    """
    try:
        client = get_redis_client()
        result = await client.ping()

        if result:
            logger.debug("Redis health check passed")
            return True
        return False

    except RedisError as e:
        logger.error(
            "Redis health check failed",
            extra={"error": str(e), "error_type": type(e).__name__},
        )
        return False
    except Exception as e:
        logger.error(
            "Unexpected error during Redis health check",
            extra={"error": str(e), "error_type": type(e).__name__},
        )
        return False


def init_redis() -> None:
    """
    Initialize Redis client on application startup.

    Creates the Redis client with connection pooling. Should be called
    once during application startup (e.g., in FastAPI lifespan).

    Example:
        >>> from contextlib import asynccontextmanager
        >>> @asynccontextmanager
        ... async def lifespan(app: FastAPI):
        ...     init_redis()
        ...     yield
        ...     await close_redis()
    """
    settings = get_settings()

    # Initialize client
    client = get_redis_client()

    logger.info(
        "Redis initialized",
        extra={
            "url": _mask_url(settings.redis_url),
            "max_connections": settings.redis_max_connections,
        },
    )


async def close_redis() -> None:
    """
    Close Redis connections on application shutdown.

    Closes the connection pool and cleans up resources.
    Should be called during application shutdown.

    Example:
        >>> from contextlib import asynccontextmanager
        >>> @asynccontextmanager
        ... async def lifespan(app: FastAPI):
        ...     init_redis()
        ...     yield
        ...     await close_redis()
    """
    global _redis_client

    if _redis_client is not None:
        await _redis_client.close()
        logger.info("Redis connection closed")
        _redis_client = None


def _mask_url(url: str) -> str:
    """
    Mask password in Redis URL for safe logging.

    Args:
        url: Redis connection URL.

    Returns:
        URL with password replaced by asterisks.
    """
    import re

    # Match pattern: redis://[:password@]host
    return re.sub(r"(redis://[^:]*:)[^@]+(@)", r"\1****\2", url)


async def cache_get_many(keys: list[str]) -> dict[str, Any]:
    """
    Get multiple values from Redis cache.

    Args:
        keys: List of cache keys to retrieve.

    Returns:
        Dictionary mapping keys to their values (missing keys excluded).

    Example:
        >>> results = await cache_get_many(["user:1:context", "user:2:context"])
        >>> for key, value in results.items():
        ...     print(f"{key}: {value}")
    """
    try:
        client = get_redis_client()
        values = await client.mget(keys)

        result = {}
        for key, value in zip(keys, values):
            if value is not None:
                try:
                    result[key] = _deserialize(value)
                except json.JSONDecodeError:
                    logger.warning(f"Failed to deserialize key: {key}")

        return result

    except RedisError as e:
        logger.error(
            "Redis error on cache get_many",
            extra={"keys_count": len(keys), "error": str(e)},
        )
        return {}
    except Exception as e:
        logger.error(
            "Unexpected error on cache get_many",
            extra={"keys_count": len(keys), "error": str(e)},
        )
        return {}


async def cache_set_many(items: dict[str, Any], ttl: int = 3600) -> bool:
    """
    Set multiple values in Redis cache.

    Args:
        items: Dictionary of key-value pairs to cache.
        ttl: Time-to-live in seconds (applied to all keys).

    Returns:
        True if all items were set successfully, False on error.

    Example:
        >>> await cache_set_many({
        ...     "user:1:context": {"name": "John"},
        ...     "user:2:context": {"name": "Jane"},
        ... }, ttl=3600)
    """
    try:
        client = get_redis_client()
        pipeline = client.pipeline()

        for key, value in items.items():
            serialized = _serialize(value)
            pipeline.setex(key, ttl, serialized)

        await pipeline.execute()

        logger.debug(
            "Cache set_many",
            extra={"keys_count": len(items), "ttl": ttl},
        )
        return True

    except (TypeError, ValueError) as e:
        logger.error(
            "Failed to serialize values for cache",
            extra={"error": str(e)},
        )
        return False
    except RedisError as e:
        logger.error(
            "Redis error on cache set_many",
            extra={"keys_count": len(items), "error": str(e)},
        )
        return False
    except Exception as e:
        logger.error(
            "Unexpected error on cache set_many",
            extra={"keys_count": len(items), "error": str(e)},
        )
        return False
