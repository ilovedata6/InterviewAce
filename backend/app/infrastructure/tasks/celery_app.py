"""
Celery application configuration.

Start the worker with::

    # Linux / macOS (default prefork pool)
    celery -A app.infrastructure.tasks.celery_app worker --loglevel=info

    # Windows (prefork is broken — use solo or threads pool)
    celery -A app.infrastructure.tasks.celery_app worker --loglevel=info --pool=solo

Start the beat scheduler (optional — for periodic cleanup)::

    celery -A app.infrastructure.tasks.celery_app beat --loglevel=info
"""

from __future__ import annotations

from celery import Celery

from app.core.config import settings

celery_app = Celery(
    "interview_ace",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
)

celery_app.conf.update(
    # ── Serialisation ──────────────────────────────────────────────────────
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    # ── Time / timezone ────────────────────────────────────────────────────
    timezone="UTC",
    enable_utc=True,
    # ── Result backend ─────────────────────────────────────────────────────
    result_expires=3600,  # results kept for 1 hour
    # ── Reliability ────────────────────────────────────────────────────────
    task_acks_late=True,
    worker_prefetch_multiplier=1,  # one task at a time per worker
    # ── Auto-discover tasks in infrastructure.tasks ────────────────────────
    imports=["app.infrastructure.tasks.resume_tasks"],
    # ── Beat schedule (periodic cleanup) ───────────────────────────────────
    beat_schedule={
        "prune-expired-blacklist-tokens": {
            "task": "app.infrastructure.tasks.maintenance.prune_expired_tokens",
            "schedule": 3600.0,  # every hour
        },
    },
)
