from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
from app.entities.models import Progress
from app.entities.schemas import ProgressCreate, ProgressUpdate
from app.repositories.progress_repository import ProgressRepository
from app.services.user_service import UserService
from app.services.lesson_service import LessonService
from fastapi import HTTPException, status


class ProgressService:
    
    def __init__(self, db: Session):
        self.db = db
        self.repository = ProgressRepository(db)
        self.user_service = UserService(db)
        self.lesson_service = LessonService(db)
    
    def create_progress(self, progress: ProgressCreate) -> Progress:
        """Create a new progress record"""
        # Validate user and lesson exist
        user = self.user_service.get_user(progress.user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        lesson = self.lesson_service.get_lesson(progress.lesson_id)
        if not lesson:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Lesson not found"
            )
        
        # Check if progress already exists
        existing = self.repository.get_user_progress(progress.user_id, progress.lesson_id)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Progress record already exists for this user and lesson"
            )
        
        return self.repository.create(progress)
    
    def get_progress(self, progress_id: UUID) -> Optional[Progress]:
        """Get progress record by ID"""
        progress = self.repository.get_by_id(progress_id)
        if not progress:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Progress record not found"
            )
        return progress
    
    def get_user_progress(self, user_id: UUID, lesson_id: UUID) -> Optional[Progress]:
        """Get user's progress for specific lesson"""
        # Validate user exists
        user = self.user_service.get_user(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return self.repository.get_user_progress(user_id, lesson_id)
    
    def get_user_all_progress(self, user_id: UUID, skip: int = 0, limit: int = 100) -> List[Progress]:
        """Get all progress records for a user"""
        # Validate user exists
        user = self.user_service.get_user(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return self.repository.get_user_all_progress(user_id, skip=skip, limit=limit)
    
    def update_progress(self, progress_id: UUID, progress_update: ProgressUpdate) -> Optional[Progress]:
        """Update progress record"""
        progress = self.repository.update(progress_id, progress_update)
        if not progress:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Progress record not found"
            )
        return progress
    
    def start_lesson(self, user_id: UUID, lesson_id: UUID) -> Progress:
        """Start a lesson for a user"""
        # Check if progress already exists
        existing = self.repository.get_user_progress(user_id, lesson_id)
        if existing:
            if existing.completion_status == "not_started":
                # Update to in_progress
                return self.repository.update(
                    existing.id, 
                    ProgressUpdate(completion_status="in_progress")
                )
            else:
                return existing
        else:
            # Create new progress record
            return self.create_progress(
                ProgressCreate(
                    user_id=user_id,
                    lesson_id=lesson_id,
                    completion_status="in_progress"
                )
            )
    
    def complete_lesson(self, user_id: UUID, lesson_id: UUID, score: Optional[float] = None, time_spent_minutes: Optional[int] = None) -> Progress:
        """Mark lesson as completed for user"""
        progress = self.repository.get_user_progress(user_id, lesson_id)
        if not progress:
            # Use repository.create directly instead of create_progress to avoid
            # the duplicate-guard race condition: create_progress re-checks for an
            # existing record and raises HTTP 400 if start_lesson committed one
            # between our initial check above and the insert below.
            return self.repository.create(
                ProgressCreate(
                    user_id=user_id,
                    lesson_id=lesson_id,
                    completion_status="completed",
                    score=score,
                    time_spent_minutes=time_spent_minutes or 0
                )
            )
        # Update existing progress (whatever status it currently has)
        update_data: dict = {"completion_status": "completed"}
        if score is not None:
            update_data["score"] = score
        if time_spent_minutes is not None:
            update_data["time_spent_minutes"] = (progress.time_spent_minutes or 0) + time_spent_minutes
        return self.repository.update(
            progress.id,
            ProgressUpdate(**update_data)
        )
    
    def get_user_stats(self, user_id: UUID) -> dict:
        """Get user learning statistics"""
        # Validate user exists
        user = self.user_service.get_user(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        completed_count = self.repository.get_completed_lessons_count(user_id)
        avg_score = self.repository.get_user_average_score(user_id)
        recent_activity = self.repository.get_recent_activity(user_id, limit=5)
        
        return {
            "completed_lessons": completed_count,
            "average_score": round(avg_score, 2),
            "recent_activity": len(recent_activity),
            "skill_level": user.skill_level
        }
    
    def get_lesson_stats(self, lesson_id: UUID) -> dict:
        """Get lesson statistics"""
        # Validate lesson exists
        lesson = self.lesson_service.get_lesson(lesson_id)
        if not lesson:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Lesson not found"
            )
        
        return self.repository.get_lesson_progress_stats(lesson_id)
    
    def get_users_needing_review(self, score_threshold: float = 70.0) -> List[Progress]:
        """Get users who might need additional help"""
        return self.repository.get_users_needing_review(score_threshold)
