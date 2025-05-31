from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID
from app.db.session import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.interview import SummaryOut
from app.services.interview_orchestrator import get_user_session, complete_interview_session

router = APIRouter()

@router.post("/{session_id}/complete", response_model=SummaryOut, status_code=200)
def complete_interview(
    session_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    session = get_user_session(db, current_user, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found or not owned by user")
    return complete_interview_session(db, session)
