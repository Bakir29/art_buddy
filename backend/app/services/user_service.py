from sqlalchemy.orm import Session
from typing import Optional, List
from uuid import UUID
from app.entities.models import User
from app.entities.schemas import UserCreate, UserUpdate
from app.repositories.user_repository import UserRepository
from app.auth.security import get_password_hash, verify_password
from fastapi import HTTPException, status


class UserService:
    
    def __init__(self, db: Session):
        self.db = db
        self.repository = UserRepository(db)
    
    def create_user(self, user: UserCreate) -> User:
        """Create a new user with hashed password"""
        # Check if user already exists
        existing_user = self.repository.get_by_email(user.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Hash password and create user
        hashed_password = get_password_hash(user.password)
        return self.repository.create(user, hashed_password)
    
    def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """Authenticate user with email and password"""
        user = self.repository.get_by_email(email)
        if not user or not user.is_active:
            return None
        
        if not verify_password(password, user.hashed_password):
            return None
        
        return user
    
    def get_user(self, user_id: UUID) -> Optional[User]:
        """Get user by ID"""
        user = self.repository.get_by_id(user_id)
        if not user or not user.is_active:
            return None
        return user
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        user = self.repository.get_by_email(email)
        if not user or not user.is_active:
            return None
        return user
    
    def get_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        """Get all active users with pagination"""
        users = self.repository.get_all(skip=skip, limit=limit)
        return [user for user in users if user.is_active]
    
    def update_user(self, user_id: UUID, user_update: UserUpdate) -> Optional[User]:
        """Update user information"""
        existing_user = self.get_user(user_id)
        if not existing_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return self.repository.update(user_id, user_update)
    
    def delete_user(self, user_id: UUID) -> bool:
        """Soft delete user"""
        existing_user = self.get_user(user_id)
        if not existing_user:
            return False
        
        return self.repository.delete(user_id)
