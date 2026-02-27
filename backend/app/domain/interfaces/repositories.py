"""
Repository interfaces — abstract contracts for data persistence.

Infrastructure adapters (SQLAlchemy repositories) implement these ABCs.
Domain / application layers depend only on these abstractions.
"""

from __future__ import annotations

import uuid
from abc import ABC, abstractmethod
from datetime import datetime

from app.domain.entities.interview import InterviewQuestionEntity, InterviewSessionEntity
from app.domain.entities.resume import ResumeEntity
from app.domain.entities.user import UserEntity


class IUserRepository(ABC):
    """Port for user persistence operations."""

    @abstractmethod
    async def get_by_id(self, user_id: uuid.UUID) -> UserEntity | None:
        """Return a user by primary key, or None."""
        ...

    @abstractmethod
    async def get_by_email(self, email: str) -> UserEntity | None:
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
    async def get_by_id(self, resume_id: uuid.UUID) -> ResumeEntity | None:
        """Return a resume by primary key, or None."""
        ...

    @abstractmethod
    async def get_by_user_id(
        self,
        user_id: uuid.UUID,
        *,
        skip: int = 0,
        limit: int = 50,
    ) -> list[ResumeEntity]:
        """Return all resumes belonging to a user (paginated)."""
        ...

    @abstractmethod
    async def get_by_user_id_filtered(
        self,
        user_id: uuid.UUID,
        *,
        skip: int = 0,
        limit: int = 50,
        status_filter: str | None = None,
        search: str | None = None,
    ) -> list[ResumeEntity]:
        """Return resumes belonging to a user with optional filtering."""
        ...

    @abstractmethod
    async def count_by_user_id_filtered(
        self,
        user_id: uuid.UUID,
        *,
        status_filter: str | None = None,
        search: str | None = None,
    ) -> int:
        """Count resumes for a user with optional filtering."""
        ...

    @abstractmethod
    async def get_latest_by_user_id(self, user_id: uuid.UUID) -> ResumeEntity | None:
        """Return the most recently created resume for a user, or None."""
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
    async def get_session_by_id(self, session_id: uuid.UUID) -> InterviewSessionEntity | None:
        """Return an interview session by primary key, or None."""
        ...

    @abstractmethod
    async def get_sessions_by_user_id(
        self,
        user_id: uuid.UUID,
        *,
        skip: int = 0,
        limit: int = 50,
    ) -> list[InterviewSessionEntity]:
        """Return all interview sessions for a user (paginated)."""
        ...

    @abstractmethod
    async def count_sessions_by_user_id(self, user_id: uuid.UUID) -> int:
        """Return total count of interview sessions for a user."""
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
    ) -> list[InterviewQuestionEntity]:
        """Return all questions for a session."""
        ...

    @abstractmethod
    async def get_next_unanswered_question(
        self, session_id: uuid.UUID
    ) -> InterviewQuestionEntity | None:
        """Return the next unanswered question for a session, or None."""
        ...

    @abstractmethod
    async def get_question_by_id(
        self, question_id: uuid.UUID, session_id: uuid.UUID
    ) -> InterviewQuestionEntity | None:
        """Return a specific question within a session, or None."""
        ...


class IAuthRepository(ABC):
    """Port for authentication-related persistence (login attempts, sessions, tokens)."""

    @abstractmethod
    async def count_recent_failed_attempts(
        self, user_id: uuid.UUID, ip_address: str, window_minutes: int = 5
    ) -> int:
        """Count recent failed login attempts within the time window."""
        ...

    @abstractmethod
    async def lock_login_attempts(
        self, user_id: uuid.UUID, ip_address: str, lock_duration_minutes: int = 5
    ) -> None:
        """Lock login attempts for the user/IP combination."""
        ...

    @abstractmethod
    async def record_login_attempt(
        self, user_id: uuid.UUID, ip_address: str, success: bool
    ) -> None:
        """Record a login attempt."""
        ...

    @abstractmethod
    async def get_active_session_count(self, user_id: uuid.UUID) -> int:
        """Return count of active sessions for a user."""
        ...

    @abstractmethod
    async def deactivate_oldest_session(self, user_id: uuid.UUID) -> None:
        """Deactivate the oldest active session for a user."""
        ...

    @abstractmethod
    async def create_session(
        self, user_id: uuid.UUID, ip_address: str, user_agent: str | None
    ) -> str:
        """Create a new user session. Returns the session ID."""
        ...

    @abstractmethod
    async def deactivate_session(self, session_id: str) -> None:
        """Deactivate a user session by session ID."""
        ...

    @abstractmethod
    async def create_password_reset_token(self, user_id: uuid.UUID) -> str:
        """Create and persist a password reset token. Returns the token string."""
        ...

    @abstractmethod
    async def verify_and_consume_reset_token(self, token: str) -> uuid.UUID | None:
        """Verify a reset token and mark as used. Returns user_id if valid, else None."""
        ...

    @abstractmethod
    async def blacklist_token(
        self, token_id: str, user_id: uuid.UUID, expires_at: datetime, reason: str
    ) -> None:
        """Add a JWT token to the blacklist."""
        ...

    @abstractmethod
    async def is_token_blacklisted(self, token_id: str) -> bool:
        """Check if a JWT token has been blacklisted."""
        ...
