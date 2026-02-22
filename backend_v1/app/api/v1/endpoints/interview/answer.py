from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session
from uuid import UUID
from app.db.session import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.interview import AnswerIn, QuestionOut
from app.services.interview_orchestrator import get_user_session, submit_answer

router = APIRouter()

@router.post("/{session_id}/{question_id}/answer", status_code=200)
def answer_question(
    session_id: UUID,
    question_id: UUID,
    answer_in: AnswerIn,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    session = get_user_session(db, current_user, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found or not owned by user")
    next_question = submit_answer(db, session, question_id, answer_in.answer_text)
    if not next_question:
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    from uuid import UUID
    question_id_val = next_question.id
    if not isinstance(question_id_val, UUID):
        question_id_val = UUID(str(question_id_val))
    return QuestionOut(question_id=question_id_val, question_text=str(next_question.question_text))
