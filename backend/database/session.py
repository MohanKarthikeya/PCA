"""
Async SQLAlchemy engine and session factory.
Uses aiosqlite for non-blocking SQLite access.
"""

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from config.settings import get_settings

settings = get_settings()

# Create the async engine — connect_args keeps WAL mode enabled for SQLite
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    connect_args={"check_same_thread": False},
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency that yields a database session and guarantees cleanup.
    Usage:
        db: AsyncSession = Depends(get_db)
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


async def create_tables() -> None:
    """Create all tables defined in ORM models (used at startup)."""
    # Import models here so Base.metadata is populated before create_all
    import models  # noqa: F401  – side-effect import

    from database.base import Base

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
