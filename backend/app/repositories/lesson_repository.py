from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import List, Optional, Dict, Any
from uuid import UUID
from app.entities.models import Lesson
from app.entities.schemas import LessonCreate, LessonUpdate


class LessonRepository:
    
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, lesson: LessonCreate) -> Lesson:
        """Create a new lesson"""
        db_lesson = Lesson(
            title=lesson.title,
            content=lesson.content,
            difficulty=lesson.difficulty,
            lesson_type=lesson.lesson_type,
            duration_minutes=lesson.duration_minutes,
            prerequisites=lesson.prerequisites
        )
        self.db.add(db_lesson)
        self.db.commit()
        self.db.refresh(db_lesson)
        return db_lesson
    
    def get_by_id(self, lesson_id: UUID) -> Optional[Lesson]:
        """Get lesson by ID"""
        return self.db.query(Lesson).filter(
            and_(Lesson.id == lesson_id, Lesson.is_active == True)
        ).first()
    
    def get_all(self, skip: int = 0, limit: int = 100) -> List[Lesson]:
        """Get all active lessons with pagination"""
        return self.db.query(Lesson).filter(
            Lesson.is_active == True
        ).offset(skip).limit(limit).all()
    
    def get_by_difficulty(self, difficulty: str, skip: int = 0, limit: int = 100) -> List[Lesson]:
        """Get lessons by difficulty level"""
        return self.db.query(Lesson).filter(
            and_(Lesson.difficulty == difficulty, Lesson.is_active == True)
        ).offset(skip).limit(limit).all()
    
    def get_by_type(self, lesson_type: str, skip: int = 0, limit: int = 100) -> List[Lesson]:
        """Get lessons by type"""
        return self.db.query(Lesson).filter(
            and_(Lesson.lesson_type == lesson_type, Lesson.is_active == True)
        ).offset(skip).limit(limit).all()
    
    def search_lessons(self, query: str, skip: int = 0, limit: int = 100) -> List[Lesson]:
        """Search lessons by title or content"""
        search_pattern = f"%{query}%"
        return self.db.query(Lesson).filter(
            and_(
                or_(
                    Lesson.title.ilike(search_pattern),
                    Lesson.content.ilike(search_pattern)
                ),
                Lesson.is_active == True
            )
        ).offset(skip).limit(limit).all()
    
    def update(self, lesson_id: UUID, lesson_update: LessonUpdate) -> Optional[Lesson]:
        """Update lesson"""
        db_lesson = self.get_by_id(lesson_id)
        if not db_lesson:
            return None
        
        update_data = lesson_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_lesson, field, value)
        
        self.db.commit()
        self.db.refresh(db_lesson)
        return db_lesson
    
    def delete(self, lesson_id: UUID) -> bool:
        """Soft delete lesson"""
        db_lesson = self.get_by_id(lesson_id)
        if not db_lesson:
            return False
        
        db_lesson.is_active = False
        self.db.commit()
        return True
    
    def get_lessons_without_prerequisites(self, skip: int = 0, limit: int = 100) -> List[Lesson]:
        """Get lessons that don't have prerequisites (good for beginners)"""
        return self.db.query(Lesson).filter(
            and_(
                Lesson.prerequisites == [],
                Lesson.is_active == True
            )
        ).offset(skip).limit(limit).all()
