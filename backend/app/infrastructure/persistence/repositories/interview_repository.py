"""
InterviewRepository — SQLAlchemy implementation of IInterviewRepository.

Translates between InterviewSession/InterviewQuestion ORM models and
domain entities.
"""

from __future__ import annotations

import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.domain.entities.interview import InterviewQuestionEntity, InterviewSessionEntity
from app.domain.interfaces.repositories import IInterviewRepository
from app.infrastructure.persistence.models.interview import (
    InterviewQuestion,
    InterviewSession,
)


class InterviewRepository(IInterviewRepository):
    """Concrete interview persistence backed by SQLAlchemy."""

    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    # ------------------------------------------------------------------
    # Mapping helpers — Session
    # ------------------------------------------------------------------

    @staticmethod
    def _session_to_entity(
        model: InterviewSession, *, include_questions: bool = True
    ) -> InterviewSessionEntity:
        questions = []
        if include_questions:
            try:
                questions = [
                    InterviewRepository._question_to_entity(q) for q in (model.questions or [])
                ]
            except Exception:
                questions = []
        return InterviewSessionEntity(
            id=model.id,
            user_id=model.user_id,
            resume_id=model.resume_id,
            started_at=model.started_at,
            completed_at=model.completed_at,
            final_score=model.final_score,
            feedback_summary=model.feedback_summary,
            difficulty=getattr(model, "difficulty", "mixed") or "mixed",
            question_count=getattr(model, "question_count", 12) or 12,
            focus_areas=getattr(model, "focus_areas", None),
            score_breakdown=getattr(model, "score_breakdown", None),
            questions=questions,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    @staticmethod
    def _session_to_model(entity: InterviewSessionEntity) -> InterviewSession:
        return InterviewSession(
            id=entity.id,
            user_id=entity.user_id,
            resume_id=entity.resume_id,
            started_at=entity.started_at,
            completed_at=entity.completed_at,
            final_score=entity.final_score,
            feedback_summary=entity.feedback_summary,
            difficulty=entity.difficulty,
            question_count=entity.question_count,
            focus_areas=entity.focus_areas,
            score_breakdown=entity.score_breakdown,
        )

    # ------------------------------------------------------------------
    # Mapping helpers — Question
    # ------------------------------------------------------------------

    @staticmethod
    def _question_to_entity(model: InterviewQuestion) -> InterviewQuestionEntity:
        return InterviewQuestionEntity(
            id=model.id,
            session_id=model.session_id,
            question_text=model.question_text,
            answer_text=model.answer_text,
            evaluation_score=model.evaluation_score,
            feedback_comment=model.feedback_comment,
            category=getattr(model, "category", "general") or "general",
            difficulty=getattr(model, "difficulty", "medium") or "medium",
            time_taken_seconds=getattr(model, "time_taken_seconds", None),
            order_index=getattr(model, "order_index", 0) or 0,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    @staticmethod
    def _question_to_model(entity: InterviewQuestionEntity) -> InterviewQuestion:
        return InterviewQuestion(
            id=entity.id,
            session_id=entity.session_id,
            question_text=entity.question_text,
            answer_text=entity.answer_text,
            evaluation_score=entity.evaluation_score,
            feedback_comment=entity.feedback_comment,
            category=entity.category,
            difficulty=entity.difficulty,
            time_taken_seconds=entity.time_taken_seconds,
            order_index=entity.order_index,
        )

    # ------------------------------------------------------------------
    # Interface methods — Session
    # ------------------------------------------------------------------

    async def get_session_by_id(self, session_id: uuid.UUID) -> InterviewSessionEntity | None:
        result = await self._db.execute(
            select(InterviewSession)
            .options(selectinload(InterviewSession.questions))
            .where(InterviewSession.id == session_id)
        )
        model = result.scalars().first()
        return self._session_to_entity(model) if model else None

    async def get_sessions_by_user_id(
        self,
        user_id: uuid.UUID,
        *,
        skip: int = 0,
        limit: int = 50,
    ) -> list[InterviewSessionEntity]:
        result = await self._db.execute(
            select(InterviewSession)
            .where(InterviewSession.user_id == user_id)
            .order_by(InterviewSession.started_at.desc())
            .offset(skip)
            .limit(limit)
        )
        models = result.scalars().all()
        return [self._session_to_entity(m, include_questions=False) for m in models]

    async def create_session(self, entity: InterviewSessionEntity) -> InterviewSessionEntity:
        model = self._session_to_model(entity)
        self._db.add(model)
        await self._db.commit()
        await self._db.refresh(model)
        return self._session_to_entity(model, include_questions=False)

    async def update_session(self, entity: InterviewSessionEntity) -> InterviewSessionEntity:
        result = await self._db.execute(
            select(InterviewSession).where(InterviewSession.id == entity.id)
        )
        model = result.scalars().first()
        if model is None:
            raise ValueError(f"InterviewSession {entity.id} not found")
        model.completed_at = entity.completed_at
        model.final_score = entity.final_score
        model.feedback_summary = entity.feedback_summary
        model.score_breakdown = entity.score_breakdown
        await self._db.commit()
        await self._db.refresh(model)
        return self._session_to_entity(model)

    # ------------------------------------------------------------------
    # Interface methods — Question
    # ------------------------------------------------------------------

    async def add_question(self, entity: InterviewQuestionEntity) -> InterviewQuestionEntity:
        model = self._question_to_model(entity)
        self._db.add(model)
        await self._db.commit()
        await self._db.refresh(model)
        return self._question_to_entity(model)

    async def update_question(self, entity: InterviewQuestionEntity) -> InterviewQuestionEntity:
        result = await self._db.execute(
            select(InterviewQuestion).where(InterviewQuestion.id == entity.id)
        )
        model = result.scalars().first()
        if model is None:
            raise ValueError(f"InterviewQuestion {entity.id} not found")
        model.answer_text = entity.answer_text
        model.evaluation_score = entity.evaluation_score
        model.feedback_comment = entity.feedback_comment
        model.time_taken_seconds = entity.time_taken_seconds
        await self._db.commit()
        await self._db.refresh(model)
        return self._question_to_entity(model)

    async def get_questions_by_session_id(
        self, session_id: uuid.UUID
    ) -> list[InterviewQuestionEntity]:
        result = await self._db.execute(
            select(InterviewQuestion)
            .where(InterviewQuestion.session_id == session_id)
            .order_by(InterviewQuestion.created_at)
        )
        models = result.scalars().all()
        return [self._question_to_entity(m) for m in models]

    async def count_sessions_by_user_id(self, user_id: uuid.UUID) -> int:
        result = await self._db.execute(
            select(func.count())
            .select_from(InterviewSession)
            .where(InterviewSession.user_id == user_id)
        )
        return result.scalar_one()

    async def get_next_unanswered_question(
        self, session_id: uuid.UUID
    ) -> InterviewQuestionEntity | None:
        result = await self._db.execute(
            select(InterviewQuestion)
            .where(
                InterviewQuestion.session_id == session_id,
                InterviewQuestion.answer_text.is_(None),
            )
            .order_by(InterviewQuestion.created_at)
        )
        model = result.scalars().first()
        return self._question_to_entity(model) if model else None

    async def get_question_by_id(
        self, question_id: uuid.UUID, session_id: uuid.UUID
    ) -> InterviewQuestionEntity | None:
        result = await self._db.execute(
            select(InterviewQuestion).where(
                InterviewQuestion.id == question_id,
                InterviewQuestion.session_id == session_id,
            )
        )
        model = result.scalars().first()
        return self._question_to_entity(model) if model else None
