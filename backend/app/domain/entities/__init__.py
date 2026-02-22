"""Domain entities — pure business objects with no framework dependencies."""

from app.domain.entities.user import UserEntity
from app.domain.entities.resume import ResumeEntity
from app.domain.entities.interview import InterviewSessionEntity, InterviewQuestionEntity

__all__ = [
    "UserEntity",
    "ResumeEntity",
    "InterviewSessionEntity",
    "InterviewQuestionEntity",
]
