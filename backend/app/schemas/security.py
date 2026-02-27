from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class LoginAttemptBase(BaseModel):
    user_id: UUID
    ip_address: str
    success: bool = False


class LoginAttemptCreate(LoginAttemptBase):
    pass


class LoginAttemptInDB(LoginAttemptBase):
    id: UUID
    created_at: datetime
    locked_until: datetime | None = None

    class Config:
        from_attributes = True


class TokenBlacklistBase(BaseModel):
    token_id: str
    user_id: UUID
    expires_at: datetime
    reason: str | None = None


class TokenBlacklistCreate(TokenBlacklistBase):
    pass


class TokenBlacklistInDB(TokenBlacklistBase):
    id: UUID
    created_at: datetime

    class Config:
        from_attributes = True


class UserSessionBase(BaseModel):
    user_id: UUID
    session_id: str
    ip_address: str
    user_agent: str | None = None
    session_data: dict | None = None


class UserSessionCreate(UserSessionBase):
    pass


class UserSessionInDB(UserSessionBase):
    id: UUID
    created_at: datetime
    last_activity: datetime
    is_active: bool = True

    class Config:
        from_attributes = True


class PasswordHistoryBase(BaseModel):
    user_id: UUID
    password_hash: str


class PasswordHistoryCreate(PasswordHistoryBase):
    pass


class PasswordHistoryInDB(PasswordHistoryBase):
    id: UUID
    created_at: datetime
    is_active: bool = True

    class Config:
        from_attributes = True
