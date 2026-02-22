from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
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
def start_interview_session(
    session_data: InterviewSessionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)  # Note: This returns a User object
):
    # Get user's most recent resume
    resume = db.query(Resume).filter(
        Resume.user_id == current_user.id  # Using the ID field from User object
    ).order_by(Resume.created_at.desc()).first()
    
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No resume found. Please upload a resume first."
        )

    # Create interview session
    session = InterviewSession(
        user_id=current_user.id,  # Using the ID field from User object
        resume_id=resume.id,
        started_at=datetime.now(timezone.utc)
    )
    db.add(session)
    db.commit()
    db.refresh(session)

    # Generate and persist questions
    orchestrator = InterviewOrchestrator(db)
    try:
        resume_context = orchestrator.fetch_resume_context(UUID(str(resume.id)))  # Convert Column[UUID] to UUID
        questions = orchestrator.generate_questions(session, resume_context)
        orchestrator.persist_questions(session, questions)
    except Exception as e:
        db.rollback()  # Rollback the session creation if question generation fails
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="Failed to generate questions"
        )

    return session
