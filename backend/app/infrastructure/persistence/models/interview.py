"""Interview ORM models — infrastructure persistence layer."""

from sqlalchemy import Column, String, UUID, ForeignKey, Float, Text, DateTime, Integer, JSON, Index
from sqlalchemy.orm import relationship
import uuid

from app.infrastructure.persistence.models.base import Base, TimestampMixin
from app.domain.value_objects.enums import InterviewDifficulty, QuestionCategory


class InterviewSession(Base, TimestampMixin):
    __tablename__ = "interview_sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    resume_id = Column(UUID(as_uuid=True), ForeignKey("resumes.id"), nullable=False)
    started_at = Column(DateTime(timezone=True), nullable=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    final_score = Column(Float, nullable=True)
    feedback_summary = Column(Text, nullable=True)

    # ── New: Interview configuration ──────────────────────────────────
    difficulty = Column(String(20), nullable=False, default=InterviewDifficulty.MIXED.value)
    question_count = Column(Integer, nullable=False, default=12)
    focus_areas = Column(JSON, nullable=True)  # e.g. ["python", "system_design"]
    score_breakdown = Column(JSON, nullable=True)  # {"technical": 0.8, "behavioral": 0.6}

    # Relationships
    resume = relationship("Resume", back_populates="interview_sessions")
    questions = relationship("InterviewQuestion", back_populates="session")

    __table_args__ = (
        Index("ix_interview_sessions_user_completed", "user_id", "completed_at"),
    )


class InterviewQuestion(Base, TimestampMixin):
    __tablename__ = "interview_questions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey("interview_sessions.id"), nullable=False, index=True)
    question_text = Column(Text, nullable=False)
    answer_text = Column(Text, nullable=True)
    evaluation_score = Column(Float, nullable=True)
    feedback_comment = Column(Text, nullable=True)

    # ── New: Question metadata ────────────────────────────────────────
    category = Column(String(30), nullable=False, default=QuestionCategory.GENERAL.value)
    difficulty = Column(String(20), nullable=False, default=InterviewDifficulty.MEDIUM.value)
    time_taken_seconds = Column(Integer, nullable=True)  # seconds the user spent answering
    order_index = Column(Integer, nullable=False, default=0)  # question order in session

    # Relationships
    session = relationship("InterviewSession", back_populates="questions")
