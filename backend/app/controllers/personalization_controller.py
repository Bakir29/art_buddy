from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional

from app.database import get_db
from app.auth.dependencies import get_current_user
from app.config import get_openai_client
from app.entities.personalization import (
    UserPersonalizationProfile, PersonalizedRecommendation, AdaptiveLearningPath,
    LearningGoal, PersonalizationInsight, ContentPersonalization,
    LearningStyle, PersonalityType, DifficultyPreference
)
from app.services.personalization_service import PersonalizationService
from app.rag.rag_service import RAGService

router = APIRouter(prefix="/api/personalization", tags=["AI Personalization"])
security = HTTPBearer()

def get_personalization_service(db: Session = Depends(get_db)) -> PersonalizationService:
    """Dependency to get personalization service."""
    openai_client = get_openai_client()
    rag_service = RAGService(db, openai_client)
    return PersonalizationService(db, openai_client, rag_service)

@router.get("/profile", response_model=UserPersonalizationProfile)
async def get_user_profile(
    current_user = Depends(get_current_user),
    service: PersonalizationService = Depends(get_personalization_service)
):
    """
    Get comprehensive personalization profile for the current user.
    
    Returns AI-analyzed profile including:
    - Learning style and personality type
    - Behavioral patterns and preferences  
    - Adaptive parameters and scores
    - Artistic interests and focus areas
    """
    try:
        profile = await service.get_or_create_user_profile(current_user["user_id"])
        return profile
        
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to retrieve personalization profile: {str(e)}"
        )

@router.get("/recommendations", response_model=List[PersonalizedRecommendation])
async def get_personalized_recommendations(
    limit: int = Query(10, le=20, description="Maximum number of recommendations"),
    context: Optional[str] = Query(None, description="Additional context for recommendations"),
    current_user = Depends(get_current_user),
    service: PersonalizationService = Depends(get_personalization_service)
):
    """
    Get AI-generated personalized content recommendations.
    
    Returns intelligent recommendations based on:
    - User's learning style and preferences
    - Performance patterns and history
    - Current context and timing
    - Artistic interests and goals
    """
    try:
        context_data = {"additional_context": context} if context else None
        
        recommendations = await service.generate_personalized_recommendations(
            user_id=current_user["user_id"],
            context=context_data
        )
        
        return recommendations[:limit]
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate recommendations: {str(e)}"
        )

@router.post("/learning-path", response_model=AdaptiveLearningPath)
async def create_adaptive_learning_path(
    goal_title: str,
    goal_description: str,
    target_skill_level: str,
    target_weeks: int = 8,
    priority_level: int = 3,
    current_user = Depends(get_current_user),
    service: PersonalizationService = Depends(get_personalization_service)
):
    """
    Create a personalized adaptive learning path for a specific goal.
    
    - **goal_title**: Title of the learning goal
    - **goal_description**: Detailed description of what to achieve
    - **target_skill_level**: Target skill level (beginner, intermediate, advanced)
    - **target_weeks**: Expected completion timeframe in weeks
    - **priority_level**: Goal priority (1-5, where 5 is highest)
    """
    try:
        # Create learning goal
        from datetime import datetime, timedelta
        
        goal = LearningGoal(
            goal_id=str(uuid.uuid4()),
            user_id=current_user["user_id"],
            title=goal_title,
            description=goal_description,
            target_skill_level=target_skill_level,
            target_completion_date=datetime.utcnow() + timedelta(weeks=target_weeks),
            priority_level=priority_level,
            current_progress=0.0,
            milestones=[],
            completed_milestones=[],
            recommended_weekly_time=180,  # 3 hours default
            suggested_activities=[],
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        learning_path = await service.create_adaptive_learning_path(
            user_id=current_user["user_id"],
            goal=goal
        )
        
        return learning_path
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create learning path: {str(e)}"
        )

