from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timezone
import os

from app.db.session import get_db
from app.models.user import User
from app.models.resume import Resume
from app.schemas.resume import (
    ResumeCreate,
    ResumeUpdate,
    ResumeResponse,
    ResumeList,
    ResumeStatus
)
from app.api.deps import get_current_user
from app.core.config import settings

router = APIRouter()

@router.get("/", response_model=ResumeList)
async def list_resumes(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    status: Optional[ResumeStatus] = None,
    search: Optional[str] = None
):
    """List all resumes for the current user with pagination and filtering."""
    query = db.query(Resume).filter(Resume.user_id == current_user.id)
    
    if status:
        query = query.filter(Resume.status == status)
    
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            (Resume.title.ilike(search_term)) |
            (Resume.description.ilike(search_term))
        )
    
    total = query.count()
    resumes = query.order_by(Resume.created_at.desc()).offset(skip).limit(limit).all()
    
    return ResumeList(
        resumes=resumes,
        total=total,
        page=skip // limit + 1,
        page_size=limit,
        total_pages=(total + limit - 1) // limit
    )

@router.get("/{resume_id}", response_model=ResumeResponse)
async def get_resume(
    resume_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific resume by ID."""
    resume = db.query(Resume).filter(
        Resume.id == resume_id,
        Resume.user_id == current_user.id
    ).first()
    
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found"
        )
    
    return resume

@router.put("/{resume_id}", response_model=ResumeResponse)
async def update_resume(
    resume_id: str,
    resume_update: ResumeUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update resume metadata."""
    resume = db.query(Resume).filter(
        Resume.id == resume_id,
        Resume.user_id == current_user.id
    ).first()
    
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found"
        )
    
    # Update fields
    for field, value in resume_update.dict(exclude_unset=True).items():
        setattr(resume, field, value)
    
    resume.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(resume)
    
    return resume

@router.delete("/{resume_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_resume(
    resume_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a resume and its associated file."""
    resume = db.query(Resume).filter(
        Resume.id == resume_id,
        Resume.user_id == current_user.id
    ).first()
    
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found"
        )
    
    # Delete the file
    if os.path.exists(resume.file_path):
        os.remove(resume.file_path)
    
    # Delete the database record
    db.delete(resume)
    db.commit()