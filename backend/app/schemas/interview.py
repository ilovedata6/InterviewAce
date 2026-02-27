from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field

from app.domain.value_objects.enums import InterviewDifficulty, QuestionCategory


class InterviewQuestionBase(BaseModel):
    question_text: str
    answer_text: str | None = None
    evaluation_score: float | None = None
    feedback_comment: str | None = None
    category: str = QuestionCategory.GENERAL.value
    difficulty: str = InterviewDifficulty.MEDIUM.value
    time_taken_seconds: int | None = None
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
    completed_at: datetime | None = None
    final_score: float | None = None
    feedback_summary: str | None = None
    difficulty: str = InterviewDifficulty.MIXED.value
    question_count: int = 12
    focus_areas: list[str] | None = None
    score_breakdown: dict[str, Any] | None = None


class InterviewStartRequest(BaseModel):
    """Request body for starting a new interview session."""

    resume_id: UUID | None = Field(None, description="Resume to use. Defaults to latest.")
    question_count: int = Field(12, ge=5, le=30, description="Number of questions to generate.")
    difficulty: str = Field(
        InterviewDifficulty.MIXED.value,
        description="Difficulty level: easy, medium, hard, mixed",
    )
    focus_areas: list[str] | None = Field(
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
    completed_at: datetime | None = None
    final_score: float | None = None
    feedback_summary: str | None = None
    difficulty: str = InterviewDifficulty.MIXED.value
    question_count: int = 12
    focus_areas: list[str] | None = None
    score_breakdown: dict[str, Any] | None = None

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
    time_taken_seconds: int | None = Field(None, ge=0, description="Seconds spent on this answer.")


class QuestionFeedback(BaseModel):
    question_id: UUID
    evaluation_score: float
    feedback_comment: str


class SummaryOut(BaseModel):
    session_id: UUID
    final_score: float
    feedback_summary: str
    question_feedback: list[QuestionFeedback]
    score_breakdown: dict[str, Any] | None = None
    strengths: list[str] | None = None
    weaknesses: list[str] | None = None
