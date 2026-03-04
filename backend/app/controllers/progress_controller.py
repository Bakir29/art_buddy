from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from uuid import UUID
from datetime import datetime, timedelta
from app.database import get_db
from app.entities.schemas import Progress, ProgressCreate, ProgressUpdate, User
from app.entities.models import Progress as ProgressModel, Lesson
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


@router.get("/summary")
async def get_progress_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get a summary of the current user's learning progress"""
    user_id = current_user.id

    total_lessons = db.query(Lesson).count()

    completed_lessons = db.query(ProgressModel).filter(
        ProgressModel.user_id == user_id,
        ProgressModel.completion_status == "completed"
    ).count()

    total_time = db.query(func.sum(ProgressModel.time_spent_minutes)).filter(
        ProgressModel.user_id == user_id
    ).scalar() or 0

    avg_score = db.query(func.avg(ProgressModel.score)).filter(
        ProgressModel.user_id == user_id,
        ProgressModel.completion_status == "completed",
        ProgressModel.score.isnot(None)
    ).scalar() or 0

    week_ago = datetime.utcnow() - timedelta(days=7)
    lessons_this_week = db.query(ProgressModel).filter(
        ProgressModel.user_id == user_id,
        ProgressModel.completion_status == "completed",
        ProgressModel.updated_at >= week_ago
    ).count()

    # Streak: count consecutive days (going back from today) that have a completed lesson
    streak = 0
    today = datetime.utcnow().date()
    for i in range(365):
        day = today - timedelta(days=i)
        day_start = datetime(day.year, day.month, day.day, 0, 0, 0)
        day_end = datetime(day.year, day.month, day.day, 23, 59, 59)
        count = db.query(ProgressModel).filter(
            ProgressModel.user_id == user_id,
            ProgressModel.completion_status == "completed",
            ProgressModel.updated_at >= day_start,
            ProgressModel.updated_at <= day_end
        ).count()
        if count > 0:
            streak += 1
        elif i > 0:
            break

    # Skill progress by lesson category
    categories = db.query(Lesson.category).distinct().all()
    skill_progress = {}
    for (category,) in categories:
        cat_total = db.query(Lesson).filter(Lesson.category == category).count()
        cat_completed = db.query(ProgressModel).join(
            Lesson, ProgressModel.lesson_id == Lesson.id
        ).filter(
            ProgressModel.user_id == user_id,
            ProgressModel.completion_status == "completed",
            Lesson.category == category
        ).count()
        if cat_total > 0:
            skill_progress[category.replace("_", " ").title()] = round((cat_completed / cat_total) * 100)

    # Per-day breakdown for the last 7 days (oldest first)
    day_names = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    weekly_breakdown = []
    for i in range(6, -1, -1):
        day = today - timedelta(days=i)
        day_start = datetime(day.year, day.month, day.day, 0, 0, 0)
        day_end = datetime(day.year, day.month, day.day, 23, 59, 59)
        day_count = db.query(ProgressModel).filter(
            ProgressModel.user_id == user_id,
            ProgressModel.completion_status == "completed",
            ProgressModel.updated_at >= day_start,
            ProgressModel.updated_at <= day_end
        ).count()
        weekly_breakdown.append({"day": day_names[day.weekday()], "lessons": day_count})

    return {
        "data": {
            "completed_lessons": completed_lessons,
            "total_lessons": total_lessons,
            "current_streak": streak,
            "total_time_spent": int(total_time),
            "average_score": round(float(avg_score), 1),
            "lessons_this_week": lessons_this_week,
            "skill_progress": skill_progress,
            "weekly_breakdown": weekly_breakdown
        }
    }


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
    time_spent_minutes: Optional[int] = Query(None, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Complete a lesson for current user
    """
    progress_service = ProgressService(db)
    progress = progress_service.complete_lesson(current_user.id, lesson_id, score, time_spent_minutes)
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
