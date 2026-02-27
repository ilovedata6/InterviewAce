# app/services/resume_parser.py

import os
from typing import Any

import docx
import pdfplumber
import structlog
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.interfaces.llm_provider import ILLMProvider
from app.infrastructure.llm.factory import get_llm_provider
from app.models.resume import Resume as ResumeModel
from app.schemas.resume import FileType, ResumeStatus

logger = structlog.get_logger(__name__)


# ─── Public API ────────────────────────────────────────────────────────────────
async def parse_and_store_resume(
    file_path: str,
    user_id: int,
    db: AsyncSession,
    llm_provider: ILLMProvider | None = None,
) -> ResumeModel:
    """
    Orchestrates:
      1) Text extraction
      2) LLM parse (primary → fallback via provider chain)
      3) Mandatory field validation
      4) ORM mapping & persistence
    """
    provider = llm_provider or get_llm_provider()

    text = _extract_text(file_path)
    parsed = provider.parse_resume(text)
    if not parsed:
        logger.warning("llm_parse_empty_result", file_path=file_path)
        parsed = {}

    _validate_mandatory(parsed, fields=("experience", "education", "skills"))

    resume = _map_to_model(parsed, user_id, file_path)
    db.add(resume)
    await db.commit()
    await db.refresh(resume)
    return resume


# ─── Internal Helpers ──────────────────────────────────────────────────────────
def _extract_text(file_path: str) -> str:
    ext = file_path.rsplit(".", 1)[-1].lower()
    if ext == "pdf":
        with pdfplumber.open(file_path) as pdf:
            return "\n".join(page.extract_text() or "" for page in pdf.pages)
    elif ext == "docx":
        doc = docx.Document(file_path)
        return "\n".join(p.text for p in doc.paragraphs)
    else:
        raise ValueError(f"Unsupported extension for parsing: .{ext}")


def _validate_mandatory(parsed: dict[str, Any], fields: tuple):
    for f in fields:
        val = parsed.get(f)
        if not val:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Mandatory field '{f}' is missing or empty.",
            )


def _map_to_model(parsed: dict[str, Any], user_id: int, file_path: str) -> ResumeModel:
    return ResumeModel(
        user_id=user_id,
        title=parsed.get("name") or os.path.basename(file_path),
        description=parsed.get("summary"),  # if you generate one
        file_path=file_path,
        inferred_role=parsed.get("inferred_role"),
        file_name=os.path.basename(file_path),
        file_size=os.path.getsize(file_path),
        skills=parsed.get("skills", []),
        file_type=FileType[file_path.rsplit(".", 1)[-1].upper()],
        status=ResumeStatus.ANALYZED,
        analysis=parsed,  # your parsed dict
        years_of_experience=parsed.get("years_of_experience"),
        confidence_score=parsed.get("confidence_score"),
        processing_time=parsed.get("processing_time"),
    )
