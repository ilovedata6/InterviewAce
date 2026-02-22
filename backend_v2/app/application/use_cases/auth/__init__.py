"""
Auth use cases — application-specific business rules for authentication.

Each use case orchestrates domain logic through repository interfaces
and security utilities.  Endpoints become thin wrappers that call these.
"""

from __future__ import annotations

import os
import uuid
from typing import Optional

from app.application.dto.auth import (
    ChangePasswordInput,
    LoginInput,
    RegisterInput,
    ResetPasswordInput,
    TokenPair,
)
from app.core.security import (
    create_tokens,
    generate_email_verification_token,
    get_password_hash,
    verify_email_verification_token,
    verify_password,
    verify_token,
)
from app.domain.entities.user import UserEntity
from app.domain.exceptions import (
    AuthenticationError,
    DuplicateEntityError,
    EntityNotFoundError,
    AccountLockedError,
    ValidationError,
)
from app.domain.interfaces.repositories import IAuthRepository, IUserRepository
from app.utils.email_utils import send_verification_email
from app.utils.email_service import send_email


# ── Register ────────────────────────────────────────────────────────────────

class RegisterUseCase:
    """Create a new user account and send a verification email."""

    def __init__(self, user_repo: IUserRepository) -> None:
        self._user_repo = user_repo

    async def execute(self, dto: RegisterInput) -> str:
        # Check duplicate email
        existing = await self._user_repo.get_by_email(dto.email)
        if existing:
            raise DuplicateEntityError("Email already registered")

        # Hash password & persist
        hashed = get_password_hash(dto.password)
        entity = UserEntity(
            email=dto.email,
            hashed_password=hashed,
            full_name=dto.full_name,
        )
        saved = await self._user_repo.create(entity)

        # Email verification
        token = generate_email_verification_token(str(saved.id))
        send_verification_email(dto.email, token)

        return "Registration successful. Please check your email to verify your account."


# ── Login ───────────────────────────────────────────────────────────────────

class LoginUseCase:
    """Authenticate user credentials and return a JWT token pair."""

    def __init__(
        self,
        user_repo: IUserRepository,
        auth_repo: IAuthRepository,
    ) -> None:
        self._user_repo = user_repo
        self._auth_repo = auth_repo

    async def execute(self, dto: LoginInput) -> TokenPair:
        # Find user
        user = await self._user_repo.get_by_email(dto.email)
        if not user:
            raise AuthenticationError("Incorrect email or password")

        # Must be verified
        if not user.is_email_verified:
            raise AuthenticationError("Please verify your email before logging in")

        # Check lockout
        max_attempts = int(os.getenv("MAX_LOGIN_ATTEMPTS", 5))
        recent_failures = await self._auth_repo.count_recent_failed_attempts(
            user.id, dto.ip_address
        )
        if recent_failures >= max_attempts:
            await self._auth_repo.lock_login_attempts(user.id, dto.ip_address)
            raise AccountLockedError("Account locked due to too many failed attempts")

        # Verify password
        if not verify_password(dto.password, user.hashed_password):
            await self._auth_repo.record_login_attempt(user.id, dto.ip_address, False)
            raise AuthenticationError("Incorrect email or password")

        # Success
        await self._auth_repo.record_login_attempt(user.id, dto.ip_address, True)

        # Session management
        max_sessions = int(os.getenv("MAX_SESSIONS_PER_USER", 5))
        active = await self._auth_repo.get_active_session_count(user.id)
        if active >= max_sessions:
            await self._auth_repo.deactivate_oldest_session(user.id)
        await self._auth_repo.create_session(user.id, dto.ip_address, None)

        # Issue tokens
        access, refresh = create_tokens({"sub": str(user.id)})
        return TokenPair(access_token=access, refresh_token=refresh)


# ── Logout ──────────────────────────────────────────────────────────────────

class LogoutUseCase:
    """Revoke tokens and deactivate the user session."""

    def __init__(self, auth_repo: IAuthRepository) -> None:
        self._auth_repo = auth_repo

    async def execute(
        self,
        token: str,
        user_id: uuid.UUID,
        session_id: Optional[str],
        db,  # AsyncSession — needed by verify_token
    ) -> str:
        from datetime import datetime, timezone

        try:
            payload = await verify_token(token, db)
            if payload and isinstance(payload, dict):
                token_id = payload.get("jti")
                if token_id and not await self._auth_repo.is_token_blacklisted(token_id):
                    exp_ts = payload.get("exp", 0)
                    ttl = max(int(exp_ts - datetime.now(timezone.utc).timestamp()), 1)

                    # Redis blacklist (best-effort)
                    try:
                        from app.infrastructure.cache.redis_client import RedisTokenBlacklist
                        await RedisTokenBlacklist.revoke(token_id, ttl_seconds=ttl, reason="logout")
                    except Exception:
                        pass

                    # DB blacklist (durable)
                    await self._auth_repo.blacklist_token(
                        token_id=token_id,
                        user_id=user_id,
                        expires_at=datetime.fromtimestamp(payload["exp"], timezone.utc),
                        reason="logout",
                    )
        except Exception:
            pass  # Token revocation failure should not block logout

        if session_id:
            await self._auth_repo.deactivate_session(session_id)

        return "Successfully logged out"


