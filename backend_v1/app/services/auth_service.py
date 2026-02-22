import uuid
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from app.models.user import User
from app.models.security import PasswordResetToken
from app.core.security import get_password_hash

def create_password_reset_token(db: Session, user_id: uuid.UUID) -> str:
    reset_token = str(uuid.uuid4())
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=15)
    db_token = PasswordResetToken(
        token=reset_token,
        user_id=user_id,
        expires_at=expires_at
    )
    db.add(db_token)
    db.commit()
    return reset_token

def verify_and_reset_password(db: Session, token: str, new_password: str) -> bool:
    record = (
        db.query(PasswordResetToken)
          .filter(
              PasswordResetToken.token == token,
              PasswordResetToken.expires_at >= datetime.now(timezone.utc),
              PasswordResetToken.used == False
          )
          .first()
    )
    if not record:
        return False
    user = db.query(User).filter(User.id == record.user_id).first()
    if not user:
        return False
    user.hashed_password = get_password_hash(new_password)  # type: ignore
    record.used = True  # type: ignore
    db.add(user)
    db.add(record)
    db.commit()
    return True
