"""Resume domain entity — pure Python, no ORM or framework dependencies."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from app.domain.value_objects.enums import FileType, ResumeStatus


@dataclass
class ResumeEntity:
    """Core business representation of a resume."""

    id: uuid.UUID = field(default_factory=uuid.uuid4)
    user_id: uuid.UUID = field(default_factory=uuid.uuid4)
    title: str = ""
    description: str | None = None
    file_path: str = ""
    file_name: str = ""
    file_size: int = 0
    file_type: FileType = FileType.PDF
    inferred_role: str | None = None
    status: ResumeStatus = ResumeStatus.PENDING
    analysis: dict[str, Any] | None = None
    version: int = 1
    years_of_experience: int | None = None
    skills: list[str] | None = None
    parent_version_id: uuid.UUID | None = None
    is_public: bool = False
    share_token: str | None = None
    confidence_score: float | None = None
    processing_time: float | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    # ------------------------------------------------------------------
    # Domain behaviour
    # ------------------------------------------------------------------

    def mark_processing(self) -> None:
        self.status = ResumeStatus.PROCESSING

    def mark_analyzed(
        self, analysis: dict[str, Any], confidence: float, processing_time: float
    ) -> None:
        self.status = ResumeStatus.ANALYZED
        self.analysis = analysis
        self.confidence_score = confidence
        self.processing_time = processing_time

    def mark_error(self) -> None:
        self.status = ResumeStatus.ERROR

    def is_analyzed(self) -> bool:
        return self.status == ResumeStatus.ANALYZED
