"""User ORM model — infrastructure persistence layer."""

import uuid

from sqlalchemy import UUID, Boolean, Column, String
from sqlalchemy.orm import relationship

from app.domain.value_objects.enums import UserRole
from app.infrastructure.persistence.models.base import Base, TimestampMixin


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    full_name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    is_email_verified = Column(Boolean, default=False)
    role = Column(String, nullable=False, default=UserRole.USER.value)
    resumes = relationship("Resume", back_populates="user")
