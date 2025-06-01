from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.core.security import (
    create_tokens, 
    get_password_hash, 
    verify_password,
    check_login_attempts, 
    record_login_attempt, 
    create_user_session,
    get_current_user,
    revoke_tokens,
    deactivate_session,
    TokenException
)
from app.db.session import get_db
from app.models.user import User
from app.schemas.auth import Token, UserCreate, UserResponse
from app.schemas.base import Message

router = APIRouter()

@router.post("/register", response_model=UserResponse)
async def register(user: UserCreate, db: Session = Depends(get_db)):
    # Check if user already exists
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    hashed_password = get_password_hash(user.password)
    db_user = User(
        email=user.email,
        hashed_password=hashed_password,
        full_name=user.full_name
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    # Get user
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    # Check login attempts
    check_login_attempts(str(user.id), "127.0.0.1", db)  # In production, use real IP
    
    # Verify password
    if not verify_password(form_data.password, str(user.hashed_password)):
        record_login_attempt(str(user.id), "127.0.0.1", False, db)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    # Record successful login
    record_login_attempt(str(user.id), "127.0.0.1", True, db)
    
    # Create session
    session_id = create_user_session(str(user.id), "127.0.0.1", None, db)
    
    # Create tokens
    access_token, refresh_token = create_tokens({"sub": str(user.id)})
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

@router.post("/logout", response_model=Message)
async def logout(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Logout user by revoking tokens and deactivating session
    """
    try:
        # Get token from Authorization header
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authorization header"
            )
        
        token = auth_header.split(" ")[1]
        
        # Revoke the token
        try:
            revoke_tokens(token, str(current_user.id), db)
        except TokenException as e:
            # If token is already invalid, we can still proceed with logout
            print(f"Warning: Token revocation failed: {str(e)}")
        
        # Deactivate user session
        session_id = request.headers.get("X-Session-ID")
        if session_id:
            deactivate_session(session_id, db)
        
        return {"message": "Successfully logged out"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Logout failed: {str(e)}"
        ) 