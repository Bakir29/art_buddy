from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
from app.database import get_db
from app.entities.schemas import Lesson, LessonCreate, LessonUpdate, User
from app.entities.models import QuizQuestion
from app.services.lesson_service import LessonService
from app.auth.dependencies import get_current_active_user

router = APIRouter()


@router.get("/", response_model=List[Lesson])
async def get_lessons(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    difficulty: Optional[str] = Query(None, regex="^(beginner|intermediate|advanced)$"),
    lesson_type: Optional[str] = Query(None, regex="^(tutorial|exercise|quiz)$"),
    search: Optional[str] = Query(None, description="Search in title and content"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get lessons with optional filtering
    """
    lesson_service = LessonService(db)
    return lesson_service.get_lessons(
        skip=skip, 
        limit=limit, 
        difficulty=difficulty,
        lesson_type=lesson_type,
        search=search
    )


@router.get("/beginner", response_model=List[Lesson])
async def get_beginner_lessons(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get lessons suitable for beginners (no prerequisites)
    """
    lesson_service = LessonService(db)
    return lesson_service.get_beginner_lessons(skip=skip, limit=limit)


@router.get("/{lesson_id}/quiz")
async def get_lesson_quiz(
    lesson_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get quiz questions for a specific lesson
    """
    # Get quiz questions for this lesson  
    quiz_questions = db.query(QuizQuestion).filter(QuizQuestion.lesson_id == lesson_id).all()
    
    if not quiz_questions:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No quiz found for lesson {lesson_id}"
        )
    
    # Format quiz questions for frontend
    formatted_questions = []
    for q in quiz_questions:
        # Find the index of the correct answer in the options
        correct_answer_index = 0
        if q.options and q.correct_answer:
            try:
                correct_answer_index = q.options.index(q.correct_answer)
            except (ValueError, AttributeError):
                # If answer not in options, default to 0
                correct_answer_index = 0
        
        formatted_questions.append({
            "id": str(q.id),
            "question": q.question_text,
            "options": q.options if q.options else [],
            "correct_answer": correct_answer_index,
            "explanation": q.explanation or "",
            "difficulty": "medium",  # Default difficulty
            "question_type": q.question_type
        })
    
    return {
        "lesson_id": str(lesson_id),
        "questions": formatted_questions,
        "total_questions": len(formatted_questions)
    }


@router.get("/{lesson_id}/validate-prerequisites")
async def validate_lesson_prerequisites(
    lesson_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Validate that all lesson prerequisites exist
    """
    lesson_service = LessonService(db)
    is_valid = lesson_service.validate_prerequisites(lesson_id)
    return {"valid": is_valid}


@router.get("/{lesson_id}", response_model=Lesson)
async def get_lesson(
    lesson_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get lesson by ID
    """
    lesson_service = LessonService(db)
    return lesson_service.get_lesson(lesson_id)


@router.post("/", response_model=Lesson, status_code=status.HTTP_201_CREATED)
async def create_lesson(
    lesson: LessonCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Create a new lesson (admin function)
    """
    lesson_service = LessonService(db)
    return lesson_service.create_lesson(lesson)


@router.put("/{lesson_id}", response_model=Lesson)
async def update_lesson(
    lesson_id: UUID,
    lesson_update: LessonUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Update lesson by ID (admin function)
    """
    lesson_service = LessonService(db)
    return lesson_service.update_lesson(lesson_id, lesson_update)


@router.delete("/{lesson_id}")
async def delete_lesson(
    lesson_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Delete lesson by ID (admin function)
    """
    lesson_service = LessonService(db)
    success = lesson_service.delete_lesson(lesson_id)
    return {"message": "Lesson deleted successfully"}
