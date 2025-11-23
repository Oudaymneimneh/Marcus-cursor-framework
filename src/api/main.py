"""
Marcus AI Avatar - Main API Entry Point.

Configures the FastAPI application, middlewares, and routers.
"""

from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response

from src.config import get_settings
from src.infrastructure.logging import setup_logging, get_logger, LoggingMiddleware
from src.infrastructure.database import init_db, close_db, check_database_health
from src.infrastructure.redis import init_redis, close_redis, check_redis_health
from src.infrastructure.metrics import generate_metrics_response

from src.api.routes import chat

logger = get_logger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifecycle manager.
    
    Initializes resources on startup and cleans them up on shutdown.
    """
    # --- Startup ---
    setup_logging()
    logger.info("Starting Marcus AI API...")
    
    init_db()
    init_redis()
    
    yield
    
    # --- Shutdown ---
    logger.info("Shutting down Marcus AI API...")
    await close_redis()
    await close_db()


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    settings = get_settings()
    
    app = FastAPI(
        title="Marcus AI API",
        description="Stoic wisdom chatbot with behavioral intelligence",
        version="1.0.0",
        lifespan=lifespan,
        docs_url="/docs" if settings.is_development else None,
        redoc_url="/redoc" if settings.is_development else None,
    )
    
    # Middlewares
    app.add_middleware(LoggingMiddleware)
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Routers
    app.include_router(chat.router, prefix="/api/v1")
    
    # Health Check
    @app.get("/health")
    async def health_check():
        """Health check endpoint for Docker/Load Balancers."""
        db_healthy = await check_database_health()
        redis_healthy = await check_redis_health()
        
        status = "healthy" if (db_healthy and redis_healthy) else "unhealthy"
        
        return {
            "status": status,
            "services": {
                "database": "up" if db_healthy else "down",
                "redis": "up" if redis_healthy else "down",
                "openai": "configured" if get_settings().openai_api_key else "missing"
            },
            "version": "1.0.0",
            "timestamp": datetime.utcnow().isoformat()
        }
        
    # Metrics Endpoint
    @app.get("/metrics")
    async def metrics():
        """Prometheus metrics endpoint."""
        content, content_type = generate_metrics_response()
        return Response(content=content, media_type=content_type)
        
    return app

app = create_app()




