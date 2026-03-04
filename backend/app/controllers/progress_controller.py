from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
from app.database import get_db
from app.entities.schemas import Progress, ProgressCreate, ProgressUpdate, User
from app.services.progress_service import ProgressService
from app.auth.dependencies import get_current_active_user

router = APIRouter()


@router.get("/user/{user_id}", response_model=List[Progress])
async def get_user_progress(
    user_id: UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get all progress records for a user
    """
    # Users can only access their own progress unless admin
    if user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    progress_service = ProgressService(db)
    return progress_service.get_user_all_progress(user_id, skip=skip, limit=limit)


@router.get("/me", response_model=List[Progress])
async def get_my_progress(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get current user's progress records
    """
    progress_service = ProgressService(db)
    return progress_service.get_user_all_progress(current_user.id, skip=skip, limit=limit)


@router.get("/user/{user_id}/lesson/{lesson_id}", response_model=Optional[Progress])
async def get_specific_progress(
    user_id: UUID,
    lesson_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get user's progress for specific lesson
    """
    # Users can only access their own progress
    if user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    progress_service = ProgressService(db)
    return progress_service.get_user_progress(user_id, lesson_id)


@router.get("/{progress_id}", response_model=Progress)
async def get_progress(
    progress_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get progress record by ID
    """
    progress_service = ProgressService(db)
    progress = progress_service.get_progress(progress_id)
    
    # Users can only access their own progress
    if progress.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    return progress


@router.post("/", response_model=Progress, status_code=status.HTTP_201_CREATED)
async def create_progress(
    progress: ProgressCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Create a new progress record
    """
    # Users can only create progress for themselves
    if progress.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    progress_service = ProgressService(db)
    return progress_service.create_progress(progress)


@router.put("/{progress_id}", response_model=Progress)
async def update_progress(
    progress_id: UUID,
    progress_update: ProgressUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Update progress record
    """
    progress_service = ProgressService(db)
    
    # Check ownership before update
    existing_progress = progress_service.get_progress(progress_id)
    if existing_progress.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    return progress_service.update_progress(progress_id, progress_update)


@router.post("/start-lesson")
async def start_lesson(
    lesson_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Start a lesson for current user
    """
    progress_service = ProgressService(db)
    progress = progress_service.start_lesson(current_user.id, lesson_id)
    return {"message": "Lesson started", "progress_id": progress.id}


@router.post("/complete-lesson")
async def complete_lesson(
    lesson_id: UUID,
    score: Optional[float] = Query(None, ge=0.0, le=100.0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Complete a lesson for current user
    """
    progress_service = ProgressService(db)
    progress = progress_service.complete_lesson(current_user.id, lesson_id, score)
    return {"message": "Lesson completed", "progress_id": progress.id, "score": score}


@router.get("/user/{user_id}/stats")
async def get_user_stats(
    user_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get user learning statistics
    """
    # Users can only access their own stats
    if user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    progress_service = ProgressService(db)
    return progress_service.get_user_stats(user_id)


@router.get("/lesson/{lesson_id}/stats")
async def get_lesson_stats(
    lesson_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get lesson statistics (admin function)
    """
    progress_service = ProgressService(db)
    return progress_service.get_lesson_stats(lesson_id)
