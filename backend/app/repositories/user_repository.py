from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import List, Optional, Dict, Any
from uuid import UUID
from app.entities.models import User
from app.entities.schemas import UserCreate, UserUpdate


class UserRepository:
    
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, user: UserCreate, hashed_password: str) -> User:
        """Create a new user"""
        db_user = User(
            name=user.name,
            email=user.email,
            hashed_password=hashed_password,
            skill_level=user.skill_level
        )
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        return db_user
    
    def get_by_id(self, user_id: UUID) -> Optional[User]:
        """Get user by ID"""
        return self.db.query(User).filter(User.id == user_id).first()
    
    def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        return self.db.query(User).filter(User.email == email).first()
    
    def get_all(self, skip: int = 0, limit: int = 100) -> List[User]:
        """Get all users with pagination"""
        return self.db.query(User).offset(skip).limit(limit).all()
    
    def update(self, user_id: UUID, user_update: UserUpdate) -> Optional[User]:
        """Update user"""
        db_user = self.get_by_id(user_id)
        if not db_user:
            return None
        
        update_data = user_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_user, field, value)
        
        self.db.commit()
        self.db.refresh(db_user)
        return db_user
    
    def delete(self, user_id: UUID) -> bool:
        """Delete user (soft delete by setting is_active=False)"""
        db_user = self.get_by_id(user_id)
        if not db_user:
            return False
        
        db_user.is_active = False
        self.db.commit()
        return True
    
    def authenticate(self, email: str, password: str) -> Optional[User]:
        """Authenticate user - note: password verification should be done in service layer"""
        return self.get_by_email(email)
