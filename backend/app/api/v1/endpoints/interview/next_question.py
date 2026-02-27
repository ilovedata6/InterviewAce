from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Response, status

from app.api.deps import get_current_user, get_next_question_uc
from app.application.use_cases.interview import GetNextQuestionUseCase
from app.domain.exceptions import EntityNotFoundError
from app.models.user import User
from app.schemas.interview import QuestionOut

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
    current_user: User = Depends(get_current_user),
    use_case: GetNextQuestionUseCase = Depends(get_next_question_uc),
):
    """Retrieve the next unanswered question in the interview session.

    Returns 204 No Content when all questions have been answered.

    Raises:
        404: Session not found or not owned by the user.
    """
    try:
        result = await use_case.execute(current_user.id, session_id)
    except EntityNotFoundError as e:
        raise HTTPException(status_code=404, detail="Session not found or not owned by user") from e
    if not result:
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    return QuestionOut(question_id=result.question_id, question_text=result.question_text)
