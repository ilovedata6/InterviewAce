"""
Resume use cases — application-specific business rules for resume management.

Each use case orchestrates domain logic through repository interfaces.
"""

from __future__ import annotations

import os
import uuid

import structlog

from app.application.dto.resume import ResumeListInput, ResumeUpdateInput, ResumeUploadInput
from app.domain.entities.resume import ResumeEntity
from app.domain.exceptions import EntityNotFoundError
from app.domain.interfaces.repositories import IResumeRepository
from app.domain.value_objects.enums import FileType, ResumeStatus

logger = structlog.get_logger(__name__)


# ── Upload Resume ───────────────────────────────────────────────────────────


class UploadResumeUseCase:
    """Create a placeholder resume record and dispatch background parsing."""

    def __init__(self, resume_repo: IResumeRepository) -> None:
        self._resume_repo = resume_repo

    async def execute(self, dto: ResumeUploadInput) -> ResumeEntity:
        entity = ResumeEntity(
            user_id=dto.user_id,
            title=dto.original_filename,
            file_path=dto.file_path,
            file_name=dto.file_name,
            file_size=dto.file_size,
            file_type=FileType[dto.file_ext],
            status=ResumeStatus.PENDING,
        )
        return await self._resume_repo.create(entity)


# ── List Resumes ────────────────────────────────────────────────────────────


class ListResumesUseCase:
    """List resumes for a user with pagination and filtering."""

    def __init__(self, resume_repo: IResumeRepository) -> None:
        self._resume_repo = resume_repo

    async def execute(self, dto: ResumeListInput) -> tuple[list[ResumeEntity], int]:
        items = await self._resume_repo.get_by_user_id_filtered(
            dto.user_id,
            skip=dto.skip,
            limit=dto.limit,
            status_filter=dto.status_filter,
            search=dto.search,
        )
        total = await self._resume_repo.count_by_user_id_filtered(
            dto.user_id,
            status_filter=dto.status_filter,
            search=dto.search,
        )
        return items, total


# ── Get Resume ──────────────────────────────────────────────────────────────


class GetResumeUseCase:
    """Get a specific resume owned by the user."""

    def __init__(self, resume_repo: IResumeRepository) -> None:
        self._resume_repo = resume_repo

    async def execute(self, user_id: uuid.UUID, resume_id: uuid.UUID) -> ResumeEntity:
        entity = await self._resume_repo.get_by_id(resume_id)
        if not entity or entity.user_id != user_id:
            raise EntityNotFoundError("Resume", str(resume_id))
        return entity


# ── Update Resume ───────────────────────────────────────────────────────────


class UpdateResumeUseCase:
    """Update resume metadata (title, description)."""

    def __init__(self, resume_repo: IResumeRepository) -> None:
        self._resume_repo = resume_repo

    async def execute(self, dto: ResumeUpdateInput) -> ResumeEntity:
        entity = await self._resume_repo.get_by_id(dto.resume_id)
        if not entity or entity.user_id != dto.user_id:
            raise EntityNotFoundError("Resume", str(dto.resume_id))

        if dto.title is not None:
            entity.title = dto.title
        if dto.description is not None:
            entity.description = dto.description

        return await self._resume_repo.update(entity)


# ── Delete Resume ───────────────────────────────────────────────────────────


class DeleteResumeUseCase:
    """Delete a resume and its file from disk."""

    def __init__(self, resume_repo: IResumeRepository) -> None:
        self._resume_repo = resume_repo

    async def execute(self, user_id: uuid.UUID, resume_id: uuid.UUID) -> None:
        entity = await self._resume_repo.get_by_id(resume_id)
        if not entity or entity.user_id != user_id:
            raise EntityNotFoundError("Resume", str(resume_id))

        # Remove file from disk
        if entity.file_path and os.path.exists(entity.file_path):
            os.remove(entity.file_path)

        await self._resume_repo.delete(resume_id)
