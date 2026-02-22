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
from app.infrastructure.tasks.resume_tasks import parse_resume_task

router = APIRouter()

logger = structlog.get_logger(__name__)


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

    # 4. Dispatch Celery background task
    task = parse_resume_task.delay(
        file_path=upload_path,
        user_id=str(current_user.id),
        resume_id=str(resume.id),
    )
    logger.info(
        "resume_task_dispatched",
        resume_id=str(resume.id),
        task_id=task.id,
    )

    # 5. Return 202 Accepted
    return ResumeUploadResponse(
        id=str(resume.id),
        file_name=unique_name,
        status=ResumeStatus.PENDING,
        file_size=resume.file_size,
        message=f"Resume accepted for processing. Track progress with task_id: {task.id}",
        file_type=FileType[file_ext],
        task_id=task.id,
    )
