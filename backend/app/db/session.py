from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import settings

async_engine = create_async_engine(
    settings.async_database_url,
    echo=False,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
)

AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db() -> AsyncSession:  # type: ignore[misc]
    """FastAPI dependency — yields an async SQLAlchemy session."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
