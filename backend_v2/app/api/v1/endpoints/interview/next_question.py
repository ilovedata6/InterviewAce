from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from app.db.session import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.interview import QuestionOut
from app.services.interview_orchestrator import get_user_session, get_next_question

router = APIRouter()

@router.get(
    "/{session_id}/next",
    response_model=QuestionOut,
    status_code=200,
    summary="Get next question",
    response_description="The next unanswered question, or 204 if none remain.",
)
async def get_next_question_route(
    session_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retrieve the next unanswered question in the interview session.

    Returns 204 No Content when all questions have been answered.

    Raises:
        404: Session not found or not owned by the user.
    """
    # Get session and check ownership
    session = await get_user_session(db, current_user, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found or not owned by user")

    question = await get_next_question(db, session)
    if not question:
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    question_id = question.id
    if not isinstance(question_id, UUID):
        question_id = UUID(str(question_id))
    return QuestionOut(question_id=question_id, question_text=str(question.question_text))
