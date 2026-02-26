from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID

from app.domain.value_objects.enums import InterviewDifficulty, QuestionCategory


class InterviewQuestionBase(BaseModel):
    question_text: str
    answer_text: Optional[str] = None
    evaluation_score: Optional[float] = None
    feedback_comment: Optional[str] = None
    category: str = QuestionCategory.GENERAL.value
    difficulty: str = InterviewDifficulty.MEDIUM.value
    time_taken_seconds: Optional[int] = None
    order_index: int = 0

class InterviewQuestionCreate(InterviewQuestionBase):
    session_id: UUID

class InterviewQuestionInDB(InterviewQuestionBase):
    id: UUID
    session_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class InterviewSessionBase(BaseModel):
    user_id: UUID
    resume_id: UUID
    started_at: datetime
    completed_at: Optional[datetime] = None
    final_score: Optional[float] = None
    feedback_summary: Optional[str] = None
    difficulty: str = InterviewDifficulty.MIXED.value
    question_count: int = 12
    focus_areas: Optional[List[str]] = None
    score_breakdown: Optional[Dict[str, Any]] = None


class InterviewStartRequest(BaseModel):
    """Request body for starting a new interview session."""
    resume_id: Optional[UUID] = Field(None, description="Resume to use. Defaults to latest.")
    question_count: int = Field(12, ge=5, le=30, description="Number of questions to generate.")
    difficulty: str = Field(
        InterviewDifficulty.MIXED.value,
        description="Difficulty level: easy, medium, hard, mixed",
    )
    focus_areas: Optional[List[str]] = Field(
        None,
        description="Focus areas for questions, e.g. ['python', 'system_design']",
        max_length=10,
    )


class InterviewSessionCreate(BaseModel):
    resume_id: UUID

class InterviewSessionInDB(BaseModel):
    id: UUID
    user_id: UUID
    resume_id: UUID
    started_at: datetime
    completed_at: Optional[datetime] = None
    final_score: Optional[float] = None
    feedback_summary: Optional[str] = None
    difficulty: str = InterviewDifficulty.MIXED.value
    question_count: int = 12
    focus_areas: Optional[List[str]] = None
    score_breakdown: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True

class QuestionOut(BaseModel):
    question_id: UUID
    question_text: str
    category: str = QuestionCategory.GENERAL.value
    difficulty: str = InterviewDifficulty.MEDIUM.value
    order_index: int = 0

class AnswerIn(BaseModel):
    answer_text: str
    time_taken_seconds: Optional[int] = Field(None, ge=0, description="Seconds spent on this answer.")

class QuestionFeedback(BaseModel):
    question_id: UUID
    evaluation_score: float
    feedback_comment: str

class SummaryOut(BaseModel):
    session_id: UUID
    final_score: float
    feedback_summary: str
    question_feedback: List[QuestionFeedback]
    score_breakdown: Optional[Dict[str, Any]] = None
    strengths: Optional[List[str]] = None
    weaknesses: Optional[List[str]] = None