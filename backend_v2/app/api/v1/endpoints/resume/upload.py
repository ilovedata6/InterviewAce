from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
import uuid, os

from app.schemas.resume import ResumeUploadResponse
from app.services.resume_parser import parse_and_store_resume
from app.utils.file_handler import save_upload_file, validate_file
from app.db.session import get_db
from app.core.security import get_current_user
from app.core.config import settings
from app.schemas.resume import ResumeStatus,FileType
import logging

router = APIRouter()

logger = logging.getLogger(__name__)

@router.post(
    "/",
    response_model=ResumeUploadResponse,
    status_code=status.HTTP_201_CREATED
)
async def upload_resume(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    #  Validate file type & size
    try:
        validate_file(file, allowed_extensions={"pdf", "docx"})
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Validation error")
        raise HTTPException(status_code=400, detail=str(e))

    #  Save file with unique name
    if not file.filename:
        raise HTTPException(status_code=400, detail="Uploaded file must have a filename.")
    unique_name = f"{uuid.uuid4()}.{file.filename.split('.')[-1]}"
    upload_path = os.path.join(settings.UPLOAD_DIR, unique_name)
    try:
        save_upload_file(file, upload_path)
    except Exception as e:
        logger.exception("Failed to save upload")
        raise HTTPException(status_code=500, detail="Could not save file.")

    # Delegate to service for parsing & DB persistence
    try:
        resume_record = await parse_and_store_resume(
            file_path=upload_path,
            user_id=current_user.id,
            db=db
        )
    except HTTPException:
        # Raised if mandatory fields missing, etc.
        raise
    except Exception as e:
        logger.exception("Parsing/storage failed")
        raise HTTPException(status_code=500, detail="Failed to process resume.")

    #  Build response
    return ResumeUploadResponse(
        id=str(resume_record.id),
        file_name=unique_name,
        status=ResumeStatus.ANALYZED,
        file_size=os.path.getsize(upload_path),
        message="Resume uploaded and parsed successfully.",
        file_type= FileType.PDF if (file.filename and file.filename.endswith('.pdf')) else FileType.DOCX
    )
