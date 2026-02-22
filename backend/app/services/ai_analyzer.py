"""
AI Analyzer service — background re-analysis of a resume via the LLM provider.
"""

from __future__ import annotations

import structlog
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.llm.factory import get_llm_provider
from app.models.resume import Resume
from app.schemas.resume import ResumeStatus

logger = structlog.get_logger(__name__)


async def analyze_resume_content(resume_id: UUID, db: AsyncSession) -> None:
    """
    Background task: re-parse the resume file through the LLM provider chain
    and persist the updated analysis.
    """
    result = await db.execute(select(Resume).where(Resume.id == str(resume_id)))
    resume = result.scalars().first()
    if not resume:
        logger.error("resume_not_found", resume_id=str(resume_id))
        return

    try:
        # Extract text from the stored file
        from app.services.resume_parser import _extract_text  # local import to avoid circulars

        text = _extract_text(resume.file_path)
        provider = get_llm_provider()
        parsed = provider.parse_resume(text)

        resume.analysis = parsed
        resume.status = ResumeStatus.ANALYZED
        resume.confidence_score = parsed.get("confidence_score")
        resume.processing_time = parsed.get("processing_time")
        await db.commit()
        logger.info("resume_reanalysis_completed", resume_id=str(resume_id))

    except Exception as exc:
        logger.error("resume_reanalysis_failed", resume_id=str(resume_id), error=str(exc), exc_info=True)
        resume.status = ResumeStatus.FAILED
        await db.commit()
