"""Interview domain entities — pure Python, no ORM or framework dependencies."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any


@dataclass
class InterviewQuestionEntity:
    """A single interview question with its answer and evaluation."""

    id: uuid.UUID = field(default_factory=uuid.uuid4)
    session_id: uuid.UUID = field(default_factory=uuid.uuid4)
    question_text: str = ""
    answer_text: str | None = None
    evaluation_score: float | None = None
    feedback_comment: str | None = None
    category: str = "general"
    difficulty: str = "medium"
    time_taken_seconds: int | None = None
    order_index: int = 0
    created_at: datetime | None = None
    updated_at: datetime | None = None

    def is_answered(self) -> bool:
        return self.answer_text is not None

    def is_evaluated(self) -> bool:
        return self.evaluation_score is not None


@dataclass
class InterviewSessionEntity:
    """A complete mock-interview session."""

    id: uuid.UUID = field(default_factory=uuid.uuid4)
    user_id: uuid.UUID = field(default_factory=uuid.uuid4)
    resume_id: uuid.UUID = field(default_factory=uuid.uuid4)
    started_at: datetime | None = None
    completed_at: datetime | None = None
    final_score: float | None = None
    feedback_summary: str | None = None
    difficulty: str = "mixed"
    question_count: int = 12
    focus_areas: list[str] | None = None
    score_breakdown: dict[str, Any] | None = None
    questions: list[InterviewQuestionEntity] = field(default_factory=list)
    created_at: datetime | None = None
    updated_at: datetime | None = None

    def is_completed(self) -> bool:
        return self.completed_at is not None

    def complete(
        self, score: float, summary: str, score_breakdown: dict[str, Any] | None = None
    ) -> None:
        self.completed_at = datetime.now(UTC)
        self.final_score = score
        self.feedback_summary = summary
        if score_breakdown:
            self.score_breakdown = score_breakdown

    @property
    def total_questions(self) -> int:
        return len(self.questions)

    @property
    def answered_questions(self) -> int:
        return sum(1 for q in self.questions if q.is_answered())
