from pydantic import BaseModel
from datetime import datetime
from typing import List, Dict, Any, Optional
from enum import Enum

class LearningStyle(str, Enum):
    VISUAL = "visual"
    KINESTHETIC = "kinesthetic"
    AUDITORY = "auditory"
    READING_WRITING = "reading_writing"
    MULTIMODAL = "multimodal"

class PersonalityType(str, Enum):
    PERFECTIONIST = "perfectionist"
    EXPLORER = "explorer"
    COMPETITOR = "competitor"
    COLLABORATOR = "collaborator"
    FOCUSED_LEARNER = "focused_learner"
    CASUAL_LEARNER = "casual_learner"

class ContentType(str, Enum):
    VIDEO_TUTORIAL = "video_tutorial"
    INTERACTIVE_EXERCISE = "interactive_exercise"
    READING_MATERIAL = "reading_material"
    PRACTICE_PROJECT = "practice_project"
    PEER_COLLABORATION = "peer_collaboration"
    AI_GUIDED_PRACTICE = "ai_guided_practice"
    QUIZ_ASSESSMENT = "quiz_assessment"

class DifficultyPreference(str, Enum):
    GRADUAL_PROGRESSION = "gradual_progression"
    CHALLENGE_SEEKER = "challenge_seeker"
    COMFORT_ZONE = "comfort_zone"
    ADAPTIVE = "adaptive"

class UserPersonalizationProfile(BaseModel):
    user_id: str
    learning_style: LearningStyle
    personality_type: PersonalityType
    difficulty_preference: DifficultyPreference
    preferred_content_types: List[ContentType]
    
    # Learning preferences
    session_length_preference: int  # minutes
    preferred_learning_times: List[int]  # hours of day (0-23)
    notification_preferences: Dict[str, bool]
    
    # Artistic interests
    favorite_art_styles: List[str]
    interested_techniques: List[str]
    skill_focus_areas: List[str]
    
    # Behavioral patterns (learned from data)
    engagement_patterns: Dict[str, Any]
    learning_velocity: float  # lessons per week
    consistency_score: float  # 0-1
    
    # Personalization scores
    curiosity_score: float  # 0-1
    persistence_score: float  # 0-1
    collaboration_preference: float  # 0-1
    
    # Adaptive parameters
    current_difficulty_level: float  # 0-1
    motivation_level: float  # 0-1
    confidence_level: float  # 0-1
    
    last_updated: datetime
    created_at: datetime

class PersonalizedRecommendation(BaseModel):
    recommendation_id: str
    user_id: str
    recommendation_type: str  # lesson, exercise, content, etc.
    content_id: str
    title: str
    description: str
    
    # Personalization factors
    relevance_score: float  # 0-1
    difficulty_match: float  # 0-1
    style_match: float  # 0-1
    timing_score: float  # 0-1
    
    # Recommendation reasoning
    reasoning: List[str]  # Why this was recommended
    personalization_factors: Dict[str, float]
    
    # Metadata
    estimated_duration: int  # minutes
    prerequisites: List[str]
    learning_outcomes: List[str]
    
    created_at: datetime
    expires_at: Optional[datetime] = None

class AdaptiveLearningPath(BaseModel):
    path_id: str
    user_id: str
    title: str
    description: str
    
    # Path configuration
    total_lessons: int
    estimated_completion_weeks: int
    difficulty_curve: List[float]  # Difficulty progression
    
    # Current progress
    current_position: int
    completion_percentage: float
    lessons_completed: List[str]
    
    # Adaptive adjustments
    pace_adjustments: List[Dict[str, Any]]
    difficulty_adjustments: List[Dict[str, Any]]
    content_substitutions: List[Dict[str, Any]]
    
    # Path effectiveness
    user_satisfaction_score: Optional[float] = None
    completion_likelihood: float  # ML prediction
    
    created_at: datetime
    last_adjusted: Optional[datetime] = None

class LearningGoal(BaseModel):
    goal_id: str
    user_id: str
    title: str
    description: str
    
    # Goal details
    target_skill_level: str
    target_completion_date: datetime
    priority_level: int  # 1-5
    
    # Progress tracking
    current_progress: float  # 0-1
    milestones: List[Dict[str, Any]]
    completed_milestones: List[str]
    
    # Adaptive elements
    recommended_weekly_time: int  # minutes
    suggested_activities: List[str]
    
    created_at: datetime
    updated_at: datetime

class PersonalizationInsight(BaseModel):
    insight_id: str
    user_id: str
    insight_type: str  # pattern, recommendation, adjustment, etc.
    title: str
    description: str
    
    # Insight data
    confidence_score: float  # 0-1
    impact_potential: float  # 0-1
    supporting_evidence: List[str]
    
    # Actions
    suggested_actions: List[str]
    applied_adjustments: List[str]
    
    created_at: datetime
    acted_upon: bool = False

class ContentPersonalization(BaseModel):
    content_id: str
    user_id: str
    
    # Personalized presentation
    difficulty_adjustment: float  # -1 to 1 (easier to harder)
    content_emphasis: Dict[str, float]  # Which aspects to highlight
    additional_resources: List[str]
    
    # Adaptive scaffolding
    prerequisite_reminders: List[str]
    concept_reinforcements: List[str]
    extension_activities: List[str]
    
    # Presentation preferences
    preferred_explanation_style: str
    visual_aid_preferences: List[str]
    interaction_preferences: List[str]
    
    created_at: datetime
