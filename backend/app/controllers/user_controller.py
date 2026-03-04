from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
from app.database import get_db
from app.entities.schemas import User, UserUpdate
from app.services.user_service import UserService
from app.auth.dependencies import get_current_active_user

router = APIRouter()


@router.get("/", response_model=List[User])
async def get_users(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get all users (paginated)
    """
    user_service = UserService(db)
    return user_service.get_users(skip=skip, limit=limit)


@router.get("/me", response_model=User)
async def get_current_user(
    current_user: User = Depends(get_current_active_user)
):
    """
    Get current user profile
    """
    return current_user


@router.get("/{user_id}", response_model=User)
async def get_user(
    user_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get user by ID
    """
    user_service = UserService(db)
    user = user_service.get_user(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user


@router.put("/me", response_model=User)
async def update_current_user(
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Update current user profile
    """
    user_service = UserService(db)
    return user_service.update_user(current_user.id, user_update)


@router.put("/{user_id}", response_model=User)
async def update_user(
    user_id: UUID,
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Update user by ID (admin function)
    """
    user_service = UserService(db)
    return user_service.update_user(user_id, user_update)


@router.delete("/me")
async def delete_current_user(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Delete current user account
    """
    user_service = UserService(db)
    success = user_service.delete_user(current_user.id)
    if success:
        return {"message": "User account deleted successfully"}
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete user account"
        )
