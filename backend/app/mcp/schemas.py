"""
Model Context Protocol (MCP) schemas and data models.

Defines the request/response schemas for MCP tool interactions.
"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime
from enum import Enum


class ToolType(str, Enum):
    """Available MCP tool types"""
    GET_USER_PROGRESS = "get_user_progress"
    UPDATE_PROGRESS = "update_progress"
    GENERATE_LESSON = "generate_lesson"
    EVALUATE_QUIZ = "evaluate_quiz"
    SCHEDULE_REMINDER = "schedule_reminder"
    FETCH_RECOMMENDATIONS = "fetch_recommendations"
    GET_USER_PROFILE = "get_user_profile"
    UPDATE_USER_PROFILE = "update_user_profile"


class MCPRequest(BaseModel):
    """Base MCP request structure"""
    tool_name: ToolType
    parameters: Dict[str, Any] = Field(default_factory=dict)
    user_id: Optional[UUID] = None
    request_id: Optional[str] = None
    
    class Config:
        use_enum_values = True


class MCPResponse(BaseModel):
    """Base MCP response structure"""
    success: bool
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    tool_name: str
    request_id: Optional[str] = None
    execution_time_ms: Optional[float] = None


# Tool-specific request schemas
class GetUserProgressRequest(BaseModel):
    """Request to get user learning progress"""
    user_id: UUID
    lesson_ids: Optional[List[int]] = None  # Specific lessons, or all if None
    include_quiz_scores: bool = True
    include_time_spent: bool = True


class UpdateProgressRequest(BaseModel):
    """Request to update user progress"""
    user_id: UUID
    lesson_id: int
    completion_status: str  # 'started', 'in_progress', 'completed'
    score: Optional[float] = None
    time_spent_minutes: Optional[int] = None
    notes: Optional[str] = None


class GenerateLessonRequest(BaseModel):
    """Request to generate a new lesson"""
    user_id: UUID
    topic: str
    difficulty_level: str  # 'beginner', 'intermediate', 'advanced'
    lesson_type: str = "theory"  # 'theory', 'practical', 'mixed'
    duration_minutes: Optional[int] = 30
    prerequisites: Optional[List[str]] = None


class EvaluateQuizRequest(BaseModel):
    """Request to evaluate quiz answers"""
    user_id: UUID
    quiz_id: int
    answers: Dict[int, Any]  # question_id -> answer
    time_taken_minutes: Optional[int] = None


class ScheduleReminderRequest(BaseModel):
    """Request to schedule a reminder"""
    user_id: UUID
    reminder_type: str  # 'practice', 'lesson', 'quiz', 'general'
    schedule_time: datetime
    message: str
    recurring: bool = False
    recurring_pattern: Optional[str] = None  # 'daily', 'weekly', 'monthly'


class FetchRecommendationsRequest(BaseModel):
    """Request to fetch personalized recommendations"""
    user_id: UUID
    recommendation_type: str = "lessons"  # 'lessons', 'tutorials', 'exercises'
    limit: int = 5
    include_completed: bool = False
    skill_areas: Optional[List[str]] = None


class GetUserProfileRequest(BaseModel):
    """Request to get user profile information"""
    user_id: UUID
    include_progress_summary: bool = True
    include_preferences: bool = True


class UpdateUserProfileRequest(BaseModel):
    """Request to update user profile"""
    user_id: UUID
    updates: Dict[str, Any]  # Field updates


# Tool-specific response schemas
class ProgressInfo(BaseModel):
    """User progress information"""
    lesson_id: int
    lesson_title: str
    completion_status: str
    score: Optional[float] = None
    time_spent_minutes: int = 0
    completed_at: Optional[datetime] = None
    quiz_attempts: int = 0
    best_quiz_score: Optional[float] = None


class UserProgressResponse(BaseModel):
    """Response for user progress retrieval"""
    user_id: UUID
    total_lessons: int
    completed_lessons: int
    in_progress_lessons: int
    average_score: float
    total_time_spent_minutes: int
    progress_details: List[ProgressInfo]
    skill_level: str
    strengths: List[str] = []
    areas_for_improvement: List[str] = []


class GeneratedLesson(BaseModel):
    """Generated lesson content"""
    title: str
    description: str
    content: str
    objectives: List[str]
    difficulty_level: str
    estimated_duration_minutes: int
    materials_needed: List[str] = []
    exercises: List[Dict[str, Any]] = []
    evaluation_criteria: List[str] = []


class QuizEvaluation(BaseModel):
    """Quiz evaluation results"""
    quiz_id: int
    user_id: UUID
    total_questions: int
    correct_answers: int
    score_percentage: float
    time_taken_minutes: int
    detailed_feedback: List[Dict[str, Any]]  # Per-question feedback
    overall_feedback: str
    areas_to_review: List[str] = []
    recommended_actions: List[str] = []


class ScheduledReminder(BaseModel):
    """Scheduled reminder information"""
    reminder_id: int
    user_id: UUID
    reminder_type: str
    message: str
    scheduled_time: datetime
    status: str = "scheduled"
    recurring: bool = False
    recurring_pattern: Optional[str] = None


class Recommendation(BaseModel):
    """Learning recommendation"""
    item_id: int
    item_type: str  # 'lesson', 'tutorial', 'exercise'
    title: str
    description: str
    difficulty_level: str
    estimated_duration_minutes: int
    relevance_score: float
    reason: str  # Why this is recommended
    prerequisites_met: bool = True


class RecommendationsResponse(BaseModel):
    """Response for recommendations"""
    user_id: UUID
    recommendations: List[Recommendation]
    recommendation_type: str
    generated_at: datetime
    reasoning: str  # Overall reasoning for recommendations


class UserProfile(BaseModel):
    """User profile information"""
    user_id: UUID
    name: str
    email: str
    skill_level: str
    learning_goals: List[str] = []
    preferred_learning_style: Optional[str] = None
    available_time_per_week: Optional[int] = None  # minutes
    progress_summary: Optional[Dict[str, Any]] = None
    preferences: Optional[Dict[str, Any]] = None
    created_at: datetime
    last_active: Optional[datetime] = None


# MCP Tool Definition
class MCPTool(BaseModel):
    """MCP tool definition"""
    name: str
    description: str
    parameters_schema: Dict[str, Any]
    returns_schema: Dict[str, Any]
    category: str = "general"
    requires_auth: bool = True
    rate_limit: Optional[int] = None  # requests per minute


class MCPServerInfo(BaseModel):
    """MCP server information"""
    name: str = "Art Buddy MCP Server"
    version: str = "1.0.0"
    description: str = "Model Context Protocol server for Art Buddy AI learning platform"
    available_tools: List[MCPTool]
    server_capabilities: List[str] = ["tools", "progress_tracking", "recommendations"]
    max_concurrent_requests: int = 10
    request_timeout_seconds: int = 30
