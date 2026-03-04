from pydantic import BaseModel
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from enum import Enum

class AnalyticsPeriod(str, Enum):
    WEEK = "week"
    MONTH = "month" 
    QUARTER = "quarter"
    YEAR = "year"
    ALL_TIME = "all_time"

class MetricType(str, Enum):
    PROGRESS_SCORE = "progress_score"
    LESSON_COMPLETION = "lesson_completion"
    QUIZ_ACCURACY = "quiz_accuracy"
    ENGAGEMENT_TIME = "engagement_time"
    ARTWORK_ANALYSIS_SCORE = "artwork_analysis_score"
    STREAK_DAYS = "streak_days"

class LearningPattern(BaseModel):
    pattern_id: str
    user_id: str
    pattern_type: str  # "focused_learner", "consistent_practicer", "weekend_warrior", etc.
    confidence_score: float  # 0-1
    description: str
    identified_at: datetime

class ProgressPrediction(BaseModel):
    user_id: str
    predicted_skill_level: str
    current_trajectory: str  # "improving", "stable", "declining"
    estimated_completion_date: Optional[datetime]
    confidence_interval: float
    key_factors: List[str]
    recommendations: List[str]

class LearningInsight(BaseModel):
    insight_id: str
    user_id: str
    insight_type: str  # "strength", "weakness", "opportunity", "trend"
    title: str
    description: str
    impact_score: float  # 0-10
    actionable_steps: List[str]
    created_at: datetime

class PerformanceMetrics(BaseModel):
    metric_type: MetricType
    current_value: float
    previous_value: Optional[float]
    change_percentage: Optional[float]
    trend: str  # "increasing", "decreasing", "stable"
    percentile_rank: Optional[float]  # User's rank compared to others

class ComprehensiveAnalytics(BaseModel):
    user_id: str
    analysis_period: AnalyticsPeriod
    generated_at: datetime
    
    # Core metrics
    performance_metrics: List[PerformanceMetrics]
    
    # Insights and patterns
    learning_patterns: List[LearningPattern]
    insights: List[LearningInsight]
    
    # Predictions
    progress_prediction: ProgressPrediction
    
    # Detailed breakdowns
    skill_development: Dict[str, Any]  # By art topic/technique
    engagement_analysis: Dict[str, Any]  # Time patterns, frequency
    comparative_analysis: Dict[str, Any]  # vs peer group
    
    # Recommendations
    personalized_recommendations: List[str]
    focus_areas: List[str]
    next_milestones: List[Dict[str, Any]]

class AnalyticsRequest(BaseModel):
    period: AnalyticsPeriod = AnalyticsPeriod.MONTH
    include_predictions: bool = True
    include_comparisons: bool = True
    detailed_insights: bool = True
