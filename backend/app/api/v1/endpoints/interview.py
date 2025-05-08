from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from app.db.session import get_db
from app.models.user import User
from app.models.resume import Resume
from app.models.interview import InterviewSession, InterviewQuestion
from app.schemas.interview import (
    InterviewSessionCreate,
    InterviewSessionInDB,
    InterviewQuestionCreate,
    InterviewQuestionInDB
)
from app.api.deps import get_current_user

router = APIRouter()

@router.post("/start", response_model=InterviewSessionInDB)
async def start_interview(
    session_data: InterviewSessionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Verify resume belongs to user
    resume = db.query(Resume).filter(
        Resume.id == session_data.resume_id,
        Resume.user_id == current_user.id
    ).first()
    
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found"
        )
    
    # Create interview session
    session = InterviewSession(
        user_id=current_user.id,
        resume_id=session_data.resume_id,
        started_at=datetime.utcnow()
    )
    
    db.add(session)
    db.commit()
    db.refresh(session)
    return session

@router.post("/{session_id}/answer", response_model=InterviewQuestionInDB)
async def submit_answer(
    session_id: str,
    question_data: InterviewQuestionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Verify session belongs to user
    session = db.query(InterviewSession).filter(
        InterviewSession.id == session_id,
        InterviewSession.user_id == current_user.id
    ).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Interview session not found"
        )
    
    # Create question record
    question = InterviewQuestion(
        session_id=session_id,
        question_text=question_data.question_text,
        answer_text=question_data.answer_text
    )
    
    db.add(question)
    db.commit()
    db.refresh(question)
    return question

@router.get("/history", response_model=List[InterviewSessionInDB])
async def get_interview_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    sessions = db.query(InterviewSession).filter(
        InterviewSession.user_id == current_user.id
    ).all()
    return sessions

@router.get("/{session_id}", response_model=InterviewSessionInDB)
async def get_interview_session(
    session_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    session = db.query(InterviewSession).filter(
        InterviewSession.id == session_id,
        InterviewSession.user_id == current_user.id
    ).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Interview session not found"
        )
    
    return session 