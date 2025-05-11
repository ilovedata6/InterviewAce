from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
import asyncio

from app.db.session import get_db
from app.models.user import User
from app.models.resume import Resume
from app.schemas.resume import ResumeAnalysisResponse, ResumeStatus
from app.api.deps import get_current_user
from app.services.resume_parser import parse_resume
from app.services.ai_analyzer import analyze_resume_content

router = APIRouter()

@router.get("/{resume_id}", response_model=ResumeAnalysisResponse)
async def get_resume_analysis(
    resume_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get the analysis results for a specific resume."""
    resume = db.query(Resume).filter(
        Resume.id == resume_id,
        Resume.user_id == current_user.id
    ).first()
    
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found"
        )
    
    if resume.status != ResumeStatus.ANALYZED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Resume analysis is not complete. Current status: {resume.status}"
        )
    
    return ResumeAnalysisResponse(
        resume_id=str(resume.id),
        analysis=resume.analysis,
        status=resume.status,
        created_at=resume.created_at,
        processing_time=resume.processing_time,
        confidence_score=resume.confidence_score
    )

@router.post("/{resume_id}/reanalyze", response_model=ResumeAnalysisResponse)
async def reanalyze_resume(
    resume_id: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Trigger a reanalysis of the resume."""
    resume = db.query(Resume).filter(
        Resume.id == resume_id,
        Resume.user_id == current_user.id
    ).first()
    
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found"
        )
    
    # Update status to processing
    resume.status = ResumeStatus.PROCESSING
    db.commit()
    
    # Start background analysis
    background_tasks.add_task(analyze_resume_content, resume.id, db)
    
    return ResumeAnalysisResponse(
        resume_id=str(resume.id),
        analysis=resume.analysis,
        status=resume.status,
        created_at=resume.created_at,
        processing_time=resume.processing_time,
        confidence_score=resume.confidence_score
    )

@router.get("/{resume_id}/skills", response_model=List[str])
async def get_resume_skills(
    resume_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get the extracted skills from the resume."""
    resume = db.query(Resume).filter(
        Resume.id == resume_id,
        Resume.user_id == current_user.id
    ).first()
    
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found"
        )
    
    if not resume.analysis or "skills" not in resume.analysis:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Skills analysis not available"
        )
    
    return resume.analysis["skills"]

@router.get("/{resume_id}/experience", response_model=List[dict])
async def get_resume_experience(
    resume_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get the extracted work experience from the resume."""
    resume = db.query(Resume).filter(
        Resume.id == resume_id,
        Resume.user_id == current_user.id
    ).first()
    
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found"
        )
    
    if not resume.analysis or "experience" not in resume.analysis:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Experience analysis not available"
        )
    
    return resume.analysis["experience"]

@router.get("/{resume_id}/education", response_model=List[dict])
async def get_resume_education(
    resume_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get the extracted education information from the resume."""
    resume = db.query(Resume).filter(
        Resume.id == resume_id,
        Resume.user_id == current_user.id
    ).first()
    
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found"
        )
    
    if not resume.analysis or "education" not in resume.analysis:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Education analysis not available"
        )
    
    return resume.analysis["education"] 