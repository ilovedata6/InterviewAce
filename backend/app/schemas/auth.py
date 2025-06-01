from pydantic import BaseModel, EmailStr, UUID4
from typing import Optional
from datetime import datetime

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

class UserBase(BaseModel):
    email: EmailStr
    full_name: str

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: UUID4
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str

class ResetPasswordRequestIn(BaseModel):
    email: EmailStr

class ResetPasswordConfirmIn(BaseModel):
    token: str
    new_password: str  # min_length=8 will be enforced in endpoint or service

class MessageOut(BaseModel):
    message: str