@router.post("/content/{content_id}/personalize", response_model=ContentPersonalization)
async def personalize_content(
    content_id: str,
    current_user = Depends(get_current_user),
    service: PersonalizationService = Depends(get_personalization_service)
):
    """
    Get personalized presentation of specific content.
    
    Adapts content based on:
    - User's learning style preferences
    - Current skill level and difficulty needs
    - Personalized scaffolding and support
    - Visual and interaction preferences
    """
    try:
        personalization = await service.adapt_content_presentation(
            content_id=content_id,
            user_id=current_user["user_id"]
        )
        
        return personalization
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to personalize content: {str(e)}"
        )

@router.post("/interaction-feedback")
async def update_profile_from_interaction(
    performance_score: Optional[float] = None,
    session_duration: Optional[int] = None,
    completion_rate: Optional[float] = None,
    content_type: Optional[str] = None,
    user_satisfaction: Optional[float] = None,
    additional_data: Optional[Dict[str, Any]] = None,
    current_user = Depends(get_current_user),
    service: PersonalizationService = Depends(get_personalization_service)
):
    """
    Update personalization profile based on user interaction data.
    
    - **performance_score**: Score from 0-1 for content performance
    - **session_duration**: Session length in minutes
    - **completion_rate**: Completion rate from 0-1
    - **content_type**: Type of content interacted with
    - **user_satisfaction**: User satisfaction rating 0-1
    - **additional_data**: Any additional interaction metadata
    """
    try:
        interaction_data = {
            "performance_score": performance_score,
            "session_duration": session_duration,
            "completion_rate": completion_rate,
            "content_type": content_type,
            "user_satisfaction": user_satisfaction,
            "timestamp": datetime.utcnow()
        }
        
        if additional_data:
            interaction_data.update(additional_data)
        
        updated_profile = await service.update_profile_from_interaction(
            user_id=current_user["user_id"],
            interaction_data=interaction_data
        )
        
        return {
            "message": "Profile updated successfully",
            "updated_attributes": [
                "difficulty_level", "session_preferences", "motivation_level"
            ]
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update profile: {str(e)}"
        )

@router.get("/insights", response_model=List[PersonalizationInsight])
async def get_personalization_insights(
    current_user = Depends(get_current_user),
    service: PersonalizationService = Depends(get_personalization_service)
):
    """
    Get AI-generated insights about user's learning patterns.
    
    Provides intelligent insights about:
    - Learning effectiveness patterns
    - Optimization opportunities  
    - Behavioral trends and recommendations
    - Personalization adjustments
    """
    try:
        insights = await service.generate_personalization_insights(
            user_id=current_user["user_id"]
        )
        
        return insights
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate insights: {str(e)}"
        )

@router.get("/learning-styles")
async def get_available_learning_styles():
    """Get list of available learning styles for profile customization."""
    return {
        "learning_styles": [
            {
                "value": style.value,
                "label": style.value.replace("_", " ").title(),
                "description": get_learning_style_description(style)
            }
            for style in LearningStyle
        ]
    }

@router.get("/personality-types")
async def get_available_personality_types():
    """Get list of available personality types for profile insights."""
    return {
        "personality_types": [
            {
                "value": ptype.value,
                "label": ptype.value.replace("_", " ").title(),
                "description": get_personality_type_description(ptype)
            }
            for ptype in PersonalityType
        ]
    }

