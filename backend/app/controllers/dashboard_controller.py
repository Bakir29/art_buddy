from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.auth.dependencies import get_current_user
from app.entities.models import User, Lesson, Progress
from app.database import get_db
from sqlalchemy import desc

router = APIRouter()

@router.get("/test")
async def test_auth(
    current_user: User = Depends(get_current_user)
):
    """Simple test endpoint to verify authentication is working"""
    return {
        "success": True,
        "message": "Authentication working",
        "user": {
            "id": str(current_user.id),
            "name": current_user.name,
            "email": current_user.email
        }
    }

@router.get("/dashboard")
async def get_dashboard_data(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Optimized endpoint that returns all dashboard data in a single request.
    Combines progress summary, recent lessons, and user stats.
    """
    
    try:
        # Get basic lesson count
        total_lessons = db.query(Lesson).count()
        
        # Get recent lessons (limit to 3 for dashboard)
        recent_lessons = db.query(Lesson).order_by(desc(Lesson.created_at)).limit(3).all()
        recent_lessons_data = [
            {
                "id": str(lesson.id),
                "title": lesson.title,
                "difficulty": lesson.difficulty,
                "duration_minutes": lesson.duration_minutes or 30,
                "lesson_type": lesson.lesson_type or "tutorial"
            }
            for lesson in recent_lessons
        ]
        
        # Get user stats from progress data 
        user_progress = db.query(Progress).filter(Progress.user_id == current_user.id).all()
        completed_lessons = len([p for p in user_progress if p.completion_status == "completed"])
        total_lessons = db.query(Lesson).count()
        
        user_stats = {
            "completed_lessons": completed_lessons,
            "total_lessons": total_lessons,
            "current_streak": 0  # Simplified for now
        }
        
        # Combine all data
        dashboard_data = {
            "progress": {
                "completed_lessons": completed_lessons,
                "total_lessons": total_lessons,
                "current_streak": 0
            },
            "recent_lessons": recent_lessons_data,  
            "stats": user_stats,
            "user_info": {
                "name": current_user.name,
                "email": current_user.email,
                "id": str(current_user.id)
            }
        }
        
        return {
            "success": True,
            "data": dashboard_data,
            "message": "Dashboard data retrieved successfully"
        }
        
    except Exception as e:
        # Return a structured error response
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "message": f"Error fetching dashboard data: {str(e)}",
                "data": {
                    "progress": None,
                    "recent_lessons": [],
                    "stats": None,
                    "user_info": {
                        "name": current_user.name,
                        "email": current_user.email,
                        "id": str(current_user.id)
                    }
                }
            }
        )