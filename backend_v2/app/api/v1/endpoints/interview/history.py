from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.interview import InterviewSessionInDB
from app.models.interview import InterviewSession
from typing import List

router = APIRouter()

@router.get("/history", response_model=List[InterviewSessionInDB])
async def get_interview_history(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(
        select(InterviewSession)
        .where(InterviewSession.user_id == current_user.id)
        .order_by(InterviewSession.started_at.desc())
    )
    sessions = result.scalars().all()
    return sessions
