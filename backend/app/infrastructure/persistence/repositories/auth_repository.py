"""
AuthRepository — SQLAlchemy implementation of IAuthRepository.

Handles persistence for login attempts, user sessions, token blacklist,
password reset tokens, and password history.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta

from sqlalchemy import func, select
from sqlalchemy import update as sa_update
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.interfaces.repositories import IAuthRepository
from app.infrastructure.persistence.models.security import (
    LoginAttempt,
    PasswordResetToken,
    TokenBlacklist,
    UserSession,
)


class AuthRepository(IAuthRepository):
    """Concrete auth persistence backed by SQLAlchemy."""

    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    # ------------------------------------------------------------------
    # Login attempts
    # ------------------------------------------------------------------

    async def count_recent_failed_attempts(
        self, user_id: uuid.UUID, ip_address: str, window_minutes: int = 5
    ) -> int:
        result = await self._db.execute(
            select(func.count())
            .select_from(LoginAttempt)
            .where(
                LoginAttempt.user_id == user_id,
                LoginAttempt.ip_address == ip_address,
                LoginAttempt.created_at > datetime.now(UTC) - timedelta(minutes=window_minutes),
                LoginAttempt.success.is_(False),
            )
        )
        return result.scalar_one()

    async def lock_login_attempts(
        self, user_id: uuid.UUID, ip_address: str, lock_duration_minutes: int = 5
    ) -> None:
        lock_until = datetime.now(UTC) + timedelta(minutes=lock_duration_minutes)
        await self._db.execute(
            sa_update(LoginAttempt)
            .where(
                LoginAttempt.user_id == user_id,
                LoginAttempt.ip_address == ip_address,
            )
            .values(locked_until=lock_until)
        )
        await self._db.commit()

    async def record_login_attempt(
        self, user_id: uuid.UUID, ip_address: str, success: bool
    ) -> None:
        attempt = LoginAttempt(
            user_id=user_id,
            ip_address=ip_address,
            success=success,
        )
        self._db.add(attempt)
        await self._db.commit()

    # ------------------------------------------------------------------
    # User sessions
    # ------------------------------------------------------------------

    async def get_active_session_count(self, user_id: uuid.UUID) -> int:
        result = await self._db.execute(
            select(func.count())
            .select_from(UserSession)
            .where(
                UserSession.user_id == user_id,
                UserSession.is_active.is_(True),
            )
        )
        return result.scalar_one()

    async def deactivate_oldest_session(self, user_id: uuid.UUID) -> None:
        result = await self._db.execute(
            select(UserSession)
            .where(
                UserSession.user_id == user_id,
                UserSession.is_active.is_(True),
            )
            .order_by(UserSession.last_activity)
            .limit(1)
        )
        oldest = result.scalars().first()
        if oldest:
            oldest.is_active = False
            await self._db.commit()

    async def create_session(
        self, user_id: uuid.UUID, ip_address: str, user_agent: str | None
    ) -> str:
        session_id = str(uuid.uuid4())
        session = UserSession(
            user_id=user_id,
            session_id=session_id,
            ip_address=ip_address,
            user_agent=user_agent,
        )
        self._db.add(session)
        await self._db.commit()
        return session_id

    async def deactivate_session(self, session_id: str) -> None:
        if not session_id:
            return
        result = await self._db.execute(
            select(UserSession).where(
                UserSession.session_id == session_id,
                UserSession.is_active.is_(True),
            )
        )
        session = result.scalars().first()
        if session:
            session.is_active = False
            session.deactivated_at = datetime.now(UTC)
            await self._db.commit()

    # ------------------------------------------------------------------
    # Password reset tokens
    # ------------------------------------------------------------------

    async def create_password_reset_token(self, user_id: uuid.UUID) -> str:
        reset_token = str(uuid.uuid4())
        expires_at = datetime.utcnow() + timedelta(minutes=15)  # naive UTC — matches TIMESTAMP WITHOUT TIME ZONE column
        db_token = PasswordResetToken(
            token=reset_token,
            user_id=user_id,
            expires_at=expires_at,
        )
        self._db.add(db_token)
        await self._db.commit()
        return reset_token

    async def verify_and_consume_reset_token(self, token: str) -> uuid.UUID | None:
        result = await self._db.execute(
            select(PasswordResetToken).where(
                PasswordResetToken.token == token,
                PasswordResetToken.expires_at >= datetime.utcnow(),  # naive UTC — matches column
                PasswordResetToken.used.is_(False),
            )
        )
        record = result.scalars().first()
        if not record:
            return None
        record.used = True  # type: ignore
        self._db.add(record)
        await self._db.commit()
        return record.user_id  # type: ignore

    # ------------------------------------------------------------------
    # Token blacklist
    # ------------------------------------------------------------------

    async def blacklist_token(
        self, token_id: str, user_id: uuid.UUID, expires_at: datetime, reason: str
    ) -> None:
        entry = TokenBlacklist(
            token_id=token_id,
            user_id=user_id,
            expires_at=expires_at,
            reason=reason,
        )
        self._db.add(entry)
        await self._db.commit()

    async def is_token_blacklisted(self, token_id: str) -> bool:
        result = await self._db.execute(
            select(TokenBlacklist).where(
                TokenBlacklist.token_id == token_id,
                TokenBlacklist.expires_at > datetime.now(UTC),
            )
        )
        return result.scalars().first() is not None
