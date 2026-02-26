"""
Health-check endpoints — /health (liveness) and /ready (readiness).

These endpoints are excluded from authentication and rate limiting.
They are mounted directly on the app (no /api/v1 prefix) so that
load-balancers and orchestrators can probe them without API versioning.
"""

from __future__ import annotations

import structlog
from fastapi import APIRouter
from sqlalchemy import text

from app.db.session import async_engine
from app.infrastructure.cache.redis_client import get_redis

logger = structlog.get_logger(__name__)

router = APIRouter(tags=["health"])


@router.get(
    "/health",
    summary="Liveness probe",
    response_description="Service is alive.",
)
async def health() -> dict:
    """Liveness probe — returns 200 if the process is running.

    No external dependency checks.
    """
    return {"status": "healthy"}


@router.get(
    "/ready",
    summary="Readiness probe",
    response_description="Service readiness status with dependency checks.",
)
async def ready() -> dict:
    """Readiness probe — returns 200 only when the application can serve
    traffic (database + Redis reachable). Returns 503 otherwise.

    Also provides informational checks for Celery and LLM provider
    (these are non-blocking — degraded but still "ready").
    """
    checks: dict = {}

    # ── Database connectivity (critical) ────────────────────────────────
    try:
        async with async_engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        checks["database"] = "ok"
    except Exception as exc:
        logger.error("readiness_db_check_failed", error=str(exc))
        checks["database"] = "unavailable"

    # ── Redis connectivity (critical) ───────────────────────────────────
    try:
        r = await get_redis()
        await r.ping()
        checks["redis"] = "ok"
    except Exception as exc:
        logger.error("readiness_redis_check_failed", error=str(exc))
        checks["redis"] = "unavailable"

    # ── Celery / broker connectivity (informational) ────────────────────
    try:
        from app.core.config import settings
        import redis as sync_redis

        r_sync = sync_redis.from_url(settings.REDIS_URL, socket_connect_timeout=2)
        r_sync.ping()
        checks["celery_broker"] = "ok"
        r_sync.close()
    except Exception as exc:
        logger.warning("readiness_celery_check_failed", error=str(exc))
        checks["celery_broker"] = "unavailable"

    # ── LLM provider availability (informational) ──────────────────────
    try:
        from app.infrastructure.llm.factory import get_llm_provider

        provider = get_llm_provider()
        checks["llm_provider"] = "ok"
    except Exception as exc:
        logger.warning("readiness_llm_check_failed", error=str(exc))
        checks["llm_provider"] = "unavailable"

    # Critical checks: database + redis
    critical_ok = checks.get("database") == "ok" and checks.get("redis") == "ok"
    overall = "ready" if critical_ok else "not_ready"

    if overall != "ready":
        from fastapi.responses import JSONResponse

        return JSONResponse(
            status_code=503,
            content={"status": overall, "checks": checks},
        )

    return {"status": overall, "checks": checks}
