"""
Domain enums — single source of truth.

These enums are imported by ORM models, Pydantic schemas, and services alike.
They live in the domain layer because they represent core business concepts.
"""

from enum import Enum


class ResumeStatus(str, Enum):
    """Processing status of a resume."""

    PENDING = "pending"
    PROCESSING = "processing"
    ANALYZED = "analyzed"
    ERROR = "error"


class FileType(str, Enum):
    """Allowed upload MIME types."""

    PDF = "application/pdf"
    DOCX = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    DOC = "application/msword"
    TXT = "text/plain"


class UserRole(str, Enum):
    """User roles for RBAC."""

    USER = "user"
    ADMIN = "admin"
    MODERATOR = "moderator"


class InterviewDifficulty(str, Enum):
    """Difficulty level for interview questions."""

    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"
    MIXED = "mixed"


class QuestionCategory(str, Enum):
    """Category / type of interview question."""

    TECHNICAL = "technical"
    BEHAVIORAL = "behavioral"
    PROJECT = "project"
    SYSTEM_DESIGN = "system_design"
    CODING = "coding"
    GENERAL = "general"
