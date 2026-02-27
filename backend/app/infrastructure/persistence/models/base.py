"""SQLAlchemy declarative base and timestamp mixin."""

from sqlalchemy import Column, DateTime, func
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class TimestampMixin:
    created_at = Column(DateTime(timezone=True), default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True), default=func.now(), onupdate=func.now(), nullable=False
    )
