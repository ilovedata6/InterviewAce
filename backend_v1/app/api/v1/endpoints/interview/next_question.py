from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session
from uuid import UUID
from app.db.session import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.interview import QuestionOut
from app.services.interview_orchestrator import get_user_session, get_next_question

router = APIRouter()

@router.get("/{session_id}/next", response_model=QuestionOut, status_code=200)
def get_next_question_route(
    session_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Get session and check ownership
    session = get_user_session(db, current_user, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found or not owned by user")

    question = get_next_question(db, session)
    if not question:
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    question_id = question.id
    if not isinstance(question_id, UUID):
        question_id = UUID(str(question_id))
    return QuestionOut(question_id=question_id, question_text=str(question.question_text))
