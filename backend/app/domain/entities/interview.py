"""Interview domain entities — pure Python, no ORM or framework dependencies."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional


@dataclass
class InterviewQuestionEntity:
    """A single interview question with its answer and evaluation."""

    id: uuid.UUID = field(default_factory=uuid.uuid4)
    session_id: uuid.UUID = field(default_factory=uuid.uuid4)
    question_text: str = ""
    answer_text: Optional[str] = None
    evaluation_score: Optional[float] = None
    feedback_comment: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

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
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    final_score: Optional[float] = None
    feedback_summary: Optional[str] = None
    questions: List[InterviewQuestionEntity] = field(default_factory=list)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def is_completed(self) -> bool:
        return self.completed_at is not None

    def complete(self, score: float, summary: str) -> None:
        self.completed_at = datetime.utcnow()
        self.final_score = score
        self.feedback_summary = summary

    @property
    def total_questions(self) -> int:
        return len(self.questions)

    @property
    def answered_questions(self) -> int:
        return sum(1 for q in self.questions if q.is_answered())
