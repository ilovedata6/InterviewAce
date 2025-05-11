from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
import os
import shutil
import magic
from datetime import datetime, timezone
import uuid

from app.db.session import get_db
from app.models.user import User
from app.models.resume import Resume
from app.schemas.resume import ResumeUploadResponse, ResumeStatus, FileType
from app.api.deps import get_current_user
from app.core.config import settings
from app.core.security import generate_share_token
from app.services.resume_parser import parse_resume
from app.utils.file_utils import validate_file_size, get_file_extension

router = APIRouter()

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
ALLOWED_EXTENSIONS = {'.pdf', '.docx', '.doc', '.txt'}

async def validate_resume_file(file: UploadFile) -> None:
    """Validate resume file type and size."""
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No file provided"
        )
    
    file_ext = get_file_extension(file.filename)
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type not allowed. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"
        )
    
    # Check file size
    file_size = 0
    chunk_size = 1024 * 1024  # 1MB chunks
    while chunk := await file.read(chunk_size):
        file_size += len(chunk)
        if file_size > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File size exceeds maximum limit of {MAX_FILE_SIZE/1024/1024}MB"
            )
    await file.seek(0)  # Reset file pointer

async def process_resume_file(
    file: UploadFile,
    resume_id: uuid.UUID,
    db: Session
) -> None:
    """Process resume file in background."""
    try:
        # Update status to processing
        resume = db.query(Resume).filter(Resume.id == resume_id).first()
        if not resume:
            return
        
        resume.status = ResumeStatus.PROCESSING
        db.commit()

        # Parse resume
        analysis_result = await parse_resume(file)
        
        # Update resume with analysis
        resume.analysis = analysis_result
        resume.status = ResumeStatus.ANALYZED
        resume.description = description or ""
        resume.confidence_score = analysis_result.get('confidence_score', 0.0)
        resume.processing_time = analysis_result.get('processing_time', 0.0)
        resume.extracted_data = analysis_result.get('content', {})
        resume.inferred_role = analysis_result.get('summary', {}).get('target_role')
        resume.experience_level = analysis_result.get('summary', {}).get('experience_level')
        resume.analysis_metadata = {
            "parser_version": settings.RESUME_PARSER_VERSION,
            "analysis_date": datetime.now(timezone.utc).isoformat(),
            "parser_engine": analysis_result.get('parser_engine', 'default')
        }
        
        db.commit()
    except Exception as e:
        # Update status to error
        resume = db.query(Resume).filter(Resume.id == resume_id).first()
        if resume:
            resume.status = ResumeStatus.ERROR
            db.commit()
        raise e

@router.post("/", response_model=ResumeUploadResponse)
async def upload_resume(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    description: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Upload a new resume file."""
    # Validate file
    await validate_resume_file(file)
    
    # Create uploads directory if it doesn't exist
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    
    # Generate unique filename
    file_ext = get_file_extension(file.filename)
    unique_filename = f"{current_user.id}_{uuid.uuid4()}{file_ext}"
    file_path = os.path.join(settings.UPLOAD_DIR, unique_filename)
    
    # Save the file
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Get file type using python-magic
    mime = magic.Magic(mime=True)
    file_type = mime.from_file(file_path)
    
    # Create resume record
    resume = Resume(
        user_id=current_user.id,
        title=file.filename,
        description="",  # Initialize empty description
        file_path=file_path,
        file_name=file.filename,
        file_size=os.path.getsize(file_path),
        file_type=FileType(file_type),
        status=ResumeStatus.PENDING,
        version=1,
        parent_version_id=None,
        analysis_metadata={"parser_version": "1.0"}
    )
    
    db.add(resume)
    db.commit()
    db.refresh(resume)
    
    # Start background processing
    background_tasks.add_task(process_resume_file, file, resume.id, db)
    
    return ResumeUploadResponse(
        id=str(resume.id),
        file_name=resume.file_name,
        status=resume.status,
        message="Resume uploaded successfully and is being processed",
        file_size=resume.file_size,
        file_type=resume.file_type,
        version=resume.version,
        description=resume.description,
        confidence_score=resume.confidence_score,
        processing_time=resume.processing_time
    )