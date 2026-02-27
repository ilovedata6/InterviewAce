"""
Backward-compatible re-export.

Canonical location: app.infrastructure.persistence.models.interview
"""

from app.infrastructure.persistence.models.interview import (  # noqa: F401
    InterviewQuestion,
    InterviewSession,
)

__all__ = ["InterviewSession", "InterviewQuestion"]
