"""
SQLAlchemy ORM models — infrastructure persistence layer.

These models map directly to database tables.
Import them from here or via the backward-compatible ``app.models`` package.
"""

from app.infrastructure.persistence.models.base import Base, TimestampMixin
from app.infrastructure.persistence.models.user import User
from app.infrastructure.persistence.models.resume import Resume
from app.infrastructure.persistence.models.interview import InterviewSession, InterviewQuestion
from app.infrastructure.persistence.models.security import (
    LoginAttempt,
    TokenBlacklist,
    UserSession,
    PasswordHistory,
    PasswordResetToken,
)

__all__ = [
    "Base",
    "TimestampMixin",
    "User",
    "Resume",
    "InterviewSession",
    "InterviewQuestion",
    "LoginAttempt",
    "TokenBlacklist",
    "UserSession",
    "PasswordHistory",
    "PasswordResetToken",
]
