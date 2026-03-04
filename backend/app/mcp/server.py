"""
MCP Server Implementation

Hanles Model Context Protocol tool execution and routing.
"""

from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException
import time
import logging
from datetime import datetime
from uuid import UUID

from .schemas import (
    MCPRequest, MCPResponse, ToolType,
    GetUserProgressRequest, UpdateProgressRequest, GenerateLessonRequest,
    EvaluateQuizRequest, ScheduleReminderRequest, FetchRecommendationsRequest,
    GetUserProfileRequest, UpdateUserProfileRequest,
    UserProgressResponse, GeneratedLesson, QuizEvaluation,
    ScheduledReminder, RecommendationsResponse, UserProfile
)
from .tool_registry import tool_registry
from ..services.user_service import UserService
from ..services.lesson_service import LessonService
from ..services.progress_service import ProgressService
from ..services.quiz_service import QuizService
from ..services.reminder_service import ReminderService
from ..services.recommendation_service import RecommendationService

logger = logging.getLogger(__name__)


class MCPServer:
    """Model Context Protocol server for Art Buddy"""
    
    def __init__(self, db: Session):
        self.db = db
        self.user_service = UserService(db)
        self.lesson_service = LessonService(db)
        self.progress_service = ProgressService(db)
        self.quiz_service = QuizService(db)
        self.reminder_service = ReminderService(db)
        self.recommendation_service = RecommendationService(db)
        
        # Register tool handlers
        self._register_handlers()
    
    def _register_handlers(self):
        """Register handlers for each MCP tool"""
        
        self.handlers = {
            ToolType.GET_USER_PROGRESS: self._handle_get_user_progress,
            ToolType.UPDATE_PROGRESS: self._handle_update_progress,
            ToolType.GENERATE_LESSON: self._handle_generate_lesson,
            ToolType.EVALUATE_QUIZ: self._handle_evaluate_quiz,
            ToolType.SCHEDULE_REMINDER: self._handle_schedule_reminder,
            ToolType.FETCH_RECOMMENDATIONS: self._handle_fetch_recommendations,
            ToolType.GET_USER_PROFILE: self._handle_get_user_profile,
            ToolType.UPDATE_USER_PROFILE: self._handle_update_user_profile,
        }
    
    async def execute_tool(self, request: MCPRequest) -> MCPResponse:
        """Execute an MCP tool request"""
        
        start_time = time.time()
        
        try:
            # Validate request
            is_valid, error_msg = tool_registry.validate_request(request)
            if not is_valid:
                return MCPResponse(
                    success=False,
                    error=error_msg,
                    tool_name=request.tool_name,
                    request_id=request.request_id
                )
            
            # Get handler
            handler = self.handlers.get(request.tool_name)
            if not handler:
                return MCPResponse(
                    success=False,
                    error=f"No handler for tool: {request.tool_name}",
                    tool_name=request.tool_name,
                    request_id=request.request_id
                )
            
            # Execute handler
            result = await handler(request.parameters, request.user_id)
            
            execution_time = (time.time() - start_time) * 1000
            
            # Record successful execution
            tool_registry.record_tool_usage(request.tool_name, True, execution_time)
            
            return MCPResponse(
                success=True,
                result=result,
                tool_name=request.tool_name,
                request_id=request.request_id,
                execution_time_ms=execution_time
            )
            
        except Exception as e:
            execution_time = (time.time() - start_time) * 1000
            
            logger.error(f"MCP tool execution error: {str(e)}", exc_info=True)
            
            # Record failed execution
            tool_registry.record_tool_usage(request.tool_name, False, execution_time)
            
            return MCPResponse(
                success=False,
                error=str(e),
                tool_name=request.tool_name,
                request_id=request.request_id,
                execution_time_ms=execution_time
            )
    
    async def _handle_get_user_progress(self, parameters: Dict[str, Any], user_id: Optional[UUID]) -> Dict[str, Any]:
        """Handle get user progress tool"""
        
        req = GetUserProgressRequest(**parameters)
        
        # Get user progress from service
        progress_data = await self.progress_service.get_user_progress_summary(
            user_id=req.user_id,
            lesson_ids=req.lesson_ids,
            include_quiz_scores=req.include_quiz_scores,
            include_time_spent=req.include_time_spent
        )
        
        return progress_data
    
    async def _handle_update_progress(self, parameters: Dict[str, Any], user_id: Optional[UUID]) -> Dict[str, Any]:
        """Handle update progress tool"""
        
        req = UpdateProgressRequest(**parameters)
        
        # Update progress via service
        updated_progress = await self.progress_service.update_progress(
            user_id=req.user_id,
            lesson_id=req.lesson_id,
            completion_status=req.completion_status,
            score=req.score,
            time_spent_minutes=req.time_spent_minutes,
            notes=req.notes
        )
        
        # Check for skill level updates
        user = await self.user_service.get_user(req.user_id)
        
        return {
            "updated": True,
            "progress_id": updated_progress.id,
            "new_skill_level": user.skill_level if user else None
        }
    
    async def _handle_generate_lesson(self, parameters: Dict[str, Any], user_id: Optional[UUID]) -> Dict[str, Any]:
        """Handle generate lesson tool"""
        
        req = GenerateLessonRequest(**parameters)
        
        # Generate lesson via service
        lesson = await self.lesson_service.generate_personalized_lesson(
            user_id=req.user_id,
            topic=req.topic,
            difficulty_level=req.difficulty_level,
            lesson_type=req.lesson_type,
            duration_minutes=req.duration_minutes,
            prerequisites=req.prerequisites
        )
        
        return lesson.dict() if hasattr(lesson, 'dict') else lesson
    
    async def _handle_evaluate_quiz(self, parameters: Dict[str, Any], user_id: Optional[UUID]) -> Dict[str, Any]:
        """Handle evaluate quiz tool"""
        
        req = EvaluateQuizRequest(**parameters)
        
        # Evaluate quiz via service
        evaluation = await self.quiz_service.evaluate_quiz_submission(
            user_id=req.user_id,
            quiz_id=req.quiz_id,
            answers=req.answers,
            time_taken_minutes=req.time_taken_minutes
        )
        
        return evaluation.dict() if hasattr(evaluation, 'dict') else evaluation
    
    async def _handle_schedule_reminder(self, parameters: Dict[str, Any], user_id: Optional[UUID]) -> Dict[str, Any]:
        """Handle schedule reminder tool"""
        
        req = ScheduleReminderRequest(**parameters)
        
        # Schedule reminder via service
        reminder = await self.reminder_service.schedule_reminder(
            user_id=req.user_id,
            reminder_type=req.reminder_type,
            schedule_time=req.schedule_time,
            message=req.message,
            recurring=req.recurring,
            recurring_pattern=req.recurring_pattern
        )
        
        return {
            "reminder_id": reminder.id,
            "scheduled": True,
            "next_occurrence": reminder.schedule_time.isoformat()
        }
    
    async def _handle_fetch_recommendations(self, parameters: Dict[str, Any], user_id: Optional[UUID]) -> Dict[str, Any]:
        """Handle fetch recommendations tool"""
        
        req = FetchRecommendationsRequest(**parameters)
        
        # Get recommendations via service
        recommendations = await self.recommendation_service.get_personalized_recommendations(
            user_id=req.user_id,
            recommendation_type=req.recommendation_type,
            limit=req.limit,
            include_completed=req.include_completed,
            skill_areas=req.skill_areas
        )
        
        return {
            "user_id": str(req.user_id),
            "recommendations": recommendations,
            "recommendation_type": req.recommendation_type,
            "generated_at": datetime.utcnow().isoformat(),
            "reasoning": "Generated based on user progress, skill level, and learning preferences"
        }
    
    async def _handle_get_user_profile(self, parameters: Dict[str, Any], user_id: Optional[UUID]) -> Dict[str, Any]:
        """Handle get user profile tool"""
        
        req = GetUserProfileRequest(**parameters)
        
        # Get user profile
        user = await self.user_service.get_user(req.user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        profile_data = {
            "user_id": str(user.id),
            "name": user.name,
            "email": user.email,
            "skill_level": user.skill_level,
            "learning_goals": user.learning_goals or [],
            "created_at": user.created_at.isoformat(),
            "last_active": user.last_login.isoformat() if user.last_login else None
        }
        
        # Add progress summary if requested
        if req.include_progress_summary:
            progress_summary = await self.progress_service.get_user_progress_summary(req.user_id)
            profile_data["progress_summary"] = progress_summary
        
        # Add preferences if requested
        if req.include_preferences:
            profile_data["preferences"] = {
                "preferred_learning_style": getattr(user, 'preferred_learning_style', None),
                "available_time_per_week": getattr(user, 'available_time_per_week', None),
                "notification_preferences": getattr(user, 'notification_preferences', {})
            }
        
        return profile_data
    
    async def _handle_update_user_profile(self, parameters: Dict[str, Any], user_id: Optional[UUID]) -> Dict[str, Any]:
        """Handle update user profile tool"""
        
        req = UpdateUserProfileRequest(**parameters)
        
        # Update user profile
        updated_user = await self.user_service.update_user(req.user_id, req.updates)
        
        return {
            "updated": True,
            "updated_fields": list(req.updates.keys()),
            "profile": {
                "user_id": str(updated_user.id),
                "name": updated_user.name,
                "email": updated_user.email,
                "skill_level": updated_user.skill_level
            }
        }
    
    def get_server_info(self) -> Dict[str, Any]:
        """Get MCP server information"""
        
        return {
            "name": "Art Buddy MCP Server",
            "version": "1.0.0",
            "description": "Model Context Protocol server for Art Buddy AI learning platform",
            "available_tools": len(tool_registry._tools),
            "tool_categories": tool_registry.get_categories(),
            "server_capabilities": ["tools", "progress_tracking", "recommendations"],
            "total_tool_calls": sum(stats["total_calls"] for stats in tool_registry._tool_stats.values()),
            "server_uptime": "Active",
            "supported_features": [
                "User progress tracking",
                "Personalized lesson generation",
                "Quiz evaluation with feedback",
                "Reminder scheduling",
                "AI-powered recommendations",
                "Profile management"
            ]
        }
    
    def get_tool_list(self) -> Dict[str, Any]:
        """Get list of available tools"""
        
        return tool_registry.export_tool_definitions()
