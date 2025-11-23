"""
Database Connection Management for Marcus AI Avatar

Provides async database connectivity using SQLAlchemy 2.0 with asyncpg driver.
All operations are async for production performance with connection pooling.

Usage:
    from fastapi import Depends
    from sqlalchemy.ext.asyncio import AsyncSession
    from src.infrastructure.database import get_db, init_db, close_db

    # In FastAPI lifespan
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        init_db()
        yield
        await close_db()

    # In route handlers
    @app.get("/example")
    async def example(db: AsyncSession = Depends(get_db)):
        result = await db.execute(text("SELECT 1"))
        return result.scalar()

Features:
    - Async connection pooling with configurable size
    - Automatic session management (commit/rollback)
    - Health check for monitoring
    - Graceful shutdown with connection cleanup
"""

import logging
from typing import AsyncGenerator, Optional

from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from src.config import get_settings

logger = logging.getLogger(__name__)

# Global engine and session factory (initialized in init_db)
_engine: Optional[AsyncEngine] = None
_session_factory: Optional[async_sessionmaker[AsyncSession]] = None


def get_engine() -> AsyncEngine:
    """
    Get or create async database engine.

    Creates a singleton AsyncEngine instance configured with connection pooling
    from application settings. The engine is created on first call and reused
    for subsequent calls.

    Returns:
        AsyncEngine: SQLAlchemy async engine for database operations.

    Raises:
        RuntimeError: If engine creation fails due to configuration issues.

    Example:
        >>> engine = get_engine()
        >>> async with engine.connect() as conn:
        ...     result = await conn.execute(text("SELECT 1"))
    """
    global _engine

    if _engine is None:
        settings = get_settings()

        # Ensure we have an async-compatible URL
        db_url = settings.database_url
        if not ("+asyncpg" in db_url or "+aiopg" in db_url):
            db_url = db_url.replace("postgresql://", "postgresql+asyncpg://")

        _engine = create_async_engine(
            db_url,
            pool_size=settings.database_pool_size,
            max_overflow=settings.database_max_overflow,
            pool_pre_ping=True,  # Verify connections before use
            echo=settings.database_echo,
        )

        logger.info(
            "Database engine created",
            extra={
                "pool_size": settings.database_pool_size,
                "max_overflow": settings.database_max_overflow,
                "echo": settings.database_echo,
            },
        )

    return _engine


def get_session_factory() -> async_sessionmaker[AsyncSession]:
    """
    Get or create async session factory.

    Creates a singleton session factory configured for async operations.
    The factory is initialized with the async engine and configured to
    prevent lazy loading issues.

    Returns:
        async_sessionmaker[AsyncSession]: Factory for creating database sessions.

    Example:
        >>> factory = get_session_factory()
        >>> async with factory() as session:
        ...     result = await session.execute(text("SELECT 1"))
    """
    global _session_factory

    if _session_factory is None:
        engine = get_engine()
        _session_factory = async_sessionmaker(
            bind=engine,
            class_=AsyncSession,
            expire_on_commit=False,  # Prevent lazy loading issues
            autocommit=False,
            autoflush=False,
        )
        logger.debug("Session factory created")

    return _session_factory


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency that provides database session.

    Yields a database session that automatically commits on success
    and rolls back on error. Ensures proper session cleanup regardless
    of outcome.

    Yields:
        AsyncSession: Database session for executing queries.

    Raises:
        SQLAlchemyError: If database operations fail.

    Example:
        >>> from fastapi import Depends
        >>> @app.get("/users")
        ... async def get_users(db: AsyncSession = Depends(get_db)):
        ...     result = await db.execute(text("SELECT * FROM users"))
        ...     return result.fetchall()
    """
    session_factory = get_session_factory()
    session = session_factory()

    try:
        yield session
        await session.commit()
        logger.debug("Session committed successfully")
    except SQLAlchemyError as e:
        await session.rollback()
        logger.error(
            "Database error, session rolled back",
            extra={"error": str(e), "error_type": type(e).__name__},
        )
        raise
    except Exception as e:
        await session.rollback()
        logger.error(
            "Unexpected error, session rolled back",
            extra={"error": str(e), "error_type": type(e).__name__},
        )
        raise
    finally:
        await session.close()
        logger.debug("Session closed")


async def check_database_health() -> bool:
    """
    Test database connectivity with a simple query.

    Executes SELECT 1 to verify the database is reachable and responsive.
    Used by health check endpoints for monitoring.

    Returns:
        bool: True if database is healthy and responsive, False otherwise.

    Example:
        >>> healthy = await check_database_health()
        >>> if not healthy:
        ...     logger.error("Database health check failed")
    """
    try:
        engine = get_engine()
        async with engine.connect() as conn:
            result = await conn.execute(text("SELECT 1 AS health_check"))
            row = result.fetchone()
            if row and row[0] == 1:
                logger.debug("Database health check passed")
                return True
            return False
    except SQLAlchemyError as e:
        logger.error(
            "Database health check failed",
            extra={"error": str(e), "error_type": type(e).__name__},
        )
        return False
    except Exception as e:
        logger.error(
            "Unexpected error during health check",
            extra={"error": str(e), "error_type": type(e).__name__},
        )
        return False


def init_db() -> None:
    """
    Initialize database connections on application startup.

    Creates the database engine and session factory. Should be called
    once during application startup (e.g., in FastAPI lifespan).

    Example:
        >>> from contextlib import asynccontextmanager
        >>> @asynccontextmanager
        ... async def lifespan(app: FastAPI):
        ...     init_db()
        ...     yield
        ...     await close_db()
    """
    settings = get_settings()

    # Initialize engine and session factory
    engine = get_engine()
    get_session_factory()

    logger.info(
        "Database initialized",
        extra={
            "database_url": _mask_password(settings.database_url),
            "pool_size": settings.database_pool_size,
            "max_overflow": settings.database_max_overflow,
        },
    )


async def close_db() -> None:
    """
    Close all database connections on application shutdown.

    Disposes of the engine and closes all pooled connections.
    Should be called during application shutdown.

    Example:
        >>> from contextlib import asynccontextmanager
        >>> @asynccontextmanager
        ... async def lifespan(app: FastAPI):
        ...     init_db()
        ...     yield
        ...     await close_db()
    """
    global _engine, _session_factory

    if _engine is not None:
        await _engine.dispose()
        logger.info("Database engine disposed, all connections closed")
        _engine = None
        _session_factory = None


def _mask_password(url: str) -> str:
    """
    Mask password in database URL for safe logging.

    Args:
        url: Database connection URL.

    Returns:
        URL with password replaced by asterisks.
    """
    import re

    # Match pattern: ://user:password@
    return re.sub(r"(://[^:]+:)[^@]+(@)", r"\1****\2", url)


async def execute_raw_sql(sql: str, params: Optional[dict] = None) -> list:
    """
    Execute raw SQL query and return results.

    Utility function for executing arbitrary SQL queries outside
    of the normal session dependency flow.

    Args:
        sql: SQL query string.
        params: Optional dictionary of query parameters.

    Returns:
        List of result rows.

    Raises:
        SQLAlchemyError: If query execution fails.

    Example:
        >>> rows = await execute_raw_sql(
        ...     "SELECT * FROM users WHERE id = :id",
        ...     {"id": 1}
        ... )
    """
    engine = get_engine()
    async with engine.connect() as conn:
        if params:
            result = await conn.execute(text(sql), params)
        else:
            result = await conn.execute(text(sql))
        return result.fetchall()
