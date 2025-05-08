from datetime import datetime, timedelta
from typing import Optional, Tuple, Dict
from jose import JWTError, jwt
from passlib.context import CryptContext
import re
import uuid
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.core.config import settings
from app.db.session import get_db
from app.models.security import LoginAttempt, TokenBlacklist, UserSession, PasswordHistory
from app.models.user import User
import os
from dotenv import load_dotenv
from datetime import timezone

load_dotenv()

# Security Constants
PASSWORD_HISTORY_LIMIT = 5
MIN_PASSWORD_AGE_DAYS = 1
SESSION_TIMEOUT_MINUTES = 30

# Password complexity requirements
PASSWORD_PATTERN = re.compile(r'^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]{8,}$')

# Configure password hashing
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=12,
    bcrypt__ident="2b",
    bcrypt__min_rounds=10,
    bcrypt__max_rounds=15
)

# OAuth2 scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")

class SecurityException(HTTPException):
    """Custom security exception with proper HTTP status codes"""
    def __init__(self, detail: str, status_code: int = status.HTTP_401_UNAUTHORIZED):
        super().__init__(status_code=status_code, detail=detail)

class TokenException(SecurityException):
    """Exception for token-related errors"""
    def __init__(self, detail: str):
        super().__init__(detail=detail, status_code=status.HTTP_401_UNAUTHORIZED)

class AuthenticationException(SecurityException):
    """Exception for authentication-related errors"""
    def __init__(self, detail: str):
        super().__init__(detail=detail, status_code=status.HTTP_401_UNAUTHORIZED)

class AuthorizationException(SecurityException):
    """Exception for authorization-related errors"""
    def __init__(self, detail: str):
        super().__init__(detail=detail, status_code=status.HTTP_403_FORBIDDEN)

class SessionException(SecurityException):
    """Exception for session-related errors"""
    def __init__(self, detail: str):
        super().__init__(detail=detail, status_code=status.HTTP_401_UNAUTHORIZED)

def validate_password_complexity(password: str) -> bool:
    """Check if password meets complexity requirements"""
    return bool(PASSWORD_PATTERN.match(password))

def check_password_history(user_id: str, new_password: str, db: Session) -> bool:
    """Check if password has been used before"""
    try:
        # Get recent password history
        recent_passwords = db.query(PasswordHistory).filter(
            PasswordHistory.user_id == user_id,
            PasswordHistory.is_active == True
        ).order_by(PasswordHistory.created_at.desc()).limit(PASSWORD_HISTORY_LIMIT).all()
        
        # Check against all recent passwords
        for old_password in recent_passwords:
            if verify_password(new_password, old_password.password_hash):
                return False
        
        return True
    except Exception as e:
        raise AuthenticationException(f"Failed to check password history: {str(e)}")

def record_password_history(user_id: str, password_hash: str, db: Session) -> None:
    """Record password in history"""
    try:
        history = PasswordHistory(
            user_id=user_id,
            password_hash=password_hash
        )
        db.add(history)
        db.commit()
    except Exception as e:
        raise AuthenticationException(f"Failed to record password history: {str(e)}")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password with bcrypt"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hash password with bcrypt"""
    if not validate_password_complexity(password):
        raise AuthenticationException("Password does not meet complexity requirements")
    return pwd_context.hash(password)

