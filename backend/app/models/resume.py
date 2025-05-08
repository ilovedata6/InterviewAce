from sqlalchemy import Column, String, UUID, JSON, ForeignKey
import uuid
from app.models.base import Base, TimestampMixin

class Resume(Base, TimestampMixin):
    __tablename__ = "resumes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    file_path = Column(String, nullable=False)
    extracted_data = Column(JSON, nullable=True)
    inferred_role = Column(String, nullable=True)
    experience_level = Column(String, nullable=True) 