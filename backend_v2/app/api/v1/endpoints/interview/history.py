from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.interview import InterviewSessionInDB
from app.schemas.base import PaginatedResponse
from app.models.interview import InterviewSession
from typing import List

router = APIRouter()

@router.get(
    "/history",
    response_model=PaginatedResponse[InterviewSessionInDB],
    summary="List interview history",
    response_description="Paginated list of past interview sessions.",
)
async def get_interview_history(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(10, ge=1, le=100, description="Max records to return"),
):
    """List all interview sessions for the authenticated user.

    Supports offset-based pagination via `skip` and `limit`.
    """
    # Total count
    count_result = await db.execute(
        select(func.count())
        .select_from(InterviewSession)
        .where(InterviewSession.user_id == current_user.id)
    )
    total = count_result.scalar_one()

    # Paginated query
    result = await db.execute(
        select(InterviewSession)
        .where(InterviewSession.user_id == current_user.id)
        .order_by(InterviewSession.started_at.desc())
        .offset(skip)
        .limit(limit)
    )
    sessions = result.scalars().all()

    return PaginatedResponse(
        items=sessions,
        total=total,
        skip=skip,
        limit=limit,
        has_more=(skip + limit) < total,
    )
