"""Interview DTOs — data transfer objects for interview use case boundaries."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional
from uuid import UUID


@dataclass(frozen=True)
class StartInterviewInput:
    user_id: UUID


@dataclass(frozen=True)
class SubmitAnswerInput:
    user_id: UUID
    session_id: UUID
    question_id: UUID
    answer_text: str


@dataclass(frozen=True)
class QuestionResult:
    question_id: UUID
    question_text: str


@dataclass
class InterviewSummaryResult:
    session_id: UUID
    final_score: float
    feedback_summary: str
    question_feedback: List[dict] = field(default_factory=list)
