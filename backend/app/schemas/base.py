from pydantic import BaseModel, Field
from typing import Generic, List, Optional, TypeVar

T = TypeVar("T")


class Message(BaseModel):
    message: str


class PaginatedResponse(BaseModel, Generic[T]):
    """Generic paginated response wrapper used by all list endpoints."""

    items: List[T]
    total: int = Field(..., description="Total number of records matching the query")
    skip: int = Field(..., ge=0, description="Number of records skipped")
    limit: int = Field(..., ge=1, description="Page size")
    has_more: bool = Field(..., description="Whether more records exist beyond this page")