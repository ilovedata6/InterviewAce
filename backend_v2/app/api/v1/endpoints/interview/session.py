from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from app.db.session import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.interview import InterviewSessionInDB
from app.models.interview import InterviewSession

router = APIRouter()

@router.get("/{session_id}", response_model=InterviewSessionInDB)
async def get_interview_session(
    session_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(
        select(InterviewSession).where(
            InterviewSession.id == session_id,
            InterviewSession.user_id == current_user.id
        )
    )
    session = result.scalars().first()
    if not session:
        raise HTTPException(status_code=404, detail="Interview session not found")
    return session
