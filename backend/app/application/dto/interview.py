"""Interview DTOs — data transfer objects for interview use case boundaries."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from uuid import UUID


@dataclass(frozen=True)
class StartInterviewInput:
    user_id: UUID
    resume_id: Optional[UUID] = None  # None = use latest resume
    question_count: int = 12
    difficulty: str = "mixed"  # easy | medium | hard | mixed
    focus_areas: Optional[List[str]] = None  # e.g. ["python", "system_design"]


@dataclass(frozen=True)
class SubmitAnswerInput:
    user_id: UUID
    session_id: UUID
    question_id: UUID
    answer_text: str
    time_taken_seconds: Optional[int] = None  # seconds the user spent answering


@dataclass(frozen=True)
class QuestionResult:
    question_id: UUID
    question_text: str
    category: str = "general"
    difficulty: str = "medium"
    order_index: int = 0


@dataclass
class InterviewSummaryResult:
    session_id: UUID
    final_score: float
    feedback_summary: str
    question_feedback: List[dict] = field(default_factory=list)
    score_breakdown: Optional[Dict[str, Any]] = None
    strengths: Optional[List[str]] = None
    weaknesses: Optional[List[str]] = None
