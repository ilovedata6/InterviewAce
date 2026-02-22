"""
Repository interfaces — abstract contracts for data persistence.

Infrastructure adapters (SQLAlchemy repositories) implement these ABCs.
Domain / application layers depend only on these abstractions.
"""

from __future__ import annotations

import uuid
from abc import ABC, abstractmethod
from typing import List, Optional

from app.domain.entities.user import UserEntity
from app.domain.entities.resume import ResumeEntity
from app.domain.entities.interview import InterviewSessionEntity, InterviewQuestionEntity


class IUserRepository(ABC):
    """Port for user persistence operations."""

    @abstractmethod
    async def get_by_id(self, user_id: uuid.UUID) -> Optional[UserEntity]:
        """Return a user by primary key, or None."""
        ...

    @abstractmethod
    async def get_by_email(self, email: str) -> Optional[UserEntity]:
        """Return a user by email, or None."""
        ...

    @abstractmethod
    async def create(self, entity: UserEntity) -> UserEntity:
        """Persist a new user and return the saved entity."""
        ...

    @abstractmethod
    async def update(self, entity: UserEntity) -> UserEntity:
        """Update an existing user and return the saved entity."""
        ...

    @abstractmethod
    async def delete(self, user_id: uuid.UUID) -> bool:
        """Delete a user. Return True if deleted, False if not found."""
        ...


class IResumeRepository(ABC):
    """Port for resume persistence operations."""

    @abstractmethod
    async def get_by_id(self, resume_id: uuid.UUID) -> Optional[ResumeEntity]:
        """Return a resume by primary key, or None."""
        ...

    @abstractmethod
    async def get_by_user_id(
        self,
        user_id: uuid.UUID,
        *,
        skip: int = 0,
        limit: int = 50,
    ) -> List[ResumeEntity]:
        """Return all resumes belonging to a user (paginated)."""
        ...

    @abstractmethod
    async def create(self, entity: ResumeEntity) -> ResumeEntity:
        """Persist a new resume and return the saved entity."""
        ...

    @abstractmethod
    async def update(self, entity: ResumeEntity) -> ResumeEntity:
        """Update an existing resume and return the saved entity."""
        ...

    @abstractmethod
    async def delete(self, resume_id: uuid.UUID) -> bool:
        """Delete a resume. Return True if deleted, False if not found."""
        ...

    @abstractmethod
    async def count_by_user_id(self, user_id: uuid.UUID) -> int:
        """Return total number of resumes for a user."""
        ...


class IInterviewRepository(ABC):
    """Port for interview persistence operations."""

    @abstractmethod
    async def get_session_by_id(self, session_id: uuid.UUID) -> Optional[InterviewSessionEntity]:
        """Return an interview session by primary key, or None."""
        ...

    @abstractmethod
    async def get_sessions_by_user_id(
        self,
        user_id: uuid.UUID,
        *,
        skip: int = 0,
        limit: int = 50,
    ) -> List[InterviewSessionEntity]:
        """Return all interview sessions for a user (paginated)."""
        ...

    @abstractmethod
    async def create_session(self, entity: InterviewSessionEntity) -> InterviewSessionEntity:
        """Persist a new interview session and return the saved entity."""
        ...

    @abstractmethod
    async def update_session(self, entity: InterviewSessionEntity) -> InterviewSessionEntity:
        """Update an existing interview session."""
        ...

    @abstractmethod
    async def add_question(self, entity: InterviewQuestionEntity) -> InterviewQuestionEntity:
        """Persist a new interview question and return the saved entity."""
        ...

    @abstractmethod
    async def update_question(self, entity: InterviewQuestionEntity) -> InterviewQuestionEntity:
        """Update an existing interview question."""
        ...

    @abstractmethod
    async def get_questions_by_session_id(
        self, session_id: uuid.UUID
    ) -> List[InterviewQuestionEntity]:
        """Return all questions for a session."""
        ...
