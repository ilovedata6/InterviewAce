from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timedelta
import uuid

from app.db.session import get_db
from app.models.user import User
from app.models.resume import Resume
from app.schemas.resume import ResumeShareRequest, ResumeShareResponse, ResumeResponse
from app.api.deps import get_current_user
from app.core.security import generate_share_token
from app.core.config import settings

router = APIRouter()

@router.post("/{resume_id}/share", response_model=ResumeShareResponse)
async def share_resume(
    resume_id: str,
    share_request: ResumeShareRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Share a resume with others."""
    resume = db.query(Resume).filter(
        Resume.id == resume_id,
        Resume.user_id == current_user.id
    ).first()
    
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found"
        )
    
    # Generate share token
    share_token = generate_share_token()
    
    # Calculate expiry date if specified
    expiry_date = None
    if share_request.expiry_days:
        expiry_date = datetime.utcnow() + timedelta(days=share_request.expiry_days)
    
    # Update resume sharing settings
    resume.is_public = share_request.is_public
    resume.share_token = share_token
    db.commit()
    
    # Generate share URL
    share_url = f"{settings.FRONTEND_URL}/resume/shared/{share_token}"
    
    return ResumeShareResponse(
        share_token=share_token,
        share_url=share_url,
        expiry_date=expiry_date,
        is_public=share_request.is_public
    )

@router.get("/shared/{share_token}", response_model=ResumeResponse)
async def get_shared_resume(
    share_token: str,
    db: Session = Depends(get_db)
):
    """Get a shared resume using the share token."""
    resume = db.query(Resume).filter(Resume.share_token == share_token).first()
    
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Shared resume not found"
        )
    
    if not resume.is_public:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This resume is not publicly shared"
        )
    
    return resume

@router.post("/{resume_id}/unshare", status_code=status.HTTP_204_NO_CONTENT)
async def unshare_resume(
    resume_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Remove sharing settings from a resume."""
    resume = db.query(Resume).filter(
        Resume.id == resume_id,
        Resume.user_id == current_user.id
    ).first()
    
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found"
        )
    
    # Remove sharing settings
    resume.is_public = False
    resume.share_token = None
    db.commit()

@router.get("/{resume_id}/share-status", response_model=ResumeShareResponse)
async def get_share_status(
    resume_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get the current sharing status of a resume."""
    resume = db.query(Resume).filter(
        Resume.id == resume_id,
        Resume.user_id == current_user.id
    ).first()
    
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found"
        )
    
    share_url = None
    if resume.share_token:
        share_url = f"{settings.FRONTEND_URL}/resume/shared/{resume.share_token}"
    
    return ResumeShareResponse(
        share_token=resume.share_token,
        share_url=share_url,
        expiry_date=None,  # We don't store expiry date in the database
        is_public=resume.is_public
    ) 