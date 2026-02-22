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

logger = structlog.get_logger(__name__)

router = APIRouter(tags=["health"])


@router.get("/health")
async def health() -> dict:
    """
    Liveness probe — returns 200 if the process is running.
    No external dependency checks.
    """
    return {"status": "healthy"}


@router.get("/ready")
async def ready() -> dict:
    """
    Readiness probe — returns 200 only when the application can serve
    traffic (database reachable).
    """
    checks: dict = {}

    # Database connectivity
    try:
        async with async_engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        checks["database"] = "ok"
    except Exception as exc:
        logger.error("readiness_db_check_failed", error=str(exc))
        checks["database"] = "unavailable"

    overall = "ready" if all(v == "ok" for v in checks.values()) else "not_ready"

    if overall != "ready":
        from fastapi.responses import JSONResponse

        return JSONResponse(
            status_code=503,
            content={"status": overall, "checks": checks},
        )

    return {"status": overall, "checks": checks}
