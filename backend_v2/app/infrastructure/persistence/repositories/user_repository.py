"""
UserRepository — SQLAlchemy implementation of IUserRepository.

Translates between the User ORM model and the UserEntity domain object.
"""

from __future__ import annotations

import uuid
from typing import Optional

from sqlalchemy.orm import Session

from app.domain.entities.user import UserEntity
from app.domain.interfaces.repositories import IUserRepository
from app.infrastructure.persistence.models.user import User


class UserRepository(IUserRepository):
    """Concrete user persistence backed by SQLAlchemy."""

    def __init__(self, db: Session) -> None:
        self._db = db

    # ------------------------------------------------------------------
    # Mapping helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _to_entity(model: User) -> UserEntity:
        return UserEntity(
            id=model.id,
            full_name=model.full_name,
            email=model.email,
            hashed_password=model.hashed_password,
            is_active=model.is_active,
            is_email_verified=model.is_email_verified,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    @staticmethod
    def _to_model(entity: UserEntity) -> User:
        return User(
            id=entity.id,
            full_name=entity.full_name,
            email=entity.email,
            hashed_password=entity.hashed_password,
            is_active=entity.is_active,
            is_email_verified=entity.is_email_verified,
        )

    # ------------------------------------------------------------------
    # Interface methods
    # ------------------------------------------------------------------

    def get_by_id(self, user_id: uuid.UUID) -> Optional[UserEntity]:
        model = self._db.query(User).filter(User.id == user_id).first()
        return self._to_entity(model) if model else None

    def get_by_email(self, email: str) -> Optional[UserEntity]:
        model = self._db.query(User).filter(User.email == email).first()
        return self._to_entity(model) if model else None

    def create(self, entity: UserEntity) -> UserEntity:
        model = self._to_model(entity)
        self._db.add(model)
        self._db.commit()
        self._db.refresh(model)
        return self._to_entity(model)

    def update(self, entity: UserEntity) -> UserEntity:
        model = self._db.query(User).filter(User.id == entity.id).first()
        if model is None:
            raise ValueError(f"User {entity.id} not found")
        model.full_name = entity.full_name
        model.email = entity.email
        model.hashed_password = entity.hashed_password
        model.is_active = entity.is_active
        model.is_email_verified = entity.is_email_verified
        self._db.commit()
        self._db.refresh(model)
        return self._to_entity(model)

    def delete(self, user_id: uuid.UUID) -> bool:
        model = self._db.query(User).filter(User.id == user_id).first()
        if model is None:
            return False
        self._db.delete(model)
        self._db.commit()
        return True
