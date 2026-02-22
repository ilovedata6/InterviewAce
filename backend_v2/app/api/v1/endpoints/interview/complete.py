from fastapi import APIRouter, Depends, HTTPException, status
from uuid import UUID
from app.api.deps import get_current_user, get_complete_interview_uc
from app.models.user import User
from app.schemas.interview import SummaryOut
from app.application.use_cases.interview import CompleteInterviewUseCase
from app.domain.exceptions import EntityNotFoundError, InterviewError

router = APIRouter()

@router.post(
    "/{session_id}/complete",
    response_model=SummaryOut,
    status_code=200,
    summary="Complete an interview session",
    response_description="Final score and AI-generated performance summary.",
)
async def complete_interview(
    session_id: UUID,
    current_user: User = Depends(get_current_user),
    use_case: CompleteInterviewUseCase = Depends(get_complete_interview_uc),
):
    """Mark an interview session as complete and generate the final summary.

    Raises:
        404: Session not found or not owned by the user.
    """
    try:
        result = await use_case.execute(current_user.id, session_id)
    except EntityNotFoundError:
        raise HTTPException(status_code=404, detail="Session not found or not owned by user")
    except InterviewError as e:
        raise HTTPException(status_code=500, detail=str(e.message))
    return result
