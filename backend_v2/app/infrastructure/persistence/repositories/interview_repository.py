"""
InterviewRepository — SQLAlchemy implementation of IInterviewRepository.

Translates between InterviewSession/InterviewQuestion ORM models and
domain entities.
"""

from __future__ import annotations

import uuid
from typing import List, Optional

from sqlalchemy.orm import Session

from app.domain.entities.interview import InterviewSessionEntity, InterviewQuestionEntity
from app.domain.interfaces.repositories import IInterviewRepository
from app.infrastructure.persistence.models.interview import (
    InterviewSession,
    InterviewQuestion,
)


class InterviewRepository(IInterviewRepository):
    """Concrete interview persistence backed by SQLAlchemy."""

    def __init__(self, db: Session) -> None:
        self._db = db

    # ------------------------------------------------------------------
    # Mapping helpers — Session
    # ------------------------------------------------------------------

    @staticmethod
    def _session_to_entity(model: InterviewSession) -> InterviewSessionEntity:
        return InterviewSessionEntity(
            id=model.id,
            user_id=model.user_id,
            resume_id=model.resume_id,
            started_at=model.started_at,
            completed_at=model.completed_at,
            final_score=model.final_score,
            feedback_summary=model.feedback_summary,
            questions=[
                InterviewRepository._question_to_entity(q)
                for q in (model.questions or [])
            ],
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
        )

    # ------------------------------------------------------------------
    # Interface methods — Session
    # ------------------------------------------------------------------

    def get_session_by_id(self, session_id: uuid.UUID) -> Optional[InterviewSessionEntity]:
        model = (
            self._db.query(InterviewSession)
            .filter(InterviewSession.id == session_id)
            .first()
        )
        return self._session_to_entity(model) if model else None

    def get_sessions_by_user_id(
        self,
        user_id: uuid.UUID,
        *,
        skip: int = 0,
        limit: int = 50,
    ) -> List[InterviewSessionEntity]:
        models = (
            self._db.query(InterviewSession)
            .filter(InterviewSession.user_id == user_id)
            .order_by(InterviewSession.started_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )
        return [self._session_to_entity(m) for m in models]

    def create_session(self, entity: InterviewSessionEntity) -> InterviewSessionEntity:
        model = self._session_to_model(entity)
        self._db.add(model)
        self._db.commit()
        self._db.refresh(model)
        return self._session_to_entity(model)

    def update_session(self, entity: InterviewSessionEntity) -> InterviewSessionEntity:
        model = (
            self._db.query(InterviewSession)
            .filter(InterviewSession.id == entity.id)
            .first()
        )
        if model is None:
            raise ValueError(f"InterviewSession {entity.id} not found")
        model.completed_at = entity.completed_at
        model.final_score = entity.final_score
        model.feedback_summary = entity.feedback_summary
        self._db.commit()
        self._db.refresh(model)
        return self._session_to_entity(model)

    # ------------------------------------------------------------------
    # Interface methods — Question
    # ------------------------------------------------------------------

    def add_question(self, entity: InterviewQuestionEntity) -> InterviewQuestionEntity:
        model = self._question_to_model(entity)
        self._db.add(model)
        self._db.commit()
        self._db.refresh(model)
        return self._question_to_entity(model)

    def update_question(self, entity: InterviewQuestionEntity) -> InterviewQuestionEntity:
        model = (
            self._db.query(InterviewQuestion)
            .filter(InterviewQuestion.id == entity.id)
            .first()
        )
        if model is None:
            raise ValueError(f"InterviewQuestion {entity.id} not found")
        model.answer_text = entity.answer_text
        model.evaluation_score = entity.evaluation_score
        model.feedback_comment = entity.feedback_comment
        self._db.commit()
        self._db.refresh(model)
        return self._question_to_entity(model)

    def get_questions_by_session_id(
        self, session_id: uuid.UUID
    ) -> List[InterviewQuestionEntity]:
        models = (
            self._db.query(InterviewQuestion)
            .filter(InterviewQuestion.session_id == session_id)
            .order_by(InterviewQuestion.created_at)
            .all()
        )
        return [self._question_to_entity(m) for m in models]