def create_tokens(data: dict) -> Tuple[str, str]:
    """Create both access and refresh tokens"""
    access_token_expires = timedelta(minutes=int(os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES', 15)))
    refresh_token_expires = timedelta(days=int(os.getenv('REFRESH_TOKEN_EXPIRE_DAYS', 7)))
    
    access_token = create_token(data, access_token_expires)
    refresh_token = create_token(data, refresh_token_expires)
    
    return access_token, refresh_token

def create_token(data: dict, expires_delta: timedelta) -> str:
    """Create a JWT token"""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + expires_delta
    token_id = str(uuid.uuid4())
    
    to_encode.update({
        "exp": expire,
        "iat": datetime.now(timezone.utc),
        "jti": token_id,
        "iss": settings.PROJECT_NAME,
        "aud": "interview_ace_api",
        "sub": data.get("sub"),
        "type": "access" if expires_delta == timedelta(minutes=int(os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES', 15))) else "refresh"
    })
    
    try:
        encoded_jwt = jwt.encode(
            to_encode,
            os.getenv('SECRET_KEY'),
            algorithm=settings.ALGORITHM
        )
        return encoded_jwt
    except Exception as e:
        raise TokenException(f"Failed to create token: {str(e)}")

def verify_token(token: str, db: Session) -> Optional[dict]:
    """Verify JWT token"""
    try:
        payload = jwt.decode(
            token,
            os.getenv('SECRET_KEY'),
            algorithms=[settings.ALGORITHM],
            audience="interview_ace_api",
            options={
                "verify_iat": True,
                "verify_exp": True,
                "require_iat": True,
                "require_exp": True,
                "verify_iss": True,
                "verify_aud": True,
                "require_iss": True,
                "require_aud": True
            }
        )
        
        # Additional security checks
        if payload.get("iss") != settings.PROJECT_NAME:
            raise TokenException("Invalid token issuer")
            
        if payload.get("type") not in ["access", "refresh"]:
            raise TokenException("Invalid token type")
            
        # Check if token is blacklisted
        token_id = payload.get("jti")
        if check_token_revocation(token_id, db):
            raise TokenException("Token has been revoked")
            
        return payload
    except JWTError as e:
        raise TokenException(f"Token verification failed: {str(e)}")

def check_token_revocation(token_id: str, db: Session) -> bool:
    """Check if token has been revoked"""
    try:
        blacklisted_token = db.query(TokenBlacklist).filter(
            TokenBlacklist.token_id == token_id,
            TokenBlacklist.expires_at > datetime.now(timezone.utc)
        ).first()
        return blacklisted_token is not None
    except Exception as e:
        raise TokenException(f"Failed to check token revocation: {str(e)}")

def revoke_tokens(token: str, user_id: str, db: Session) -> None:
    """Revoke access and refresh tokens"""
    try:
        # Get token payload
        payload = verify_token(token, db)
        token_id = payload.get("jti")
        
        if not token_id:
            raise TokenException("Invalid token: missing token ID")
        
        # Check if token is already blacklisted
        if check_token_revocation(token_id, db):
            return  # Token already revoked
        
        # Add token to blacklist
        blacklisted_token = TokenBlacklist(
            token_id=token_id,
            user_id=user_id,
            expires_at=datetime.fromtimestamp(payload["exp"], timezone.utc),
            reason="logout"
        )
        db.add(blacklisted_token)
        db.commit()
    except JWTError as e:
        raise TokenException(f"Invalid token: {str(e)}")
    except Exception as e:
        raise TokenException(f"Failed to revoke token: {str(e)}")

def check_login_attempts(user_id: str, ip_address: str, db: Session) -> bool:
    """Check if user has exceeded login attempts"""
    try:
        # Get recent failed attempts
        recent_attempts = db.query(LoginAttempt).filter(
            LoginAttempt.user_id == user_id,
            LoginAttempt.ip_address == ip_address,
            LoginAttempt.created_at > datetime.now(timezone.utc) - timedelta(minutes=5),
            LoginAttempt.success == False
        ).count()
        
        max_attempts = int(os.getenv('MAX_LOGIN_ATTEMPTS', 5))
        if recent_attempts >= max_attempts:
            # Lock the account
            lock_until = datetime.now(timezone.utc) + timedelta(minutes=5)
            db.query(LoginAttempt).filter(
                LoginAttempt.user_id == user_id,
                LoginAttempt.ip_address == ip_address
            ).update({"locked_until": lock_until})
            db.commit()
            raise AuthenticationException("Account locked due to too many failed attempts")
        
        return True
    except Exception as e:
        raise AuthenticationException(f"Failed to check login attempts: {str(e)}")

def record_login_attempt(user_id: str, ip_address: str, success: bool, db: Session) -> None:
    """Record login attempt"""
    try:
        attempt = LoginAttempt(
            user_id=user_id,
            ip_address=ip_address,
            success=success
        )
        db.add(attempt)
        db.commit()
    except Exception as e:
        raise AuthenticationException(f"Failed to record login attempt: {str(e)}")

def create_user_session(user_id: str, ip_address: str, user_agent: Optional[str], db: Session) -> str:
    """Create a new user session"""
    try:
        # Check if user has too many active sessions
        max_sessions = int(os.getenv('MAX_SESSIONS_PER_USER', 5))
        active_sessions = db.query(UserSession).filter(
            UserSession.user_id == user_id,
            UserSession.is_active == True
        ).count()
        
        if active_sessions >= max_sessions:
            # Deactivate oldest session
            oldest_session = db.query(UserSession).filter(
                UserSession.user_id == user_id,
                UserSession.is_active == True
            ).order_by(UserSession.last_activity).first()
            
            if oldest_session:
                oldest_session.is_active = False
                db.commit()
        
        # Create new session
        session_id = str(uuid.uuid4())
        session = UserSession(
            user_id=user_id,
            session_id=session_id,
            ip_address=ip_address,
            user_agent=user_agent
        )
        db.add(session)
        db.commit()
        
        return session_id
    except Exception as e:
        raise SessionException(f"Failed to create user session: {str(e)}")

def update_session_activity(session_id: str, db: Session) -> None:
    """Update session last activity time"""
    try:
        session = db.query(UserSession).filter(
            UserSession.session_id == session_id,
            UserSession.is_active == True
        ).first()
        
        if not session:
            raise SessionException("Session not found or inactive")
            
        session.last_activity = datetime.now(timezone.utc)
        db.commit()
    except Exception as e:
        raise SessionException(f"Failed to update session activity: {str(e)}")

def deactivate_session(session_id: str, db: Session) -> None:
    """Deactivate a user session"""
    try:
        if not session_id:
            return  # No session ID provided, skip deactivation
            
        session = db.query(UserSession).filter(
            UserSession.session_id == session_id,
            UserSession.is_active == True
        ).first()
        
        if session:
            session.is_active = False
            session.deactivated_at = datetime.now(timezone.utc)
            db.commit()
    except Exception as e:
        # Log the error but don't raise it to prevent logout failure
        print(f"Warning: Failed to deactivate session: {str(e)}")

def generate_csrf_token() -> str:
    """Generate CSRF token"""
    return str(uuid.uuid4())

def verify_csrf_token(token: str, csrf_token: str) -> bool:
    """Verify CSRF token"""
    if not token or not csrf_token:
        raise SecurityException("Missing CSRF token")
    return token == csrf_token

def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """Get current user from token"""
    try:
        payload = verify_token(token, db)
        user_id = payload.get("sub")
        if not user_id:
            raise AuthenticationException("Invalid token payload")
        
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise AuthenticationException("User not found")
        
        if not user.is_active:
            raise AuthenticationException("User is inactive")
        
        return user
    except Exception as e:
        raise AuthenticationException(str(e)) 