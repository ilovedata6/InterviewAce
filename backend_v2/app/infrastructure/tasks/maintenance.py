"""
Periodic maintenance tasks (Celery beat).

These tasks run on a schedule defined in ``celery_app.py``.
"""

from __future__ import annotations

import structlog
from datetime import datetime, timezone

from app.infrastructure.tasks.celery_app import celery_app

logger = structlog.get_logger(__name__)


def _get_sync_session():
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from app.core.config import settings

    engine = create_engine(settings.database_url, pool_pre_ping=True)
    Session = sessionmaker(bind=engine)
    return Session()


@celery_app.task(name="app.infrastructure.tasks.maintenance.prune_expired_tokens")
def prune_expired_tokens():
    """
    Delete ``TokenBlacklist`` rows whose ``expires_at`` is in the past.

    Redis handles its own expiry automatically, but the DB table still
    accumulates stale rows.  This task runs every hour via Celery beat.
    """
    from app.models.security import TokenBlacklist
    from sqlalchemy import delete

    db = _get_sync_session()
    try:
        result = db.execute(
            delete(TokenBlacklist).where(
                TokenBlacklist.expires_at < datetime.now(timezone.utc)
            )
        )
        deleted = result.rowcount
        db.commit()
        logger.info("prune_expired_tokens", deleted=deleted)
        return {"deleted": deleted}
    except Exception as exc:
        db.rollback()
        logger.error("prune_expired_tokens_failed", error=str(exc))
        raise
    finally:
        db.close()
