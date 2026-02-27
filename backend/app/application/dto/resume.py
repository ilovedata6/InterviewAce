"""Resume DTOs — data transfer objects for resume use case boundaries."""

from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class ResumeUploadInput:
    user_id: UUID
    file_path: str
    file_name: str
    original_filename: str
    file_size: int
    file_ext: str


@dataclass(frozen=True)
class ResumeUpdateInput:
    user_id: UUID
    resume_id: UUID
    title: str | None = None
    description: str | None = None


@dataclass(frozen=True)
class ResumeListInput:
    user_id: UUID
    skip: int = 0
    limit: int = 10
    status_filter: str | None = None
    search: str | None = None
