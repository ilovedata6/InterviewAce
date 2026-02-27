from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr

from app.domain.value_objects.enums import UserRole


class UserBase(BaseModel):
    name: str
    email: EmailStr


class UserCreate(UserBase):
    password: str


class UserUpdate(UserBase):
    password: str | None = None


class UserInDB(UserBase):
    id: UUID
    role: UserRole = UserRole.USER
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    sub: str | None = None
