"""
MCP Tool Registry

Manages registration, discovery, and validation of MCP tools.
"""

from typing import Dict, List, Any, Optional, Callable
from .schemas import (
    MCPTool, ToolType, MCPRequest, MCPResponse,
    GetUserProgressRequest, UpdateProgressRequest, GenerateLessonRequest,
    EvaluateQuizRequest, ScheduleReminderRequest, FetchRecommendationsRequest,
    GetUserProfileRequest, UpdateUserProfileRequest
)
import json
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class ToolRegistry:
    """Registry for MCP tools with validation and execution management"""
    
    def __init__(self):
        self._tools: Dict[str, MCPTool] = {}
        self._handlers: Dict[str, Callable] = {}
        self._tool_stats: Dict[str, Dict[str, Any]] = {}
        self._register_default_tools()
    
    def _register_default_tools(self):
        """Register default Art Buddy MCP tools"""
        
        # Get User Progress Tool
        self.register_tool(
            name=ToolType.GET_USER_PROGRESS,
            description="Retrieve comprehensive user learning progress including lessons, scores, and time spent",
            parameters_schema={
                "type": "object",
                "properties": {
                    "user_id": {"type": "string", "format": "uuid"},
                    "lesson_ids": {
                        "type": "array",
                        "items": {"type": "integer"},
                        "description": "Specific lesson IDs to retrieve, or all if omitted"
                    },
                    "include_quiz_scores": {"type": "boolean", "default": True},
                    "include_time_spent": {"type": "boolean", "default": True}
                },
                "required": ["user_id"]
            },
            returns_schema={
                "type": "object",
                "properties": {
                    "user_id": {"type": "string"},
                    "total_lessons": {"type": "integer"},
                    "completed_lessons": {"type": "integer"},
                    "average_score": {"type": "number"},
                    "progress_details": {"type": "array"}
                }
            },
            category="progress"
        )
        
        # Update Progress Tool
        self.register_tool(
            name=ToolType.UPDATE_PROGRESS,
            description="Update user progress for a specific lesson with completion status and score",
            parameters_schema={
                "type": "object",
                "properties": {
                    "user_id": {"type": "string", "format": "uuid"},
                    "lesson_id": {"type": "integer"},
                    "completion_status": {
                        "type": "string",
                        "enum": ["started", "in_progress", "completed"]
                    },
                    "score": {"type": "number", "minimum": 0, "maximum": 100},
                    "time_spent_minutes": {"type": "integer", "minimum": 0},
                    "notes": {"type": "string"}
                },
                "required": ["user_id", "lesson_id", "completion_status"]
            },
            returns_schema={
                "type": "object",
                "properties": {
                    "updated": {"type": "boolean"},
                    "progress_id": {"type": "integer"},
                    "new_skill_level": {"type": "string"}
                }
            },
            category="progress"
        )
        
        # Generate Lesson Tool
        self.register_tool(
            name=ToolType.GENERATE_LESSON,
            description="Generate personalized lesson content based on user skill level and topic",
            parameters_schema={
                "type": "object",
                "properties": {
                    "user_id": {"type": "string", "format": "uuid"},
                    "topic": {"type": "string", "description": "Art topic or technique to cover"},
                    "difficulty_level": {
                        "type": "string",
                        "enum": ["beginner", "intermediate", "advanced"]
                    },
                    "lesson_type": {
                        "type": "string",
                        "enum": ["theory", "practical", "mixed"],
                        "default": "theory"
                    },
                    "duration_minutes": {"type": "integer", "minimum": 10, "maximum": 180},
                    "prerequisites": {
                        "type": "array",
                        "items": {"type": "string"}
                    }
                },
                "required": ["user_id", "topic", "difficulty_level"]
            },
            returns_schema={
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "content": {"type": "string"},
                    "objectives": {"type": "array"},
                    "exercises": {"type": "array"}
                }
            },
            category="content"
        )
        
        # Evaluate Quiz Tool
        self.register_tool(
            name=ToolType.EVALUATE_QUIZ,
            description="Evaluate user quiz answers and provide detailed feedback",
            parameters_schema={
                "type": "object",
                "properties": {
                    "user_id": {"type": "string", "format": "uuid"},
                    "quiz_id": {"type": "integer"},
                    "answers": {
                        "type": "object",
                        "description": "Question ID to answer mapping"
                    },
                    "time_taken_minutes": {"type": "integer", "minimum": 0}
                },
                "required": ["user_id", "quiz_id", "answers"]
            },
            returns_schema={
                "type": "object",
                "properties": {
                    "score_percentage": {"type": "number"},
                    "correct_answers": {"type": "integer"},
                    "detailed_feedback": {"type": "array"},
                    "areas_to_review": {"type": "array"}
                }
            },
            category="assessment"
        )
        
        # Schedule Reminder Tool
        self.register_tool(
            name=ToolType.SCHEDULE_REMINDER,
            description="Schedule practice reminders and learning notifications for users",
            parameters_schema={
                "type": "object",
                "properties": {
                    "user_id": {"type": "string", "format": "uuid"},
                    "reminder_type": {
                        "type": "string",
                        "enum": ["practice", "lesson", "quiz", "general"]
                    },
                    "schedule_time": {"type": "string", "format": "date-time"},
                    "message": {"type": "string"},
                    "recurring": {"type": "boolean", "default": False},
                    "recurring_pattern": {
                        "type": "string",
                        "enum": ["daily", "weekly", "monthly"]
                    }
                },
                "required": ["user_id", "reminder_type", "schedule_time", "message"]
            },
            returns_schema={
                "type": "object",
                "properties": {
                    "reminder_id": {"type": "integer"},
                    "scheduled": {"type": "boolean"},
                    "next_occurrence": {"type": "string", "format": "date-time"}
                }
            },
            category="engagement"
        )
        
        # Fetch Recommendations Tool
        self.register_tool(
            name=ToolType.FETCH_RECOMMENDATIONS,
            description="Get personalized learning recommendations based on user progress and preferences",
            parameters_schema={
                "type": "object",
                "properties": {
                    "user_id": {"type": "string", "format": "uuid"},
                    "recommendation_type": {
                        "type": "string",
                        "enum": ["lessons", "tutorials", "exercises"],
                        "default": "lessons"
                    },
                    "limit": {"type": "integer", "minimum": 1, "maximum": 20, "default": 5},
                    "include_completed": {"type": "boolean", "default": False},
                    "skill_areas": {
                        "type": "array",
                        "items": {"type": "string"}
                    }
                },
                "required": ["user_id"]
            },
            returns_schema={
                "type": "object",
                "properties": {
                    "recommendations": {"type": "array"},
                    "reasoning": {"type": "string"},
                    "generated_at": {"type": "string", "format": "date-time"}
                }
            },
            category="recommendations"
        )
        
        # Get User Profile Tool
        self.register_tool(
            name=ToolType.GET_USER_PROFILE,
            description="Retrieve comprehensive user profile including preferences and progress summary",
            parameters_schema={
                "type": "object",
                "properties": {
                    "user_id": {"type": "string", "format": "uuid"},
                    "include_progress_summary": {"type": "boolean", "default": True},
                    "include_preferences": {"type": "boolean", "default": True}
                },
                "required": ["user_id"]
            },
            returns_schema={
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "skill_level": {"type": "string"},
                    "learning_goals": {"type": "array"},
                    "progress_summary": {"type": "object"}
                }
            },
            category="profile"
        )
        
        # Update User Profile Tool
        self.register_tool(
            name=ToolType.UPDATE_USER_PROFILE,
            description="Update user profile information and preferences",
            parameters_schema={
                "type": "object",
                "properties": {
                    "user_id": {"type": "string", "format": "uuid"},
                    "updates": {
                        "type": "object",
                        "description": "Fields to update in the user profile"
                    }
                },
                "required": ["user_id", "updates"]
            },
            returns_schema={
                "type": "object",
                "properties": {
                    "updated": {"type": "boolean"},
                    "updated_fields": {"type": "array"},
                    "profile": {"type": "object"}
                }
            },
            category="profile"
        )
        
        logger.info(f"Registered {len(self._tools)} default MCP tools")
    
    def register_tool(
        self,
        name: str,
        description: str,
        parameters_schema: Dict[str, Any],
        returns_schema: Dict[str, Any],
        category: str = "general",
        requires_auth: bool = True,
        rate_limit: Optional[int] = None,
        handler: Optional[Callable] = None
    ) -> None:
        """Register a new MCP tool"""
        
        tool = MCPTool(
            name=name,
            description=description,
            parameters_schema=parameters_schema,
            returns_schema=returns_schema,
            category=category,
            requires_auth=requires_auth,
            rate_limit=rate_limit
        )
        
        self._tools[name] = tool
        
        if handler:
            self._handlers[name] = handler
        
        # Initialize tool statistics
        self._tool_stats[name] = {
            "total_calls": 0,
            "successful_calls": 0,
            "failed_calls": 0,
            "average_execution_time_ms": 0.0,
            "last_used": None
        }
        
        logger.debug(f"Registered MCP tool: {name}")
    
    def get_tool(self, name: str) -> Optional[MCPTool]:
        """Get tool by name"""
        return self._tools.get(name)
    
    def list_tools(self, category: Optional[str] = None) -> List[MCPTool]:
        """List all tools, optionally filtered by category"""
        tools = list(self._tools.values())
        
        if category:
            tools = [tool for tool in tools if tool.category == category]
        
        return tools
    
    def validate_request(self, request: MCPRequest) -> tuple[bool, Optional[str]]:
        """Validate MCP request against tool schema"""
        
        tool = self.get_tool(request.tool_name)
        if not tool:
            return False, f"Unknown tool: {request.tool_name}"
        
        # Basic parameter validation would go here
        # For now, we'll do simple type checking
        
        try:
            # Validate required parameters exist
            schema = tool.parameters_schema
            if "required" in schema:
                for required_param in schema["required"]:
                    if required_param not in request.parameters:
                        return False, f"Missing required parameter: {required_param}"
            
            return True, None
        except Exception as e:
            return False, f"Validation error: {str(e)}"
    
    def record_tool_usage(self, tool_name: str, success: bool, execution_time_ms: float):
        """Record tool usage statistics"""
        
        if tool_name not in self._tool_stats:
            return
        
        stats = self._tool_stats[tool_name]
        stats["total_calls"] += 1
        stats["last_used"] = datetime.utcnow().isoformat()
        
        if success:
            stats["successful_calls"] += 1
        else:
            stats["failed_calls"] += 1
        
        # Update average execution time
        current_avg = stats["average_execution_time_ms"]
        total_calls = stats["total_calls"]
        stats["average_execution_time_ms"] = (
            (current_avg * (total_calls - 1) + execution_time_ms) / total_calls
        )
    
    def get_tool_stats(self, tool_name: Optional[str] = None) -> Dict[str, Any]:
        """Get tool usage statistics"""
        
        if tool_name:
            return self._tool_stats.get(tool_name, {})
        
        return dict(self._tool_stats)
    
    def get_categories(self) -> List[str]:
        """Get list of all tool categories"""
        categories = set(tool.category for tool in self._tools.values())
        return sorted(list(categories))
    
    def export_tool_definitions(self) -> Dict[str, Any]:
        """Export all tool definitions for external use"""
        
        return {
            "tools": {
                name: {
                    "description": tool.description,
                    "parameters_schema": tool.parameters_schema,
                    "returns_schema": tool.returns_schema,
                    "category": tool.category,
                    "requires_auth": tool.requires_auth,
                    "rate_limit": tool.rate_limit
                }
                for name, tool in self._tools.items()
            },
            "categories": self.get_categories(),
            "total_tools": len(self._tools),
            "export_timestamp": datetime.utcnow().isoformat()
        }


# Global tool registry instance
tool_registry = ToolRegistry()
