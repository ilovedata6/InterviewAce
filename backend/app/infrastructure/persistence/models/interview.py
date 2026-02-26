"""Interview ORM models — infrastructure persistence layer."""

from sqlalchemy import Column, String, UUID, ForeignKey, Float, Text, DateTime
from sqlalchemy.orm import relationship
import uuid

from app.infrastructure.persistence.models.base import Base, TimestampMixin


class InterviewSession(Base, TimestampMixin):
    __tablename__ = "interview_sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    resume_id = Column(UUID(as_uuid=True), ForeignKey("resumes.id"), nullable=False)
    started_at = Column(DateTime(timezone=True), nullable=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    final_score = Column(Float, nullable=True)
    feedback_summary = Column(Text, nullable=True)

    # Relationships
    resume = relationship("Resume", back_populates="interview_sessions")
    questions = relationship("InterviewQuestion", back_populates="session")


class InterviewQuestion(Base, TimestampMixin):
    __tablename__ = "interview_questions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey("interview_sessions.id"), nullable=False)
    question_text = Column(Text, nullable=False)
    answer_text = Column(Text, nullable=True)
    evaluation_score = Column(Float, nullable=True)
    feedback_comment = Column(Text, nullable=True)

    # Relationships
    session = relationship("InterviewSession", back_populates="questions")
