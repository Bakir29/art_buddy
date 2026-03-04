from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from app.entities.schemas import LessonRecommendation, RecommendationResponse
from app.services.user_service import UserService
from app.services.lesson_service import LessonService
from app.services.progress_service import ProgressService
from fastapi import HTTPException, status


class RecommendationService:
    
    def __init__(self, db: Session):
        self.db = db
        self.user_service = UserService(db)
        self.lesson_service = LessonService(db)
        self.progress_service = ProgressService(db)
    
    def get_recommendations_for_user(self, user_id: UUID, limit: int = 5) -> RecommendationResponse:
        """Get lesson recommendations for a user"""
        # Validate user exists
        user = self.user_service.get_user(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        recommendations = []
        
        # Get user's current progress
        user_progress = self.progress_service.get_user_all_progress(user_id)
        completed_lesson_ids = {
            p.lesson_id for p in user_progress 
            if p.completion_status == "completed"
        }
        in_progress_lesson_ids = {
            p.lesson_id for p in user_progress 
            if p.completion_status == "in_progress"
        }
        
        # 1. Prioritize lessons matching user's skill level
        skill_level_lessons = self.lesson_service.get_lessons(
            difficulty=user.skill_level,
            limit=50
        )
        
        for lesson in skill_level_lessons:
            if lesson.id not in completed_lesson_ids and lesson.id not in in_progress_lesson_ids:
                # Check if prerequisites are met
                if self._check_prerequisites_met(lesson.id, completed_lesson_ids):
                    recommendations.append(LessonRecommendation(
                        lesson=lesson,
                        reason=f"Matches your {user.skill_level} skill level",
                        priority=8
                    ))
        
        # 2. If user is beginner, recommend lessons without prerequisites
        if user.skill_level == "beginner" and len(recommendations) < limit:
            beginner_lessons = self.lesson_service.get_beginner_lessons(limit=20)
            for lesson in beginner_lessons:
                if lesson.id not in completed_lesson_ids and lesson.id not in in_progress_lesson_ids:
                    if not any(r.lesson.id == lesson.id for r in recommendations):
                        recommendations.append(LessonRecommendation(
                            lesson=lesson,
                            reason="Perfect for beginners - no prerequisites required",
                            priority=9
                        ))
        
        # 3. Recommend next difficulty level if user has completed many lessons
        if len(completed_lesson_ids) >= 3:
            next_difficulty = self._get_next_difficulty_level(user.skill_level)
            if next_difficulty:
                next_level_lessons = self.lesson_service.get_lessons(
                    difficulty=next_difficulty,
                    limit=10
                )
                for lesson in next_level_lessons:
                    if lesson.id not in completed_lesson_ids and lesson.id not in in_progress_lesson_ids:
                        if self._check_prerequisites_met(lesson.id, completed_lesson_ids):
                            if not any(r.lesson.id == lesson.id for r in recommendations):
                                recommendations.append(LessonRecommendation(
                                    lesson=lesson,
                                    reason=f"Ready to advance to {next_difficulty} level",
                                    priority=7
                                ))
        
        # 4. If user has low scores, recommend review lessons
        user_stats = self.progress_service.get_user_stats(user_id)
        if user_stats["average_score"] < 75.0 and user_stats["completed_lessons"] > 0:
            review_lessons = self.lesson_service.get_lessons(
                lesson_type="exercise",
                difficulty=user.skill_level,
                limit=10
            )
            for lesson in review_lessons:
                if lesson.id not in completed_lesson_ids and lesson.id not in in_progress_lesson_ids:
                    if not any(r.lesson.id == lesson.id for r in recommendations):
                        recommendations.append(LessonRecommendation(
                            lesson=lesson,
                            reason="Practice exercises to improve your scores",
                            priority=6
                        ))
        
        # Sort by priority (descending) and limit results
        recommendations.sort(key=lambda x: x.priority, reverse=True)
        limited_recommendations = recommendations[:limit]
        
        return RecommendationResponse(
            recommendations=limited_recommendations,
            total_count=len(limited_recommendations)
        )
    
    def _check_prerequisites_met(self, lesson_id: UUID, completed_lesson_ids: set) -> bool:
        """Check if lesson prerequisites are met"""
        lesson = self.lesson_service.get_lesson(lesson_id)
        if not lesson or not lesson.prerequisites:
            return True
        
        return all(prereq_id in completed_lesson_ids for prereq_id in lesson.prerequisites)
    
    def _get_next_difficulty_level(self, current_level: str) -> str:
        """Get next difficulty level for progression"""
        difficulty_progression = {
            "beginner": "intermediate",
            "intermediate": "advanced",
            "advanced": None  # No next level
        }
        return difficulty_progression.get(current_level)
