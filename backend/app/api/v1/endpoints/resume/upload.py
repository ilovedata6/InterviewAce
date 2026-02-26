from fastapi import APIRouter, Depends, HTTPException, Request, status, UploadFile, File
import uuid, os

import structlog

from app.schemas.resume import ResumeUploadResponse
from app.utils.file_handler import save_upload_file, validate_file
from app.api.deps import get_current_user, get_upload_resume_uc
from app.core.config import settings
from app.core.middleware import limiter
from app.schemas.resume import ResumeStatus, FileType
from app.application.use_cases.resume import UploadResumeUseCase
from app.application.dto.resume import ResumeUploadInput

router = APIRouter()

logger = structlog.get_logger(__name__)


def _dispatch_celery_task(file_path: str, user_id: str, resume_id: str) -> str | None:
    """Try to dispatch Celery task; return task_id or None if broker unavailable."""
    try:
        from app.infrastructure.tasks.resume_tasks import parse_resume_task
        task = parse_resume_task.delay(
            file_path=file_path,
            user_id=user_id,
            resume_id=resume_id,
        )
        return task.id
    except Exception as exc:
        logger.warning(
            "celery_dispatch_failed_falling_back_to_sync",
            error=str(exc),
            resume_id=resume_id,
        )
        return None


async def _sync_parse_fallback(file_path: str, resume_id: str) -> None:
    """Synchronous fallback: parse resume in-process when Celery is unavailable."""
    from app.infrastructure.llm.factory import get_llm_provider
    from app.services.resume_parser import _extract_text
    from app.infrastructure.persistence.models.resume import Resume as ResumeModel
    from sqlalchemy import select, create_engine
    from sqlalchemy.orm import sessionmaker

    logger.info("sync_parse_fallback_started", resume_id=resume_id)

    engine = create_engine(settings.database_url, pool_pre_ping=True)
    Session = sessionmaker(bind=engine)
    db = Session()

    try:
        text = _extract_text(file_path)
        provider = get_llm_provider()
        parsed = provider.parse_resume(text)
        if not parsed:
            parsed = {}

        result = db.execute(select(ResumeModel).where(ResumeModel.id == resume_id))
        resume = result.scalars().first()
        if not resume:
            raise ValueError(f"Resume {resume_id} not found in DB")

        resume.status = ResumeStatus.ANALYZED
        resume.analysis = parsed
        resume.skills = parsed.get("skills", [])
        resume.inferred_role = parsed.get("inferred_role")
        resume.years_of_experience = parsed.get("years_of_experience")
        resume.confidence_score = parsed.get("confidence_score")
        resume.processing_time = parsed.get("processing_time")
        resume.title = parsed.get("name") or os.path.basename(file_path)
        resume.description = parsed.get("summary")
        db.commit()
        logger.info("sync_parse_fallback_completed", resume_id=resume_id)

    except Exception as exc:
        logger.error("sync_parse_fallback_failed", resume_id=resume_id, error=str(exc))
        try:
            result = db.execute(select(ResumeModel).where(ResumeModel.id == resume_id))
            resume = result.scalars().first()
            if resume:
                resume.status = ResumeStatus.ERROR
                db.commit()
        except Exception:
            db.rollback()
    finally:
        db.close()
        engine.dispose()


@router.post(
    "/",
    response_model=ResumeUploadResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Upload a resume",
    response_description="Accepted — resume ID and background task ID for polling.",
)
@limiter.limit("10/minute")
async def upload_resume(
    request: Request,
    file: UploadFile = File(...),
    current_user=Depends(get_current_user),
    use_case: UploadResumeUseCase = Depends(get_upload_resume_uc),
):
    """
    Upload a resume file.

    The file is saved to disk, a placeholder ``Resume`` row is created
    with ``status = PENDING``, and a Celery background task is dispatched
    to parse the resume via the LLM provider chain.

    If Celery/Redis is unavailable, falls back to synchronous parsing
    so the feature still works in development without a worker running.

    Returns **202 Accepted** with the resume ID and Celery task ID so
    the client can poll ``GET /tasks/{task_id}`` for progress.
    """

    # 1. Validate file type & size
    try:
        validate_file(file, allowed_extensions={"pdf", "docx"})
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("validation_error")
        raise HTTPException(status_code=400, detail=str(e))

    # 2. Save file with unique name
    if not file.filename:
        raise HTTPException(status_code=400, detail="Uploaded file must have a filename.")
    file_ext = file.filename.rsplit(".", 1)[-1].upper()
    unique_name = f"{uuid.uuid4()}.{file.filename.split('.')[-1]}"
    upload_path = os.path.join(settings.UPLOAD_DIR, unique_name)
    try:
        save_upload_file(file, upload_path)
    except Exception as e:
        logger.exception("save_upload_failed")
        raise HTTPException(status_code=500, detail="Could not save file.")

    # 3. Create placeholder Resume row via use case
    resume = await use_case.execute(
        ResumeUploadInput(
            user_id=current_user.id,
            file_path=upload_path,
            file_name=unique_name,
            original_filename=file.filename,
            file_size=os.path.getsize(upload_path),
            file_ext=file_ext,
        )
    )

    # 4. Dispatch Celery background task (with sync fallback)
    task_id = _dispatch_celery_task(
        file_path=upload_path,
        user_id=str(current_user.id),
        resume_id=str(resume.id),
    )

    message = f"Resume accepted for processing. Track progress with task_id: {task_id}"
    if task_id is None:
        # Celery unavailable — parse synchronously
        await _sync_parse_fallback(upload_path, str(resume.id))
        message = "Resume processed synchronously (Celery unavailable)."
        task_id = None

    logger.info(
        "resume_upload_complete",
        resume_id=str(resume.id),
        task_id=task_id,
        mode="celery" if task_id else "sync_fallback",
    )

    # 5. Return 202 Accepted
    return ResumeUploadResponse(
        id=str(resume.id),
        file_name=unique_name,
        status=ResumeStatus.PENDING if task_id else ResumeStatus.ANALYZED,
        file_size=resume.file_size,
        message=message,
        file_type=FileType[file_ext],
        task_id=task_id,
    )