@router.post("/profile/manual-update")
async def manually_update_profile(
    learning_style: Optional[LearningStyle] = None,
    preferred_session_length: Optional[int] = None,
    notification_preferences: Optional[Dict[str, bool]] = None,
    artistic_interests: Optional[List[str]] = None,
    difficulty_preference: Optional[DifficultyPreference] = None,
    current_user = Depends(get_current_user),
    service: PersonalizationService = Depends(get_personalization_service)
):
    """
    Allow users to manually update their personalization preferences.
    
    Users can override AI-detected preferences with manual selections.
    """
    try:
        # Get current profile
        profile = await service.get_or_create_user_profile(current_user["user_id"])
        
        # Apply manual updates
        updates = {}
        if learning_style:
            updates["learning_style"] = learning_style
        if preferred_session_length:
            updates["session_length_preference"] = preferred_session_length
        if notification_preferences:
            current_prefs = profile.notification_preferences.copy()
            current_prefs.update(notification_preferences)
            updates["notification_preferences"] = current_prefs
        if artistic_interests:
            updates["interested_techniques"] = artistic_interests
        if difficulty_preference:
            updates["difficulty_preference"] = difficulty_preference
        
        # Apply updates
        for key, value in updates.items():
            setattr(profile, key, value)
        
        profile.last_updated = datetime.utcnow()
        
        return {
            "message": "Profile preferences updated successfully",
            "updated_fields": list(updates.keys())
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update profile preferences: {str(e)}"
        )

@router.get("/dashboard")
async def get_personalization_dashboard(
    current_user = Depends(get_current_user),
    service: PersonalizationService = Depends(get_personalization_service)
):
    """
    Get comprehensive personalization dashboard data.
    
    Provides all personalization-related data for dashboard display.
    """
    try:
        # Get profile and recommendations
        profile = await service.get_or_create_user_profile(current_user["user_id"])
        recommendations = await service.generate_personalized_recommendations(
            current_user["user_id"]
        )
        insights = await service.generate_personalization_insights(
            current_user["user_id"]
        )
        
        dashboard_data = {
            "profile_summary": {
                "learning_style": profile.learning_style.value,
                "personality_type": profile.personality_type.value,
                "skill_confidence": profile.confidence_level,
                "motivation_level": profile.motivation_level,
                "consistency_score": profile.consistency_score
            },
            "top_recommendations": [
                {
                    "title": rec.title,
                    "description": rec.description,
                    "relevance_score": rec.relevance_score,
                    "estimated_duration": rec.estimated_duration
                } for rec in recommendations[:5]
            ],
            "key_insights": [
                {
                    "title": insight.title,
                    "description": insight.description,
                    "impact_potential": insight.impact_potential
                } for insight in insights[:3]
            ],
            "preferences": {
                "preferred_session_length": profile.session_length_preference,
                "peak_learning_hours": profile.preferred_learning_times,
                "favorite_content_types": [ct.value for ct in profile.preferred_content_types]
            },
            "adaptive_parameters": {
                "current_difficulty": profile.current_difficulty_level,
                "learning_velocity": profile.learning_velocity,
                "engagement_score": profile.engagement_patterns.get("consistency_score", 0)
            }
        }
        
        return dashboard_data
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate dashboard data: {str(e)}"
        )

# Helper functions
def get_learning_style_description(style: LearningStyle) -> str:
    """Get description for learning style."""
    descriptions = {
        LearningStyle.VISUAL: "Learn best through images, diagrams, and visual examples",
        LearningStyle.KINESTHETIC: "Learn best through hands-on practice and physical activities", 
        LearningStyle.AUDITORY: "Learn best through listening and verbal explanation",
        LearningStyle.READING_WRITING: "Learn best through reading text and taking notes",
        LearningStyle.MULTIMODAL: "Learn effectively through multiple different approaches"
    }
    return descriptions.get(style, "")

def get_personality_type_description(ptype: PersonalityType) -> str:
    """Get description for personality type.""" 
    descriptions = {
        PersonalityType.PERFECTIONIST: "Focuses on mastering details and achieving high standards",
        PersonalityType.EXPLORER: "Enjoys trying new techniques and experimenting with styles",
        PersonalityType.COMPETITOR: "Motivated by challenges and comparing progress with others",
        PersonalityType.COLLABORATOR: "Thrives in group learning and peer interaction",
        PersonalityType.FOCUSED_LEARNER: "Prefers structured, goal-oriented learning paths",
        PersonalityType.CASUAL_LEARNER: "Enjoys flexible, relaxed approach to learning"
    }
    return descriptions.get(ptype, "")

# Import necessary modules
import uuid
from datetime import datetime
