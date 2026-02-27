"""
Domain enums — single source of truth.

These enums are imported by ORM models, Pydantic schemas, and services alike.
They live in the domain layer because they represent core business concepts.
"""

from enum import StrEnum


class ResumeStatus(StrEnum):
    """Processing status of a resume."""

    PENDING = "pending"
    PROCESSING = "processing"
    ANALYZED = "analyzed"
    ERROR = "error"


class FileType(StrEnum):
    """Allowed upload MIME types."""

    PDF = "application/pdf"
    DOCX = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    DOC = "application/msword"
    TXT = "text/plain"


class UserRole(StrEnum):
    """User roles for RBAC."""

    USER = "user"
    ADMIN = "admin"
    MODERATOR = "moderator"


class InterviewDifficulty(StrEnum):
    """Difficulty level for interview questions."""

    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"
    MIXED = "mixed"


class QuestionCategory(StrEnum):
    """Category / type of interview question."""

    TECHNICAL = "technical"
    BEHAVIORAL = "behavioral"
    PROJECT = "project"
    SYSTEM_DESIGN = "system_design"
    CODING = "coding"
    GENERAL = "general"
