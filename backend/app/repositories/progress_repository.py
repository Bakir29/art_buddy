from sqlalchemy.orm import Session
from sqlalchemy import and_, func, desc
from typing import List, Optional
from uuid import UUID
from datetime import datetime
from app.entities.models import Progress, User, Lesson
from app.entities.schemas import ProgressCreate, ProgressUpdate


class ProgressRepository:
    
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, progress: ProgressCreate) -> Progress:
        """Create a new progress record"""
        db_progress = Progress(
            user_id=progress.user_id,
            lesson_id=progress.lesson_id,
            completion_status=progress.completion_status,
            score=progress.score,
            time_spent_minutes=progress.time_spent_minutes,
            started_at=datetime.utcnow() if progress.completion_status != "not_started" else None
        )
        self.db.add(db_progress)
        self.db.commit()
        self.db.refresh(db_progress)
        return db_progress
    
    def get_by_id(self, progress_id: UUID) -> Optional[Progress]:
        """Get progress record by ID"""
        return self.db.query(Progress).filter(Progress.id == progress_id).first()
    
    def get_user_progress(self, user_id: UUID, lesson_id: UUID) -> Optional[Progress]:
        """Get specific user's progress for a lesson"""
        return self.db.query(Progress).filter(
            and_(Progress.user_id == user_id, Progress.lesson_id == lesson_id)
        ).first()
    
    def get_user_all_progress(self, user_id: UUID, skip: int = 0, limit: int = 100) -> List[Progress]:
        """Get all progress records for a user"""
        # Order by created_at ASC so that if duplicate records exist for the same
        # lesson (possible race condition between start_lesson and complete_lesson),
        # the frontend's progressMap will keep the last-seen record.  The newest
        # record (latest created_at) is therefore the authoritative one.
        return self.db.query(Progress).filter(
            Progress.user_id == user_id
        ).order_by(Progress.created_at.asc()).offset(skip).limit(limit).all()
    
    def get_lesson_progress_stats(self, lesson_id: UUID) -> dict:
        """Get progress statistics for a lesson"""
        stats = self.db.query(
            Progress.completion_status,
            func.count(Progress.id).label('count'),
            func.avg(Progress.score).label('avg_score')
        ).filter(
            Progress.lesson_id == lesson_id
        ).group_by(Progress.completion_status).all()
        
        result = {'not_started': 0, 'in_progress': 0, 'completed': 0, 'avg_score': 0.0}
        total_completed = 0
        total_score = 0.0
        
        for status, count, avg_score in stats:
            result[status] = count
            if status == 'completed' and avg_score:
                total_completed = count
                total_score = avg_score
        
        if total_completed > 0:
            result['avg_score'] = total_score
        
        return result
    
    def get_completed_lessons_count(self, user_id: UUID) -> int:
        """Get count of completed lessons for user"""
        return self.db.query(Progress).filter(
            and_(Progress.user_id == user_id, Progress.completion_status == 'completed')
        ).count()
    
    def get_user_average_score(self, user_id: UUID) -> float:
        """Get user's average score across completed lessons"""
        result = self.db.query(
            func.avg(Progress.score)
        ).filter(
            and_(
                Progress.user_id == user_id, 
                Progress.completion_status == 'completed',
                Progress.score.isnot(None)
            )
        ).scalar()
        
        return result or 0.0
    
    def update(self, progress_id: UUID, progress_update: ProgressUpdate) -> Optional[Progress]:
        """Update progress record"""
        db_progress = self.get_by_id(progress_id)
        if not db_progress:
            return None
        
        update_data = progress_update.model_dump(exclude_unset=True)
        
        # Handle status transitions
        if 'completion_status' in update_data:
            new_status = update_data['completion_status']
            if new_status == 'in_progress' and db_progress.started_at is None:
                db_progress.started_at = datetime.utcnow()
            elif new_status == 'completed':
                db_progress.completed_at = datetime.utcnow()
                if db_progress.started_at is None:
                    db_progress.started_at = datetime.utcnow()
        
        # Update attempts counter
        if 'completion_status' in update_data or 'score' in update_data:
            db_progress.attempts += 1
        
        for field, value in update_data.items():
            setattr(db_progress, field, value)
        
        self.db.commit()
        self.db.refresh(db_progress)
        return db_progress
    
    def get_recent_activity(self, user_id: UUID, limit: int = 10) -> List[Progress]:
        """Get user's recent learning activity"""
        return self.db.query(Progress).filter(
            Progress.user_id == user_id
        ).order_by(desc(Progress.updated_at)).limit(limit).all()
    
    def get_users_needing_review(self, score_threshold: float = 70.0) -> List[Progress]:
        """Get users who scored below threshold and might need review"""
        return self.db.query(Progress).filter(
            and_(
                Progress.completion_status == 'completed',
                Progress.score < score_threshold,
                Progress.score.isnot(None)
            )
        ).all()
