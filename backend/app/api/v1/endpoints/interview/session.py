from fastapi import APIRouter, Depends, HTTPException
from uuid import UUID
from app.api.deps import get_current_user, get_session_uc
from app.models.user import User
from app.schemas.interview import InterviewSessionInDB
from app.application.use_cases.interview import GetSessionUseCase
from app.domain.exceptions import EntityNotFoundError

router = APIRouter()

@router.get(
    "/{session_id}",
    response_model=InterviewSessionInDB,
    summary="Get interview session",
    response_description="Interview session details.",
)
async def get_interview_session(
    session_id: UUID,
    current_user: User = Depends(get_current_user),
    use_case: GetSessionUseCase = Depends(get_session_uc),
):
    """Retrieve a specific interview session by ID.

    Raises:
        404: Session not found or not owned by the user.
    """
    try:
        session = await use_case.execute(current_user.id, session_id)
    except EntityNotFoundError:
        raise HTTPException(status_code=404, detail="Interview session not found")
    return session
