"""Auth DTOs — data transfer objects for auth use case boundaries."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class RegisterInput:
    email: str
    password: str
    full_name: str


@dataclass(frozen=True)
class LoginInput:
    email: str
    password: str
    ip_address: str = "127.0.0.1"


@dataclass(frozen=True)
class TokenPair:
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


@dataclass(frozen=True)
class ChangePasswordInput:
    old_password: str
    new_password: str


@dataclass(frozen=True)
class ResetPasswordInput:
    token: str
    new_password: str
