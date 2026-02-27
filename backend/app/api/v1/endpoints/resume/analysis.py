from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.session import get_db
from app.domain.value_objects.enums import ResumeStatus
from app.models.resume import Resume
from app.models.user import User
from app.schemas.resume import ResumeAnalysisResponse
from app.services.ai_analyzer import analyze_resume_content

router = APIRouter()


@router.get("/{resume_id}", response_model=ResumeAnalysisResponse)
async def get_resume_analysis(
    resume_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get the analysis results for a specific resume."""
    result = await db.execute(
        select(Resume).where(Resume.id == resume_id, Resume.user_id == current_user.id)
    )
    resume = result.scalars().first()

    if not resume:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resume not found")

    if resume.status != ResumeStatus.ANALYZED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Resume analysis is not complete. Current status: {resume.status}",
        )

    return ResumeAnalysisResponse(
        resume_id=str(resume.id),
        analysis=resume.analysis,
        status=resume.status,
        created_at=resume.created_at,
        processing_time=resume.processing_time,
        confidence_score=resume.confidence_score,
    )


@router.post("/{resume_id}/reanalyze", response_model=ResumeAnalysisResponse)
async def reanalyze_resume(
    resume_id: str,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Trigger a reanalysis of the resume."""
    result = await db.execute(
        select(Resume).where(Resume.id == resume_id, Resume.user_id == current_user.id)
    )
    resume = result.scalars().first()

    if not resume:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resume not found")

    # Update status to processing
    resume.status = ResumeStatus.PROCESSING
    await db.commit()

    # Start background analysis
    background_tasks.add_task(analyze_resume_content, resume.id, db)

    return ResumeAnalysisResponse(
        resume_id=str(resume.id),
        analysis=resume.analysis,
        status=resume.status,
        created_at=resume.created_at,
        processing_time=resume.processing_time,
        confidence_score=resume.confidence_score,
    )


@router.get("/{resume_id}/skills", response_model=list[str])
async def get_resume_skills(
    resume_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get the extracted skills from the resume."""
    result = await db.execute(
        select(Resume).where(Resume.id == resume_id, Resume.user_id == current_user.id)
    )
    resume = result.scalars().first()

    if not resume:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resume not found")

    if not resume.analysis or "skills" not in resume.analysis:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Skills analysis not available"
        )

    return resume.analysis["skills"]


@router.get("/{resume_id}/experience", response_model=list[dict])
async def get_resume_experience(
    resume_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get the extracted work experience from the resume."""
    result = await db.execute(
        select(Resume).where(Resume.id == resume_id, Resume.user_id == current_user.id)
    )
    resume = result.scalars().first()

    if not resume:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resume not found")

    if not resume.analysis or "experience" not in resume.analysis:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Experience analysis not available"
        )

    return resume.analysis["experience"]


@router.get("/{resume_id}/education", response_model=list[dict])
async def get_resume_education(
    resume_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get the extracted education information from the resume."""
    result = await db.execute(
        select(Resume).where(Resume.id == resume_id, Resume.user_id == current_user.id)
    )
    resume = result.scalars().first()

    if not resume:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resume not found")

    if not resume.analysis or "education" not in resume.analysis:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Education analysis not available"
        )

    return resume.analysis["education"]
