"""Resume ORM model — infrastructure persistence layer.

Note: Enums are imported from ``app.domain.value_objects.enums`` — the single
source of truth — fixing the previous model→schema layer violation.
"""

import uuid

from sqlalchemy import JSON, UUID, Boolean, Column, Float, ForeignKey, Integer, String, Text
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import relationship

from app.domain.value_objects.enums import FileType, ResumeStatus
from app.infrastructure.persistence.models.base import Base, TimestampMixin


class Resume(Base, TimestampMixin):
    __tablename__ = "resumes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)  # noqa: A003
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    title = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    file_path = Column(String, nullable=False)
    file_name = Column(String(255), nullable=False)
    file_size = Column(Integer, nullable=False)
    file_type = Column(SQLEnum(FileType), nullable=False)
    inferred_role = Column(String(100), nullable=True)
    status = Column(SQLEnum(ResumeStatus), nullable=False, default=ResumeStatus.PENDING, index=True)
    analysis = Column(JSON, nullable=True)
    version = Column(Integer, nullable=False, default=1)
    years_of_experience = Column(Integer, nullable=True)
    skills = Column(JSON, nullable=True)
    parent_version_id = Column(UUID(as_uuid=True), ForeignKey("resumes.id"), nullable=True)
    is_public = Column(Boolean, nullable=False, default=False)
    share_token = Column(String(64), nullable=True, unique=True)
    confidence_score = Column(Float, nullable=True)
    processing_time = Column(Float, nullable=True)

    # Relationships
    user = relationship("User", back_populates="resumes")
    parent_version = relationship("Resume", remote_side=[id], backref="child_versions")  # noqa: A003
    interview_sessions = relationship("InterviewSession", back_populates="resume")

    def __repr__(self):
        return f"<Resume {self.id}: {self.title}>"
