from fastapi import APIRouter, Depends, HTTPException
from uuid import UUID
from app.api.deps import get_current_user, get_summary_uc
from app.models.user import User
from app.application.use_cases.interview import GetSummaryUseCase
from app.domain.exceptions import EntityNotFoundError

router = APIRouter()

@router.get(
    "/{session_id}/summary",
    response_model=dict,
    status_code=200,
    summary="Get interview summary",
    response_description="AI-generated performance summary and per-question feedback.",
)
async def get_interview_summary_route(
    session_id: UUID,
    current_user: User = Depends(get_current_user),
    use_case: GetSummaryUseCase = Depends(get_summary_uc),
):
    """Retrieve the AI-generated summary for a completed interview session.

    Raises:
        404: Session not found or not owned by the user.
    """
    try:
        return await use_case.execute(current_user.id, session_id)
    except EntityNotFoundError:
        raise HTTPException(status_code=404, detail="Session not found or not owned by user")
