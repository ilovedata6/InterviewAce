"""
Admin endpoints — platform-wide analytics and user management.

All endpoints require ``UserRole.ADMIN``.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy import select, func, case
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Any, Dict, List
from uuid import UUID

from app.db.session import get_db
from app.models.user import User
from app.api.deps import require_role
from app.domain.value_objects.enums import UserRole
from app.infrastructure.persistence.models.interview import InterviewSession
from app.infrastructure.persistence.models.resume import Resume

router = APIRouter()


# ─── Platform stats ────────────────────────────────────────────────────────

@router.get(
    "/stats",
    summary="Platform-wide statistics (admin only)",
    response_description="Aggregate platform metrics.",
)
async def admin_stats(
    db: AsyncSession = Depends(get_db),
    _admin: User = Depends(require_role(UserRole.ADMIN)),
) -> Dict[str, Any]:
    """Return high-level platform statistics — total users, interviews,
    resumes, and conversion metrics."""

    user_count = await db.execute(select(func.count(User.id)))
    interview_count = await db.execute(select(func.count(InterviewSession.id)))
    completed_count = await db.execute(
        select(func.count(InterviewSession.id)).where(
            InterviewSession.completed_at.isnot(None)
        )
    )
    resume_count = await db.execute(select(func.count(Resume.id)))

    avg_score_result = await db.execute(
        select(func.avg(InterviewSession.final_score)).where(
            InterviewSession.final_score.isnot(None)
        )
    )
    avg_score = avg_score_result.scalar()

    return {
        "total_users": user_count.scalar(),
        "total_interviews": interview_count.scalar(),
        "completed_interviews": completed_count.scalar(),
        "total_resumes": resume_count.scalar(),
        "platform_avg_score": round(float(avg_score), 3) if avg_score else None,
    }


# ─── User listing ──────────────────────────────────────────────────────────

@router.get(
    "/users",
    summary="List users (admin only)",
    response_description="Paginated user list.",
)
async def admin_list_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    _admin: User = Depends(require_role(UserRole.ADMIN)),
) -> Dict[str, Any]:
    """Paginated list of users with interview/resume counts."""
    total_result = await db.execute(select(func.count(User.id)))
    total = total_result.scalar()

    users_result = await db.execute(
        select(User).order_by(User.created_at.desc()).offset(skip).limit(limit)
    )
    users = users_result.scalars().all()

    items = []
    for u in users:
        interview_cnt = await db.execute(
            select(func.count(InterviewSession.id)).where(InterviewSession.user_id == u.id)
        )
        resume_cnt = await db.execute(
            select(func.count(Resume.id)).where(Resume.user_id == u.id)
        )
        items.append(
            {
                "id": str(u.id),
                "email": u.email,
                "full_name": u.full_name,
                "role": u.role,
                "is_active": u.is_active,
                "is_verified": u.is_verified,
                "created_at": u.created_at.isoformat() if u.created_at else None,
                "interview_count": interview_cnt.scalar(),
                "resume_count": resume_cnt.scalar(),
            }
        )

    return {"items": items, "total": total, "skip": skip, "limit": limit}


# ─── User detail / management ──────────────────────────────────────────────

@router.get(
    "/users/{user_id}",
    summary="Get user detail (admin only)",
)
async def admin_get_user(
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
    _admin: User = Depends(require_role(UserRole.ADMIN)),
) -> Dict[str, Any]:
    """Return detailed information about a specific user."""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return {
        "id": str(user.id),
        "email": user.email,
        "full_name": user.full_name,
        "role": user.role,
        "is_active": user.is_active,
        "is_verified": user.is_verified,
        "created_at": user.created_at.isoformat() if user.created_at else None,
        "updated_at": user.updated_at.isoformat() if user.updated_at else None,
    }


@router.patch(
    "/users/{user_id}/deactivate",
    summary="Deactivate a user (admin only)",
    status_code=200,
)
async def admin_deactivate_user(
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
    _admin: User = Depends(require_role(UserRole.ADMIN)),
) -> Dict[str, str]:
    """Deactivate a user account — sets ``is_active = False``."""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.is_active = False
    await db.commit()
    return {"detail": f"User {user_id} deactivated."}


@router.patch(
    "/users/{user_id}/activate",
    summary="Activate a user (admin only)",
    status_code=200,
)
async def admin_activate_user(
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
    _admin: User = Depends(require_role(UserRole.ADMIN)),
) -> Dict[str, str]:
    """Reactivate a previously deactivated user account."""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.is_active = True
    await db.commit()
    return {"detail": f"User {user_id} activated."}
