import ssl as _ssl

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import settings

# ── Engine kwargs ──────────────────────────────────────────────────────────
_engine_kwargs: dict = {
    "echo": False,
    "pool_pre_ping": True,
    "pool_size": 10,
    "max_overflow": 20,
}

# Neon (and most cloud Postgres) requires SSL.
# asyncpg needs an explicit ssl context when sslmode=require is in the URL.
if "sslmode=require" in settings.async_database_url:
    _ssl_ctx = _ssl.create_default_context()
    _ssl_ctx.check_hostname = False
    _ssl_ctx.verify_mode = _ssl.CERT_NONE
    _engine_kwargs["connect_args"] = {"ssl": _ssl_ctx}

async_engine = create_async_engine(
    settings.async_database_url,
    **_engine_kwargs,
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
