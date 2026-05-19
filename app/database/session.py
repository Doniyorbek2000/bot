"""Database session management."""
import asyncio
from typing import AsyncGenerator
from sqlalchemy import text as sa_text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool
from tenacity import retry, stop_after_attempt, wait_fixed

from app.utils.config import settings
from app.utils.logger import logger


# Create async engine
if settings.DATABASE_URL.startswith("sqlite"):
    # SQLite doesn't support pool_size and max_overflow
    engine = create_async_engine(
        settings.database_url_async,
        echo=False,
        pool_pre_ping=True,
    )
else:
    # PostgreSQL with connection pooling
    engine = create_async_engine(
        settings.database_url_async,
        echo=False,
        pool_pre_ping=True,
        pool_size=10,
        max_overflow=20,
    )

# Session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency that provides a database session.
    
    Yields:
        AsyncSession: Database session
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


@retry(stop=stop_after_attempt(3), wait=wait_fixed(5))
async def check_db_connection() -> bool:
    """
    Check database connectivity with retry logic.
    
    Returns:
        True if connection successful
        
    Raises:
        Exception: If connection fails after 3 attempts
    """
    try:
        async with engine.connect() as conn:
            await conn.execute(sa_text("SELECT 1"))
        logger.info("Database connection successful")
        return True
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        raise


async def close_db():
    """Close database engine."""
    await engine.dispose()
    logger.info("Database connection closed")
