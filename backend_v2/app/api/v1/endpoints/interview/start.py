from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from datetime import datetime, timezone
from app.db.session import get_db
from app.models.interview import InterviewSession
from app.models.resume import Resume
from app.schemas.interview import InterviewSessionCreate, InterviewSessionInDB
from app.services.interview_orchestrator import InterviewOrchestrator
from app.core.security import get_current_user
from app.models.user import User  # Import the User model

router = APIRouter()

@router.post("", response_model=InterviewSessionInDB)
async def start_interview_session(
    session_data: InterviewSessionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)  # Note: This returns a User object
):
    # Get user's most recent resume
    result = await db.execute(
        select(Resume)
        .where(Resume.user_id == current_user.id)
        .order_by(Resume.created_at.desc())
    )
    resume = result.scalars().first()
    
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No resume found. Please upload a resume first."
        )

    # Create interview session
    session = InterviewSession(
        user_id=current_user.id,
        resume_id=resume.id,
        started_at=datetime.now(timezone.utc)
    )
    db.add(session)
    await db.commit()
    await db.refresh(session)

    # Generate and persist questions
    orchestrator = InterviewOrchestrator(db)
    try:
        resume_context = await orchestrator.fetch_resume_context(UUID(str(resume.id)))
        questions = orchestrator.generate_questions(session, resume_context)
        await orchestrator.persist_questions(session, questions)
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="Failed to generate questions"
        )

    return session
