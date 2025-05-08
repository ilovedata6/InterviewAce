from sqlalchemy import Column, String, UUID, ForeignKey, Float, Text, DateTime
import uuid
from app.models.base import Base, TimestampMixin

class InterviewSession(Base, TimestampMixin):
    __tablename__ = "interview_sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    resume_id = Column(UUID(as_uuid=True), ForeignKey("resumes.id"), nullable=False)
    started_at = Column(DateTime, nullable=False)
    completed_at = Column(DateTime, nullable=True)
    final_score = Column(Float, nullable=True)
    feedback_summary = Column(Text, nullable=True)

class InterviewQuestion(Base, TimestampMixin):
    __tablename__ = "interview_questions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey("interview_sessions.id"), nullable=False)
    question_text = Column(Text, nullable=False)
    answer_text = Column(Text, nullable=True)
    evaluation_score = Column(Float, nullable=True)
    feedback_comment = Column(Text, nullable=True) 