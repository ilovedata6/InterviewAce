"""
Backward-compatible re-export.

Canonical location: app.infrastructure.persistence.models.base
"""

from app.infrastructure.persistence.models.base import Base, TimestampMixin  # noqa: F401

__all__ = ["Base", "TimestampMixin"]