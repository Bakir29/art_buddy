from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.auth.security import decode_access_token
from app.database import get_db
from app.entities.models import User
from app.entities.schemas import TokenData

security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """Get current authenticated user"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        email = decode_access_token(credentials.credentials)
        token_data = TokenData(email=email)
    except Exception:
        raise credentials_exception
    
    user = db.query(User).filter(User.email == token_data.email).first()
    if user is None:
        raise credentials_exception
    
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Get current active user"""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


async def get_current_user_websocket(token: str, db: Session) -> dict:
    """Get current user for WebSocket authentication"""
    try:
        email = decode_access_token(token)
        user = db.query(User).filter(User.email == email).first()
        
        if user is None or not user.is_active:
            raise Exception("Invalid user")
        
        return {
            "user_id": str(user.id),
            "email": user.email,
            "name": user.name
        }
    except Exception as e:
        raise Exception(f"WebSocket authentication failed: {str(e)}")
