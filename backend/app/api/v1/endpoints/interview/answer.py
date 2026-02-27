from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Response, status

from app.api.deps import get_current_user, get_submit_answer_uc
from app.application.dto.interview import SubmitAnswerInput
from app.application.use_cases.interview import SubmitAnswerUseCase
from app.domain.exceptions import EntityNotFoundError
from app.models.user import User
from app.schemas.interview import AnswerIn, QuestionOut

router = APIRouter()


@router.post(
    "/{session_id}/{question_id}/answer",
    status_code=200,
    summary="Submit an answer",
    response_description="The next question, or 204 if session is complete.",
)
async def answer_question(
    session_id: UUID,
    question_id: UUID,
    answer_in: AnswerIn,
    current_user: User = Depends(get_current_user),
    use_case: SubmitAnswerUseCase = Depends(get_submit_answer_uc),
):
    """Submit an answer to a specific interview question.

    Optionally includes ``time_taken_seconds`` — how long the user spent
    answering this question (tracked for analytics).

    Returns the next unanswered question or 204 No Content when all
    questions have been answered.

    Raises:
        404: Session not found or not owned by the user.
    """
    try:
        result = await use_case.execute(
            SubmitAnswerInput(
                session_id=session_id,
                question_id=question_id,
                user_id=current_user.id,
                answer_text=answer_in.answer_text,
                time_taken_seconds=answer_in.time_taken_seconds,
            )
        )
    except EntityNotFoundError as e:
        raise HTTPException(status_code=404, detail="Session not found or not owned by user") from e
    if not result:
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    return QuestionOut(
        question_id=result.question_id,
        question_text=result.question_text,
        category=result.category,
        difficulty=result.difficulty,
        order_index=result.order_index,
    )
