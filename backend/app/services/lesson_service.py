from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
from app.entities.models import Lesson
from app.entities.schemas import LessonCreate, LessonUpdate
from app.repositories.lesson_repository import LessonRepository
from fastapi import HTTPException, status


class LessonService:
    
    def __init__(self, db: Session):
        self.db = db
        self.repository = LessonRepository(db)
    
    def create_lesson(self, lesson: LessonCreate) -> Lesson:
        """Create a new lesson"""
        return self.repository.create(lesson)
    
    def get_lesson(self, lesson_id: UUID) -> Optional[Lesson]:
        """Get lesson by ID"""
        lesson = self.repository.get_by_id(lesson_id)
        if not lesson:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Lesson not found"
            )
        return lesson
    
    def get_lessons(
        self, 
        skip: int = 0, 
        limit: int = 100,
        difficulty: Optional[str] = None,
        lesson_type: Optional[str] = None,
        search: Optional[str] = None
    ) -> List[Lesson]:
        """Get lessons with optional filtering"""
        if search:
            return self.repository.search_lessons(search, skip=skip, limit=limit)
        elif difficulty:
            return self.repository.get_by_difficulty(difficulty, skip=skip, limit=limit)
        elif lesson_type:
            return self.repository.get_by_type(lesson_type, skip=skip, limit=limit)
        else:
            return self.repository.get_all(skip=skip, limit=limit)
    
    def get_beginner_lessons(self, skip: int = 0, limit: int = 100) -> List[Lesson]:
        """Get lessons suitable for beginners (no prerequisites)"""
        return self.repository.get_lessons_without_prerequisites(skip=skip, limit=limit)
    
    def update_lesson(self, lesson_id: UUID, lesson_update: LessonUpdate) -> Optional[Lesson]:
        """Update lesson"""
        lesson = self.repository.update(lesson_id, lesson_update)
        if not lesson:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Lesson not found"
            )
        return lesson
    
    def delete_lesson(self, lesson_id: UUID) -> bool:
        """Delete lesson"""
        success = self.repository.delete(lesson_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Lesson not found"
            )
        return success
    
    def validate_prerequisites(self, lesson_id: UUID) -> bool:
        """Check if all prerequisites for a lesson exist"""
        lesson = self.repository.get_by_id(lesson_id)
        if not lesson or not lesson.prerequisites:
            return True
        
        for prereq_id in lesson.prerequisites:
            if not self.repository.get_by_id(prereq_id):
                return False
        
        return True
