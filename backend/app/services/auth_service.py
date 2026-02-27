import uuid
from datetime import UTC, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_password_hash
from app.models.security import PasswordResetToken
from app.models.user import User


async def create_password_reset_token(db: AsyncSession, user_id: uuid.UUID) -> str:
    reset_token = str(uuid.uuid4())
    expires_at = datetime.now(UTC) + timedelta(minutes=15)
    db_token = PasswordResetToken(token=reset_token, user_id=user_id, expires_at=expires_at)
    db.add(db_token)
    await db.commit()
    return reset_token


async def verify_and_reset_password(db: AsyncSession, token: str, new_password: str) -> bool:
    result = await db.execute(
        select(PasswordResetToken).where(
            PasswordResetToken.token == token,
            PasswordResetToken.expires_at >= datetime.now(UTC),
            PasswordResetToken.used.is_(False),
        )
    )
    record = result.scalars().first()
    if not record:
        return False
    result2 = await db.execute(select(User).where(User.id == record.user_id))
    user = result2.scalars().first()
    if not user:
        return False
    user.hashed_password = get_password_hash(new_password)  # type: ignore
    record.used = True  # type: ignore
    db.add(user)
    db.add(record)
    await db.commit()
    return True
