"""
Dashboard endpoints — user statistics and analytics.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, func, case
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Any, Dict, List, Optional

from app.db.session import get_db
from app.models.user import User
from app.api.deps import get_current_user
from app.infrastructure.persistence.models.interview import InterviewSession, InterviewQuestion
from app.infrastructure.persistence.models.resume import Resume

router = APIRouter()


@router.get(
    "/stats",
    summary="Get user dashboard statistics",
    response_description="Aggregate statistics for the authenticated user.",
)
async def get_user_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    """Return key metrics for the authenticated user's dashboard:

    - Total interviews, completed interviews, average score
    - Total resumes uploaded, active resumes
    - Recent interview trend (last 5 sessions)
    """
    user_id = current_user.id

    # ── Interview statistics ────────────────────────────────────────────
    interview_stats = await db.execute(
        select(
            func.count(InterviewSession.id).label("total_interviews"),
            func.count(InterviewSession.completed_at).label("completed_interviews"),
            func.avg(
                case(
                    (InterviewSession.final_score.isnot(None), InterviewSession.final_score),
                    else_=None,
                )
            ).label("avg_score"),
            func.max(InterviewSession.final_score).label("best_score"),
        ).where(InterviewSession.user_id == user_id)
    )
    row = interview_stats.one()

    # ── Resume statistics ───────────────────────────────────────────────
    resume_stats = await db.execute(
        select(
            func.count(Resume.id).label("total_resumes"),
        ).where(Resume.user_id == user_id)
    )
    resume_row = resume_stats.one()

    # ── Recent interviews (last 5) ─────────────────────────────────────
    recent_result = await db.execute(
        select(
            InterviewSession.id,
            InterviewSession.started_at,
            InterviewSession.completed_at,
            InterviewSession.final_score,
            InterviewSession.difficulty,
        )
        .where(InterviewSession.user_id == user_id)
        .order_by(InterviewSession.started_at.desc())
        .limit(5)
    )
    recent_sessions = [
        {
            "session_id": str(r.id),
            "started_at": r.started_at.isoformat() if r.started_at else None,
            "completed_at": r.completed_at.isoformat() if r.completed_at else None,
            "final_score": r.final_score,
            "difficulty": r.difficulty,
        }
        for r in recent_result.all()
    ]

    # ── Category breakdown (for completed sessions) ─────────────────────
    category_result = await db.execute(
        select(
            InterviewQuestion.category,
            func.avg(InterviewQuestion.evaluation_score).label("avg_score"),
            func.count(InterviewQuestion.id).label("question_count"),
        )
        .join(
            InterviewSession,
            InterviewQuestion.session_id == InterviewSession.id,
        )
        .where(
            InterviewSession.user_id == user_id,
            InterviewQuestion.evaluation_score.isnot(None),
        )
        .group_by(InterviewQuestion.category)
    )
    category_breakdown = {
        r.category: {"avg_score": float(r.avg_score) if r.avg_score else 0, "count": r.question_count}
        for r in category_result.all()
    }

    return {
        "interviews": {
            "total": row.total_interviews,
            "completed": row.completed_interviews,
            "avg_score": round(float(row.avg_score), 3) if row.avg_score else None,
            "best_score": round(float(row.best_score), 3) if row.best_score else None,
        },
        "resumes": {
            "total": resume_row.total_resumes,
        },
        "recent_sessions": recent_sessions,
        "category_breakdown": category_breakdown,
    }
