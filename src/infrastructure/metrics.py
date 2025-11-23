"""
Prometheus Metrics Infrastructure for Marcus AI Avatar

Provides centralized metrics collection using prometheus_client.
Tracks system performance (latency, errors) and business metrics (PAD state, conversations).

Usage:
    from src.infrastructure.metrics import (
        track_request, track_latency, update_pad_metrics,
        REQUEST_COUNT, REQUEST_LATENCY
    )

    # In middleware
    @track_request
    async def handle_request(request):
        ...

    # In business logic
    update_pad_metrics(user_id="123", p=0.5, a=0.1, d=0.8)

Features:
    - Standard HTTP metrics (latency, counts, status codes)
    - Database connection pool metrics
    - Business metrics (PAD states, conversation turns)
    - Decorators for easy instrumentation
    - Singleton registry
"""

import time
import platform
from typing import Callable, Any
from functools import wraps

from prometheus_client import (
    Counter, Histogram, Gauge, Summary,
    CollectorRegistry, generate_latest, CONTENT_TYPE_LATEST
)

# Create a custom registry to avoid default python metrics if needed
# or use the default one for simplicity
from prometheus_client import REGISTRY

# ==============================================================================
# 1. HTTP / API Metrics
# ==============================================================================

REQUEST_COUNT = Counter(
    "http_requests_total",
    "Total HTTP requests processed",
    ["method", "path", "status"]
)

REQUEST_LATENCY = Histogram(
    "http_request_duration_seconds",
    "HTTP request latency in seconds",
    ["method", "path"],
    buckets=(0.01, 0.05, 0.1, 0.5, 1.0, 2.0, 5.0, 10.0, float("inf"))
)

REQUEST_IN_PROGRESS = Gauge(
    "http_requests_in_progress",
    "Number of HTTP requests currently being processed",
    ["method", "path"]
)

# ==============================================================================
# 2. System / Infrastructure Metrics
# ==============================================================================

DB_POOL_SIZE = Gauge(
    "db_connection_pool_size",
    "Current size of the database connection pool"
)

DB_POOL_CHECKED_OUT = Gauge(
    "db_connections_checked_out",
    "Number of database connections currently in use"
)

REDIS_CONNECTED = Gauge(
    "redis_connected",
    "Whether Redis connection is healthy (1=up, 0=down)"
)

SYSTEM_INFO = Gauge(
    "system_info",
    "System information",
    ["python_version", "platform", "app_version"]
)

# Set static system info
SYSTEM_INFO.labels(
    python_version=platform.python_version(),
    platform=platform.platform(),
    app_version="1.0.0"  # TODO: Get from config/package
).set(1)

# ==============================================================================
# 3. Business / Domain Metrics
# ==============================================================================

CONVERSATION_TURNS = Counter(
    "conversation_turns_total",
    "Total number of conversation turns processed",
    ["user_id", "model"]
)

PAD_STATE_PLEASURE = Gauge(
    "pad_state_pleasure",
    "Current Pleasure (P) value for user",
    ["user_id"]
)

PAD_STATE_AROUSAL = Gauge(
    "pad_state_arousal",
    "Current Arousal (A) value for user",
    ["user_id"]
)

PAD_STATE_DOMINANCE = Gauge(
    "pad_state_dominance",
    "Current Dominance (D) value for user",
    ["user_id"]
)

EMOTIONAL_QUADRANT = Counter(
    "emotional_quadrant_total",
    "Distribution of emotional quadrants entered",
    ["quadrant"]
)

# ==============================================================================
# 4. Decorators & Helpers
# ==============================================================================

def track_time(metric: Histogram, labels: dict = None):
    """
    Decorator to track execution time of a function in a Histogram.
    
    Args:
        metric: The Histogram metric to update.
        labels: Optional default labels.
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.perf_counter()
            try:
                result = await func(*args, **kwargs)
                return result
            finally:
                duration = time.perf_counter() - start_time
                if labels:
                    metric.labels(**labels).observe(duration)
                else:
                    metric.observe(duration)
        return wrapper
    return decorator

def update_pad_metrics(user_id: str, p: float, a: float, d: float, quadrant: str = None):
    """
    Update PAD state metrics for a specific user.
    
    Args:
        user_id: The user identifier.
        p: Pleasure value (-1.0 to 1.0).
        a: Arousal value (-1.0 to 1.0).
        d: Dominance value (-1.0 to 1.0).
        quadrant: Optional quadrant name to increment counter.
    """
    PAD_STATE_PLEASURE.labels(user_id=user_id).set(p)
    PAD_STATE_AROUSAL.labels(user_id=user_id).set(a)
    PAD_STATE_DOMINANCE.labels(user_id=user_id).set(d)
    
    if quadrant:
        EMOTIONAL_QUADRANT.labels(quadrant=quadrant).inc()

def generate_metrics_response():
    """
    Generate the metrics response for the /metrics endpoint.
    
    Returns:
        Tuple of (content, content_type)
    """
    return generate_latest(REGISTRY), CONTENT_TYPE_LATEST




