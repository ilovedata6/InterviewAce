"""
Redis client — single async connection pool shared across the application.

Usage::

    from app.infrastructure.cache.redis_client import get_redis, redis_client

    # Inside an async function:
    r = await get_redis()
    await r.set("key", "value", ex=300)
    val = await r.get("key")

    # Graceful shutdown (called from main.py lifespan):
    await redis_client.close()
"""

from __future__ import annotations

import structlog
from redis.asyncio import Redis

from app.core.config import settings

logger = structlog.get_logger(__name__)

# Module-level singleton — lazily connected on first use
_redis: Redis | None = None


async def get_redis() -> Redis:
    """Return the shared async Redis client, creating it lazily."""
    global _redis
    if _redis is None:
        _redis = Redis.from_url(
            settings.REDIS_URL,
            decode_responses=True,
            socket_connect_timeout=5,
            retry_on_timeout=True,
        )
        logger.info("redis_connected", url=settings.REDIS_URL)
    return _redis


async def close_redis() -> None:
    """Gracefully close the Redis connection pool."""
    global _redis
    if _redis is not None:
        await _redis.close()
        _redis = None
        logger.info("redis_closed")


class RedisTokenBlacklist:
    """
    Redis-backed token blacklist.

    Each revoked JTI is stored as a Redis key with a TTL equal to the
    remaining token lifetime.  This avoids growing a database table
    forever and removes the need for periodic pruning.
    """

    PREFIX = "token:blacklist:"

    @staticmethod
    async def revoke(token_id: str, ttl_seconds: int, reason: str = "logout") -> None:
        """Add a JTI to the blacklist with automatic expiry."""
        r = await get_redis()
        key = f"{RedisTokenBlacklist.PREFIX}{token_id}"
        await r.set(key, reason, ex=max(ttl_seconds, 1))
        logger.info("token_revoked_redis", token_id=token_id, ttl=ttl_seconds)

    @staticmethod
    async def is_revoked(token_id: str) -> bool:
        """Return True if the JTI is in the blacklist."""
        r = await get_redis()
        key = f"{RedisTokenBlacklist.PREFIX}{token_id}"
        return await r.exists(key) > 0


class RedisRateLimit:
    """
    Thin helper used by SlowAPI's custom storage backend (see middleware).
    Not used directly — SlowAPI handles all rate-limit logic.
    This class is retained for any future manual rate-limit checks.
    """

    PREFIX = "ratelimit:"

    @staticmethod
    async def check(identifier: str, limit: int, window: int) -> tuple[bool, int]:
        """
        Sliding-window counter.

        Returns (allowed: bool, remaining: int).
        """
        r = await get_redis()
        key = f"{RedisRateLimit.PREFIX}{identifier}"
        current = await r.incr(key)
        if current == 1:
            await r.expire(key, window)
        remaining = max(limit - current, 0)
        return current <= limit, remaining
