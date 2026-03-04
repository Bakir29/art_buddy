from sqlalchemy import Column, Integer, String, DateTime, Text, Float, Boolean, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base, UUID
from pgvector.sqlalchemy import Vector
import uuid


class User(Base):
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    skill_level = Column(String(50), default="beginner")  # beginner, intermediate, advanced
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    progress_records = relationship("Progress", back_populates="user")
    reminders = relationship("Reminder", back_populates="user")


class Lesson(Base):
    __tablename__ = "lessons"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    difficulty = Column(String(50), nullable=False)  # beginner, intermediate, advanced
    category = Column(String(100), default="general")  # drawing, painting, color_theory, digital_art, design, character_art, sculpture
    order_in_category = Column(Integer, default=0)  # Order within category (lower = easier)
    lesson_type = Column(String(50), default="tutorial")  # tutorial, exercise, quiz
    duration_minutes = Column(Integer, default=30)
    prerequisites = Column(JSON, default=list)  # List of lesson IDs
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    progress_records = relationship("Progress", back_populates="lesson")
    quiz_questions = relationship("QuizQuestion", back_populates="lesson")


class Progress(Base):
    __tablename__ = "progress"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    lesson_id = Column(UUID(as_uuid=True), ForeignKey("lessons.id"), nullable=False)
    completion_status = Column(String(50), default="not_started")  # not_started, in_progress, completed
    score = Column(Float, nullable=True)  # 0.0 to 100.0
    time_spent_minutes = Column(Integer, default=0)
    attempts = Column(Integer, default=0)
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="progress_records")
    lesson = relationship("Lesson", back_populates="progress_records")


class QuizQuestion(Base):
    __tablename__ = "quiz_questions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    lesson_id = Column(UUID(as_uuid=True), ForeignKey("lessons.id"), nullable=False)
    question_text = Column(Text, nullable=False)
    question_type = Column(String(50), nullable=False)  # multiple_choice, true_false, short_answer
    options = Column(JSON, nullable=True)  # For multiple choice questions
    correct_answer = Column(Text, nullable=False)
    explanation = Column(Text, nullable=True)
    points = Column(Integer, default=1)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    lesson = relationship("Lesson", back_populates="quiz_questions")
    quiz_responses = relationship("QuizResponse", back_populates="question")


class QuizResponse(Base):
    __tablename__ = "quiz_responses"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    question_id = Column(UUID(as_uuid=True), ForeignKey("quiz_questions.id"), nullable=False)
    user_answer = Column(Text, nullable=False)
    is_correct = Column(Boolean, nullable=False)
    points_earned = Column(Integer, default=0)
    answered_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    question = relationship("QuizQuestion", back_populates="quiz_responses")


class Reminder(Base):
    __tablename__ = "reminders"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=True)
    reminder_type = Column(String(50), nullable=False)  # daily_practice, lesson_reminder, achievement
    schedule_time = Column(DateTime(timezone=True), nullable=False)
    is_sent = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="reminders")


class KnowledgeChunk(Base):
    __tablename__ = "knowledge_chunks"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    content = Column(Text, nullable=False)
    source = Column(String(255), nullable=True)  # File path, URL, or other source identifier
    chunk_index = Column(Integer, nullable=False)  # Order within the source
    chunk_metadata = Column(JSON, default=dict)  # Additional metadata about the chunk
    embedding = Column(Vector(1536))  # OpenAI ada-002 embedding dimension
    created_at = Column(DateTime(timezone=True), server_default=func.now())

# Import image analysis model to include in metadata
# from app.repositories.image_analysis_repository import ImageAnalysisModel
