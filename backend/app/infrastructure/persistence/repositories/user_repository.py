"""
UserRepository — SQLAlchemy implementation of IUserRepository.

Translates between the User ORM model and the UserEntity domain object.
"""

from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.user import UserEntity
from app.domain.interfaces.repositories import IUserRepository
from app.infrastructure.persistence.models.user import User


class UserRepository(IUserRepository):
    """Concrete user persistence backed by SQLAlchemy."""

    def __init__(self, db: AsyncSession) -> None:
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

    async def get_by_id(self, user_id: uuid.UUID) -> UserEntity | None:
        result = await self._db.execute(select(User).where(User.id == user_id))
        model = result.scalars().first()
        return self._to_entity(model) if model else None

    async def get_by_email(self, email: str) -> UserEntity | None:
        result = await self._db.execute(select(User).where(User.email == email))
        model = result.scalars().first()
        return self._to_entity(model) if model else None

    async def create(self, entity: UserEntity) -> UserEntity:
        model = self._to_model(entity)
        self._db.add(model)
        await self._db.commit()
        await self._db.refresh(model)
        return self._to_entity(model)

    async def update(self, entity: UserEntity) -> UserEntity:
        result = await self._db.execute(select(User).where(User.id == entity.id))
        model = result.scalars().first()
        if model is None:
            raise ValueError(f"User {entity.id} not found")
        model.full_name = entity.full_name
        model.email = entity.email
        model.hashed_password = entity.hashed_password
        model.is_active = entity.is_active
        model.is_email_verified = entity.is_email_verified
        await self._db.commit()
        await self._db.refresh(model)
        return self._to_entity(model)

    async def delete(self, user_id: uuid.UUID) -> bool:
        result = await self._db.execute(select(User).where(User.id == user_id))
        model = result.scalars().first()
        if model is None:
            return False
        await self._db.delete(model)
        await self._db.commit()
        return True
