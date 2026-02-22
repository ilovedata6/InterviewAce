"""
ResumeRepository — SQLAlchemy implementation of IResumeRepository.

Translates between the Resume ORM model and the ResumeEntity domain object.
"""

from __future__ import annotations

import uuid
from typing import List, Optional

from sqlalchemy.orm import Session

from app.domain.entities.resume import ResumeEntity
from app.domain.interfaces.repositories import IResumeRepository
from app.infrastructure.persistence.models.resume import Resume


class ResumeRepository(IResumeRepository):
    """Concrete resume persistence backed by SQLAlchemy."""

    def __init__(self, db: Session) -> None:
        self._db = db

    # ------------------------------------------------------------------
    # Mapping helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _to_entity(model: Resume) -> ResumeEntity:
        return ResumeEntity(
            id=model.id,
            user_id=model.user_id,
            title=model.title,
            description=model.description,
            file_path=model.file_path,
            file_name=model.file_name,
            file_size=model.file_size,
            file_type=model.file_type,
            inferred_role=model.inferred_role,
            status=model.status,
            analysis=model.analysis,
            version=model.version,
            years_of_experience=model.years_of_experience,
            skills=model.skills,
            parent_version_id=model.parent_version_id,
            is_public=model.is_public,
            share_token=model.share_token,
            confidence_score=model.confidence_score,
            processing_time=model.processing_time,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    @staticmethod
    def _to_model(entity: ResumeEntity) -> Resume:
        return Resume(
            id=entity.id,
            user_id=entity.user_id,
            title=entity.title,
            description=entity.description,
            file_path=entity.file_path,
            file_name=entity.file_name,
            file_size=entity.file_size,
            file_type=entity.file_type,
            inferred_role=entity.inferred_role,
            status=entity.status,
            analysis=entity.analysis,
            version=entity.version,
            years_of_experience=entity.years_of_experience,
            skills=entity.skills,
            parent_version_id=entity.parent_version_id,
            is_public=entity.is_public,
            share_token=entity.share_token,
            confidence_score=entity.confidence_score,
            processing_time=entity.processing_time,
        )

    # ------------------------------------------------------------------
    # Interface methods
    # ------------------------------------------------------------------

    def get_by_id(self, resume_id: uuid.UUID) -> Optional[ResumeEntity]:
        model = self._db.query(Resume).filter(Resume.id == resume_id).first()
        return self._to_entity(model) if model else None

    def get_by_user_id(
        self,
        user_id: uuid.UUID,
        *,
        skip: int = 0,
        limit: int = 50,
    ) -> List[ResumeEntity]:
        models = (
            self._db.query(Resume)
            .filter(Resume.user_id == user_id)
            .order_by(Resume.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )
        return [self._to_entity(m) for m in models]

    def create(self, entity: ResumeEntity) -> ResumeEntity:
        model = self._to_model(entity)
        self._db.add(model)
        self._db.commit()
        self._db.refresh(model)
        return self._to_entity(model)

    def update(self, entity: ResumeEntity) -> ResumeEntity:
        model = self._db.query(Resume).filter(Resume.id == entity.id).first()
        if model is None:
            raise ValueError(f"Resume {entity.id} not found")
        model.title = entity.title
        model.description = entity.description
        model.inferred_role = entity.inferred_role
        model.status = entity.status
        model.analysis = entity.analysis
        model.version = entity.version
        model.years_of_experience = entity.years_of_experience
        model.skills = entity.skills
        model.is_public = entity.is_public
        model.share_token = entity.share_token
        model.confidence_score = entity.confidence_score
        model.processing_time = entity.processing_time
        self._db.commit()
        self._db.refresh(model)
        return self._to_entity(model)

    def delete(self, resume_id: uuid.UUID) -> bool:
        model = self._db.query(Resume).filter(Resume.id == resume_id).first()
        if model is None:
            return False
        self._db.delete(model)
        self._db.commit()
        return True

    def count_by_user_id(self, user_id: uuid.UUID) -> int:
        return self._db.query(Resume).filter(Resume.user_id == user_id).count()
