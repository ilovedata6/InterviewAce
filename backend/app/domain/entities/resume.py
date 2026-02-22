"""Resume domain entity — pure Python, no ORM or framework dependencies."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional

from app.domain.value_objects.enums import FileType, ResumeStatus


@dataclass
class ResumeEntity:
    """Core business representation of a resume."""

    id: uuid.UUID = field(default_factory=uuid.uuid4)
    user_id: uuid.UUID = field(default_factory=uuid.uuid4)
    title: str = ""
    description: Optional[str] = None
    file_path: str = ""
    file_name: str = ""
    file_size: int = 0
    file_type: FileType = FileType.PDF
    inferred_role: Optional[str] = None
    status: ResumeStatus = ResumeStatus.PENDING
    analysis: Optional[Dict[str, Any]] = None
    version: int = 1
    years_of_experience: Optional[int] = None
    skills: Optional[List[str]] = None
    parent_version_id: Optional[uuid.UUID] = None
    is_public: bool = False
    share_token: Optional[str] = None
    confidence_score: Optional[float] = None
    processing_time: Optional[float] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    # ------------------------------------------------------------------
    # Domain behaviour
    # ------------------------------------------------------------------

    def mark_processing(self) -> None:
        self.status = ResumeStatus.PROCESSING

    def mark_analyzed(self, analysis: Dict[str, Any], confidence: float, processing_time: float) -> None:
        self.status = ResumeStatus.ANALYZED
        self.analysis = analysis
        self.confidence_score = confidence
        self.processing_time = processing_time

    def mark_error(self) -> None:
        self.status = ResumeStatus.ERROR

    def is_analyzed(self) -> bool:
        return self.status == ResumeStatus.ANALYZED