# ── Refresh Token ───────────────────────────────────────────────────────────

class RefreshTokenUseCase:
    """Exchange a valid refresh token for a new token pair."""

    def __init__(self, user_repo: IUserRepository) -> None:
        self._user_repo = user_repo

    async def execute(self, refresh_token: str, db) -> TokenPair:
        from app.core.security import get_current_user_from_refresh_token

        user = await get_current_user_from_refresh_token(refresh_token, db)
        access, new_refresh = create_tokens({"sub": str(user.id)})
        return TokenPair(access_token=access, refresh_token=new_refresh)


# ── Change Password ─────────────────────────────────────────────────────────

class ChangePasswordUseCase:
    """Change the password of an authenticated user."""

    def __init__(self, user_repo: IUserRepository) -> None:
        self._user_repo = user_repo

    async def execute(self, user_id: uuid.UUID, dto: ChangePasswordInput) -> str:
        user = await self._user_repo.get_by_id(user_id)
        if not user:
            raise EntityNotFoundError("User", str(user_id))

        if not verify_password(dto.old_password, user.hashed_password):
            raise ValidationError("Old password is incorrect")

        if dto.old_password == dto.new_password:
            raise ValidationError("New password must be different from old password")

        user.hashed_password = get_password_hash(dto.new_password)
        await self._user_repo.update(user)
        return "Password changed successfully"


# ── Verify Email ────────────────────────────────────────────────────────────

class VerifyEmailUseCase:
    """Confirm a user's email address via a one-time token."""

    def __init__(self, user_repo: IUserRepository) -> None:
        self._user_repo = user_repo

    async def execute(self, token: str) -> str:
        try:
            user_id_str = verify_email_verification_token(token)
        except Exception:
            raise ValidationError("Invalid or expired verification token.")

        user = await self._user_repo.get_by_id(uuid.UUID(user_id_str))
        if not user:
            raise ValidationError("Invalid or expired verification token.")

        if user.is_email_verified:
            return "Email already verified."

        user.verify_email()
        await self._user_repo.update(user)
        return "Email verified successfully. You can now log in."


# ── Resend Verification ────────────────────────────────────────────────────

class ResendVerificationUseCase:
    """Resend the verification email to a registered user."""

    def __init__(self, user_repo: IUserRepository) -> None:
        self._user_repo = user_repo

    async def execute(self, email: str) -> str:
        user = await self._user_repo.get_by_email(email)
        if user and not user.is_email_verified:
            token = generate_email_verification_token(str(user.id))
            send_verification_email(user.email, token)
        # Always return success to prevent user enumeration
        return "Verification email sent again."


# ── Reset Password Request ─────────────────────────────────────────────────

class ResetPasswordRequestUseCase:
    """Initiate the forgot-password flow."""

    def __init__(
        self,
        user_repo: IUserRepository,
        auth_repo: IAuthRepository,
    ) -> None:
        self._user_repo = user_repo
        self._auth_repo = auth_repo

    async def execute(self, email: str) -> str:
        user = await self._user_repo.get_by_email(email)
        if user:
            token = await self._auth_repo.create_password_reset_token(user.id)
            reset_link = f"https://your-frontend-domain.com/reset-password?token={token}"
            body = (
                f"Hi {user.email},\n\n"
                "You requested a password reset. Click the link below (valid for 15 minutes):\n"
                f"{reset_link}\n\n"
                "If you did not request this, ignore this email.\n"
            )
            send_email(
                to_email=user.email,
                subject="Reset Your Interview Ace Password",
                body=body,
            )
        return "If an account with that email exists, you will receive a reset link shortly."


# ── Reset Password Confirm ─────────────────────────────────────────────────

class ResetPasswordConfirmUseCase:
    """Complete the password-reset flow using a token."""

    def __init__(
        self,
        user_repo: IUserRepository,
        auth_repo: IAuthRepository,
    ) -> None:
        self._user_repo = user_repo
        self._auth_repo = auth_repo

    async def execute(self, dto: ResetPasswordInput) -> str:
        user_id = await self._auth_repo.verify_and_consume_reset_token(dto.token)
        if not user_id:
            raise ValidationError("Invalid or expired reset token.")

        user = await self._user_repo.get_by_id(user_id)
        if not user:
            raise ValidationError("Invalid or expired reset token.")

        user.hashed_password = get_password_hash(dto.new_password)
        await self._user_repo.update(user)
        return "Password has been reset successfully."
