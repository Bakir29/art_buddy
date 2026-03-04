from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from uuid import UUID
from app.database import get_db
from app.entities.schemas import RecommendationResponse, User
from app.services.recommendation_service import RecommendationService
from app.auth.dependencies import get_current_active_user

router = APIRouter()


@router.get("/user/{user_id}", response_model=RecommendationResponse)
async def get_recommendations(
    user_id: UUID,
    limit: int = Query(5, ge=1, le=20, description="Number of recommendations to return"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get lesson recommendations for a specific user
    """
    recommendation_service = RecommendationService(db)
    return recommendation_service.get_recommendations_for_user(user_id, limit=limit)


@router.get("/me", response_model=RecommendationResponse)
async def get_my_recommendations(
    limit: int = Query(5, ge=1, le=20, description="Number of recommendations to return"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get lesson recommendations for current user
    """
    recommendation_service = RecommendationService(db)
    return recommendation_service.get_recommendations_for_user(current_user.id, limit=limit)
