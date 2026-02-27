"""
Backward-compatible re-export.

Canonical location: app.infrastructure.persistence.models.user
"""

from app.infrastructure.persistence.models.user import User  # noqa: F401

__all__ = ["User"]
