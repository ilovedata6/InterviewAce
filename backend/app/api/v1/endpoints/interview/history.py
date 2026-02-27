from fastapi import APIRouter, Depends, Query

from app.api.deps import get_current_user, get_history_uc
from app.application.use_cases.interview import GetHistoryUseCase
from app.models.user import User
from app.schemas.base import PaginatedResponse
from app.schemas.interview import InterviewSessionInDB

router = APIRouter()


@router.get(
    "/history",
    response_model=PaginatedResponse[InterviewSessionInDB],
    summary="List interview history",
    response_description="Paginated list of past interview sessions.",
)
async def get_interview_history(
    current_user: User = Depends(get_current_user),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(10, ge=1, le=100, description="Max records to return"),
    use_case: GetHistoryUseCase = Depends(get_history_uc),
):
    """List all interview sessions for the authenticated user.

    Supports offset-based pagination via `skip` and `limit`.
    """
    sessions, total = await use_case.execute(current_user.id, skip=skip, limit=limit)
    return PaginatedResponse(
        items=sessions,
        total=total,
        skip=skip,
        limit=limit,
        has_more=(skip + limit) < total,
    )
