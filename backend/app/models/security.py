"""
Backward-compatible re-export.

Canonical location: app.infrastructure.persistence.models.security
"""

from app.infrastructure.persistence.models.security import (  # noqa: F401
    LoginAttempt,
    PasswordHistory,
    PasswordResetToken,
    TokenBlacklist,
    UserSession,
)

__all__ = [
    "LoginAttempt",
    "TokenBlacklist",
    "UserSession",
    "PasswordHistory",
    "PasswordResetToken",
]
