from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException

from app.api.deps import get_complete_interview_uc, get_current_user
from app.application.use_cases.interview import CompleteInterviewUseCase
from app.domain.exceptions import EntityNotFoundError, InterviewError
from app.models.user import User
from app.schemas.interview import QuestionFeedback, SummaryOut

router = APIRouter()


@router.post(
    "/{session_id}/complete",
    response_model=SummaryOut,
    status_code=200,
    summary="Complete an interview session",
    response_description="Final score, AI-generated performance summary, strengths and weaknesses.",
)
async def complete_interview(
    session_id: UUID,
    current_user: User = Depends(get_current_user),
    use_case: CompleteInterviewUseCase = Depends(get_complete_interview_uc),
):
    """Mark an interview session as complete and generate the final summary.

    Returns:
        - **final_score**: overall confidence score 0-1
        - **feedback_summary**: narrative summary from the AI
        - **score_breakdown**: per-category scores (technical, behavioral, etc.)
        - **strengths / weaknesses**: bullet-point lists
        - **question_feedback**: per-question score and feedback

    Raises:
        404: Session not found or not owned by the user.
    """
    try:
        result = await use_case.execute(current_user.id, session_id)
    except EntityNotFoundError as e:
        raise HTTPException(status_code=404, detail="Session not found or not owned by user") from e
    except InterviewError as e:
        raise HTTPException(status_code=500, detail=str(e.message)) from e
    return SummaryOut(
        session_id=result.session_id,
        final_score=result.final_score,
        feedback_summary=result.feedback_summary,
        question_feedback=[
            QuestionFeedback(**fb) if isinstance(fb, dict) else fb
            for fb in result.question_feedback
        ],
        score_breakdown=result.score_breakdown,
        strengths=result.strengths,
        weaknesses=result.weaknesses,
    )
