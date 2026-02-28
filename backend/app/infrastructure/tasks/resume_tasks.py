"""
Background Celery tasks for resume processing.

The heavy LLM call is moved off the HTTP thread so the upload endpoint
can return ``202 Accepted`` immediately.
"""

from __future__ import annotations

import os
import uuid

import structlog

from app.infrastructure.tasks.celery_app import celery_app

logger = structlog.get_logger(__name__)


def _get_sync_session():
    """Create a *synchronous* SQLAlchemy session for Celery workers.

    Celery workers run in their own process — they don't share the
    FastAPI async event-loop, so we need a plain sync engine.
    """
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker

    from app.core.config import settings

    engine = create_engine(settings.database_url, pool_pre_ping=True)
    session_factory = sessionmaker(bind=engine)
    return session_factory()


@celery_app.task(
    bind=True,
    name="app.infrastructure.tasks.resume_tasks.parse_resume",
    max_retries=2,
    default_retry_delay=30,
)
def parse_resume_task(self, file_path: str, user_id: str, resume_id: str):
    """
    Parse a resume file via the LLM provider chain and persist the result.

    This task is enqueued by the ``/resume/upload`` endpoint after the
    file has been saved to disk and a placeholder ``Resume`` row has been
    inserted with ``status = PENDING``.

    Parameters
    ----------
    file_path : str
        Absolute path to the uploaded file on disk.
    user_id : str
        UUID of the uploading user.
    resume_id : str
        UUID of the placeholder Resume row to update.
    """
    from sqlalchemy import select

    from app.infrastructure.llm.factory import get_llm_provider
    from app.models.resume import Resume as ResumeModel
    from app.schemas.resume import ResumeStatus

    logger.info(
        "parse_resume_task_started",
        resume_id=resume_id,
        file_path=file_path,
    )

    # Convert string UUID to proper uuid.UUID for SQLAlchemy UUID column comparison
    resume_uuid = uuid.UUID(resume_id)

    db = _get_sync_session()
    try:
        # 1. Text extraction (synchronous — CPU-bound, no async needed)
        from app.services.resume_parser import _extract_text, _validate_mandatory

        text = _extract_text(file_path)

        # 2. LLM parse (provider.parse_resume is sync)
        provider = get_llm_provider()
        parsed = provider.parse_resume(text)
        if not parsed:
            parsed = {}

        _validate_mandatory(parsed, fields=("experience", "education", "skills"))

        # 3. Update the existing Resume row
        result = db.execute(select(ResumeModel).where(ResumeModel.id == resume_uuid))
        resume = result.scalars().first()
        if not resume:
            raise ValueError(f"Resume {resume_id} not found in DB")

        resume.status = ResumeStatus.ANALYZED  # type: ignore[assignment]
        resume.analysis = parsed  # type: ignore[assignment]
        resume.skills = parsed.get("skills", [])  # type: ignore[assignment]
        resume.inferred_role = parsed.get("inferred_role")  # type: ignore[assignment]
        resume.years_of_experience = int(parsed["years_of_experience"]) if parsed.get("years_of_experience") is not None else None  # type: ignore[assignment]
        resume.confidence_score = float(parsed["confidence_score"]) if parsed.get("confidence_score") is not None else None  # type: ignore[assignment]
        resume.processing_time = float(parsed["processing_time"]) if parsed.get("processing_time") is not None else None  # type: ignore[assignment]
        resume.title = parsed.get("name") or os.path.basename(file_path)  # type: ignore[assignment]
        resume.description = parsed.get("summary")  # type: ignore[assignment]

        db.commit()

        logger.info("parse_resume_task_completed", resume_id=resume_id)
        return {"resume_id": resume_id, "status": "analyzed"}

    except Exception as exc:
        logger.error(
            "parse_resume_task_failed",
            resume_id=resume_id,
            error=str(exc),
        )
        # Mark resume as ERROR in DB
        try:
            result = db.execute(select(ResumeModel).where(ResumeModel.id == resume_uuid))
            resume = result.scalars().first()
            if resume:
                resume.status = ResumeStatus.ERROR  # type: ignore[assignment]
                db.commit()
        except Exception:
            db.rollback()

        # Retry up to max_retries
        raise self.retry(exc=exc) from exc

    finally:
        db.close()
