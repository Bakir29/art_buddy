from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import UUID


# User Schemas
class UserBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    email: EmailStr
    skill_level: str = Field(default="beginner", pattern="^(beginner|intermediate|advanced)$")


class UserCreate(UserBase):
    password: str = Field(..., min_length=8)


class UserUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    skill_level: Optional[str] = Field(None, pattern="^(beginner|intermediate|advanced)$")


class User(UserBase):
    id: UUID
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Lesson Schemas
class LessonBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    content: str
    difficulty: str = Field(..., pattern="^(beginner|intermediate|advanced)$")
    category: str = Field(default="general")
    order_in_category: int = Field(default=1, ge=1)
    lesson_type: str = Field(default="tutorial", pattern="^(tutorial|exercise|quiz)$")
    duration_minutes: int = Field(default=30, ge=1)
    prerequisites: List[UUID] = Field(default_factory=list)


class LessonCreate(LessonBase):
    pass


class LessonUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    content: Optional[str] = None
    difficulty: Optional[str] = Field(None, pattern="^(beginner|intermediate|advanced)$")
    category: Optional[str] = None
    order_in_category: Optional[int] = Field(None, ge=1)
    lesson_type: Optional[str] = Field(None, pattern="^(tutorial|exercise|quiz)$")
    duration_minutes: Optional[int] = Field(None, ge=1)
    prerequisites: Optional[List[UUID]] = None
    is_active: Optional[bool] = None


class Lesson(LessonBase):
    id: UUID
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Progress Schemas
class ProgressBase(BaseModel):
    completion_status: str = Field(default="not_started", pattern="^(not_started|in_progress|completed)$")
    score: Optional[float] = Field(None, ge=0.0, le=100.0)
    time_spent_minutes: int = Field(default=0, ge=0)


class ProgressCreate(ProgressBase):
    user_id: UUID
    lesson_id: UUID


class ProgressUpdate(BaseModel):
    completion_status: Optional[str] = Field(None, pattern="^(not_started|in_progress|completed)$")
    score: Optional[float] = Field(None, ge=0.0, le=100.0)
    time_spent_minutes: Optional[int] = Field(None, ge=0)


class Progress(ProgressBase):
    id: UUID
    user_id: UUID
    lesson_id: UUID
    attempts: int
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Quiz Schemas
class QuizQuestionBase(BaseModel):
    question_text: str
    question_type: str = Field(..., pattern="^(multiple_choice|true_false|short_answer)$")
    options: Optional[List[str]] = None
    correct_answer: str
    explanation: Optional[str] = None
    points: int = Field(default=1, ge=1)


class QuizQuestionCreate(QuizQuestionBase):
    lesson_id: UUID


class QuizQuestion(QuizQuestionBase):
    id: UUID
    lesson_id: UUID
    created_at: datetime
    
    class Config:
        from_attributes = True


class QuizResponseCreate(BaseModel):
    question_id: UUID
    user_answer: str


class QuizResponse(BaseModel):
    id: UUID
    user_id: UUID
    question_id: UUID
    user_answer: str
    is_correct: bool
    points_earned: int
    answered_at: datetime
    
    class Config:
        from_attributes = True


# Reminder Schemas
class ReminderBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    message: Optional[str] = None
    reminder_type: str = Field(..., pattern="^(daily_practice|lesson_reminder|achievement)$")
    schedule_time: datetime


class ReminderCreate(ReminderBase):
    user_id: UUID


class ReminderUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    message: Optional[str] = None
    reminder_type: Optional[str] = Field(None, pattern="^(daily_practice|lesson_reminder|achievement)$")
    schedule_time: Optional[datetime] = None
    is_active: Optional[bool] = None


class Reminder(ReminderBase):
    id: UUID
    user_id: UUID
    is_sent: bool
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


# Knowledge Chunk Schemas
class KnowledgeChunkCreate(BaseModel):
    content: str
    source: Optional[str] = None
    chunk_index: int = Field(..., ge=0)
    chunk_metadata: Dict[str, Any] = Field(default_factory=dict)


class KnowledgeChunk(BaseModel):
    id: UUID
    content: str
    source: Optional[str] = None
    chunk_index: int
    chunk_metadata: Dict[str, Any]
    created_at: datetime
    
    class Config:
        from_attributes = True


# Authentication Schemas
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: Optional[str] = None


# AI/RAG Schemas
class AIQuestionRequest(BaseModel):
    question: str = Field(..., min_length=1)
    user_id: UUID
    include_context: bool = Field(default=True)


class AIResponse(BaseModel):
    answer: str
    sources: List[str] = Field(default_factory=list)
    confidence: float = Field(..., ge=0.0, le=1.0)


# Recommendation Schemas
class RecommendationRequest(BaseModel):
    user_id: UUID
    limit: int = Field(default=5, ge=1, le=20)


class LessonRecommendation(BaseModel):
    lesson: Lesson
    reason: str
    priority: int = Field(..., ge=1, le=10)


class RecommendationResponse(BaseModel):
    recommendations: List[LessonRecommendation]
    total_count: int
