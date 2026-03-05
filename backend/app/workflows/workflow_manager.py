"""
Workflow Manager

High-level interface for managing Art Buddy workflows and n8n integration.
"""

from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from uuid import UUID
import logging
from sqlalchemy.orm import Session

from .event_system import EventSystem, WorkflowEvent, WorkflowEventType, event_system
from .n8n_client import N8nClient
from ..services.user_service import UserService
from ..services.progress_service import ProgressService
from ..services.reminder_service import ReminderService

logger = logging.getLogger(__name__)


class WorkflowManager:
    """Manager for Art Buddy workflows and automation"""
    
    def __init__(self, db: Session, n8n_url: str = "http://localhost:5678", n8n_api_key: Optional[str] = None, n8n_webhook_url: Optional[str] = None):
        self.db = db
        # Use a fresh EventSystem with the configured webhook base when a URL is supplied,
        # otherwise fall back to the module-level singleton (which reads settings at import).
        if n8n_webhook_url:
            from .event_system import EventSystem as _EventSystem
            self.event_system = _EventSystem(webhook_base_url=n8n_webhook_url)
        else:
            self.event_system = event_system
        self.n8n_client = N8nClient(n8n_url, api_key=n8n_api_key)
        
        # Initialize services
        self.user_service = UserService(db)
        self.progress_service = ProgressService(db)
        self.reminder_service = ReminderService(db)
    
    async def initialize(self) -> bool:
        """Initialize workflow manager and check n8n connectivity"""
        
        try:
            # Check n8n connectivity
            is_healthy = await self.n8n_client.health_check()
            
            if not is_healthy:
                logger.warning("n8n instance not available - workflows will run in mock mode")
                return False
            
            # Get workflow status
            workflows = await self.n8n_client.get_workflows()
            logger.info(f"Connected to n8n with {len(workflows)} workflows available")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize workflow manager: {str(e)}")
            return False
    
    # Event emission methods for different scenarios
    
    async def handle_user_registration(self, user_id: UUID, user_data: Dict[str, Any]) -> bool:
        """Handle new user registration workflow"""
        
        event = WorkflowEvent(
            event_type=WorkflowEventType.USER_REGISTERED,
            user_id=user_id,
            data={
                "user_name": user_data.get("name"),
                "email": user_data.get("email"),
                "skill_level": user_data.get("skill_level", "beginner"),
                "registration_timestamp": datetime.utcnow().isoformat()
            },
            metadata={"source": "user_registration"}
        )
        
        return await self.event_system.emit_event(event)
    
    async def handle_lesson_completion(self, user_id: UUID, lesson_id: int, completion_data: Dict[str, Any], user_email: Optional[str] = None, user_name: Optional[str] = None) -> bool:
        """Handle lesson completion workflow"""
        
        # Get user details and progress
        if user_email is None or user_name is None:
            user = self.user_service.get_user(user_id)
            user_email = user_email or (user.email if user else None)
            user_name = user_name or (user.name if user else "Art Buddy User")
        try:
            progress_summary = self.progress_service.get_user_stats(user_id)
        except Exception:
            progress_summary = {}
        
        event_type = WorkflowEventType.LESSON_COMPLETED
        
        # Check if this is a milestone (every 5 lessons)
        completed = progress_summary.get("completed_lessons", 0)
        if completed > 0 and completed % 5 == 0:
            event_type = WorkflowEventType.PROGRESS_MILESTONE
        
        event = WorkflowEvent(
            event_type=event_type,
            user_id=user_id,
            data={
                "user_email": user_email,
                "user_name": user_name,
                "lesson_id": lesson_id,
                "completion_status": completion_data.get("completion_status"),
                "score": completion_data.get("score"),
                "time_spent_minutes": completion_data.get("time_spent_minutes"),
                "total_completed_lessons": progress_summary.get("completed_lessons", 0),
                "skill_level": progress_summary.get("skill_level", "beginner")
            },
            metadata={"source": "lesson_completion"}
        )
        
        return await self.event_system.emit_event(event)
    
    async def handle_quiz_completion(self, user_id: UUID, quiz_id: int, quiz_results: Dict[str, Any], user_email: Optional[str] = None, user_name: Optional[str] = None) -> bool:
        """Handle quiz completion workflow"""
        
        if user_email is None or user_name is None:
            user = self.user_service.get_user(user_id)
            user_email = user_email or (user.email if user else None)
            user_name = user_name or (user.name if user else "Art Buddy User")
        score = quiz_results.get("score_percentage", 0)
        
        # Determine event type based on performance
        if score < 60:  # Low performance threshold
            event_type = WorkflowEventType.QUIZ_FAILED
        else:
            event_type = WorkflowEventType.QUIZ_COMPLETED
        
        event = WorkflowEvent(
            event_type=event_type,
            user_id=user_id,
            data={
                "user_email": user_email,
                "user_name": user_name,
                "quiz_id": quiz_id,
                "score": score,
                "total_questions": quiz_results.get("total_questions"),
                "correct_answers": quiz_results.get("correct_answers"),
                "time_taken_minutes": quiz_results.get("time_taken_minutes"),
                "areas_to_review": quiz_results.get("areas_to_review", []),
                "performance_level": "low" if score < 60 else "good" if score < 80 else "excellent"
            },
            metadata={"source": "quiz_completion"}
        )
        
        return await self.event_system.emit_event(event)
    
    async def handle_low_performance_detection(self, user_id: UUID, performance_data: Dict[str, Any], user_email: Optional[str] = None, user_name: Optional[str] = None) -> bool:
        """Handle low performance detection workflow"""
        
        if user_email is None or user_name is None:
            user = self.user_service.get_user(user_id)
            user_email = user_email or (user.email if user else None)
            user_name = user_name or (user.name if user else "Art Buddy User")
        
        event = WorkflowEvent(
            event_type=WorkflowEventType.LOW_PERFORMANCE_DETECTED,
            user_id=user_id,
            data={
                "user_email": user_email,
                "user_name": user_name,
                "average_score": performance_data.get("average_score"),
                "recent_scores": performance_data.get("recent_scores", []),
                "struggling_areas": performance_data.get("struggling_areas", []),
                "recommendation": "review_fundamentals",
                "intervention_level": "moderate"
            },
            metadata={"source": "performance_monitoring"}
        )
        
        return await self.event_system.emit_event(event)
    
    async def handle_daily_practice_reminder(self, user_id: UUID, user_email: Optional[str] = None, user_name: Optional[str] = None) -> bool:
        """Handle daily practice reminder workflow"""
        
        # Get user details and progress
        if user_email is None or user_name is None:
            user = self.user_service.get_user(user_id)
            user_email = user_email or (user.email if user else None)
            user_name = user_name or (user.name if user else "Art Buddy User")
        try:
            user_progress = self.progress_service.get_user_stats(user_id)
        except Exception:
            user_progress = {}
        
        event = WorkflowEvent(
            event_type=WorkflowEventType.DAILY_PRACTICE_DUE,
            user_id=user_id,
            data={
                "user_email": user_email,
                "user_name": user_name,
                "practice_streak": 0,
                "total_lessons": 0,
                "completed_lessons": user_progress.get("completed_lessons", 0),
                "suggested_duration": 30,  # minutes
                "recommended_activities": ["drawing_practice", "technique_review"]
            },
            metadata={"source": "daily_scheduler"}
        )
        
        return await self.event_system.emit_event(event)
    
    async def handle_weekly_summary_generation(self, user_id: UUID, user_email: Optional[str] = None, user_name: Optional[str] = None) -> bool:
        """Handle weekly progress summary workflow"""
        
        # Get user details and weekly progress data
        if user_email is None or user_name is None:
            user = self.user_service.get_user(user_id)
            user_email = user_email or (user.email if user else None)
            user_name = user_name or (user.name if user else "Art Buddy User")
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=7)
        try:
            stats = self.progress_service.get_user_stats(user_id)
        except Exception:
            stats = {}
        
        event = WorkflowEvent(
            event_type=WorkflowEventType.WEEKLY_SUMMARY_DUE,
            user_id=user_id,
            data={
                "user_email": user_email,
                "user_name": user_name,
                "week_start": start_date.isoformat(),
                "week_end": end_date.isoformat(),
                "lessons_completed": stats.get("completed_lessons", 0),
                "total_practice_time": 0,
                "average_score": stats.get("average_score", 0),
                "achievements": [],
                "goals_met": [],
                "next_week_recommendations": []
            },
            metadata={"source": "weekly_scheduler"}
        )
        
        return await self.event_system.emit_event(event)
    
    async def handle_user_inactivity(self, user_id: UUID, inactivity_days: int, user_email: Optional[str] = None, user_name: Optional[str] = None) -> bool:
        """Handle user inactivity workflow"""
        
        if user_email is None or user_name is None:
            user = self.user_service.get_user(user_id)
            user_email = user_email or (user.email if user else None)
            user_name = user_name or (user.name if user else "Art Buddy User")
        
        event = WorkflowEvent(
            event_type=WorkflowEventType.USER_INACTIVE,
            user_id=user_id,
            data={
                "user_email": user_email,
                "user_name": user_name,
                "inactivity_days": inactivity_days,
                "last_activity": (datetime.utcnow() - timedelta(days=inactivity_days)).isoformat(),
                "engagement_level": "low" if inactivity_days > 7 else "moderate",
                "suggested_actions": ["motivational_message", "easy_lesson_recommendation"]
            },
            metadata={"source": "engagement_monitor"}
        )
        
        return await self.event_system.emit_event(event)
    
    async def handle_streak_achievement(self, user_id: UUID, streak_data: Dict[str, Any], user_email: Optional[str] = None, user_name: Optional[str] = None) -> bool:
        """Handle learning streak achievement workflow"""
        
        if user_email is None or user_name is None:
            user = self.user_service.get_user(user_id)
            user_email = user_email or (user.email if user else None)
            user_name = user_name or (user.name if user else "Art Buddy User")
        
        event = WorkflowEvent(
            event_type=WorkflowEventType.STREAK_ACHIEVED,
            user_id=user_id,
            data={
                "user_email": user_email,
                "user_name": user_name,
                "streak_type": streak_data.get("type", "daily_practice"),
                "streak_length": streak_data.get("length"),
                "achievement_level": streak_data.get("level", "bronze"),
                "celebration_type": "badge" if streak_data.get("length", 0) < 10 else "certificate"
            },
            metadata={"source": "streak_tracker"}
        )
        
        return await self.event_system.emit_event(event)
    
    # Management and monitoring methods
    
    async def get_workflow_status(self) -> Dict[str, Any]:
        """Get overall workflow system status"""
        
        try:
            # Get n8n status
            n8n_info = await self.n8n_client.get_server_info()
            
            # Get event system status
            triggers = self.event_system.get_triggers()
            queue_size = self.event_system.get_event_queue_size()
            
            # Get workflow statistics
            workflows = await self.n8n_client.get_workflows()
            
            return {
                "n8n_status": n8n_info,
                "event_system": {
                    "active_triggers": len([t for t in triggers if t.is_active]),
                    "total_triggers": len(triggers),
                    "queue_size": queue_size,
                    "processing": self.event_system.processing_events
                },
                "workflows": {
                    "total_count": len(workflows),
                    "active_count": len([w for w in workflows if w.get('active', False)])
                },
                "last_updated": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting workflow status: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "last_updated": datetime.utcnow().isoformat()
            }
    
    async def get_workflow_analytics(self, days: int = 7) -> Dict[str, Any]:
        """Get workflow execution analytics"""
        
        try:
            # Get recent executions
            executions = await self.n8n_client.get_executions(limit=100)
            
            # Filter by date range
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            recent_executions = [
                exec for exec in executions 
                if exec.started_at >= cutoff_date
            ]
            
            # Calculate statistics
            total_executions = len(recent_executions)
            successful_executions = len([e for e in recent_executions if e.status == 'success'])
            failed_executions = len([e for e in recent_executions if e.status == 'error'])
            
            success_rate = (successful_executions / total_executions * 100) if total_executions > 0 else 0
            
            return {
                "period_days": days,
                "total_executions": total_executions,
                "successful_executions": successful_executions,
                "failed_executions": failed_executions,
                "success_rate": round(success_rate, 2),
                "average_execution_time_ms": sum(
                    e.execution_time_ms for e in recent_executions 
                    if e.execution_time_ms
                ) / len(recent_executions) if recent_executions else 0,
                "most_active_workflows": self._get_most_active_workflows(recent_executions)
            }
            
        except Exception as e:
            logger.error(f"Error getting workflow analytics: {str(e)}")
            return {"error": str(e)}
    
    def _get_most_active_workflows(self, executions) -> List[Dict[str, Any]]:
        """Get most active workflows from execution data"""
        
        workflow_counts = {}
        for execution in executions:
            workflow_id = execution.workflow_id
            if workflow_id not in workflow_counts:
                workflow_counts[workflow_id] = 0
            workflow_counts[workflow_id] += 1
        
        # Sort by execution count
        sorted_workflows = sorted(
            workflow_counts.items(), 
            key=lambda x: x[1], 
            reverse=True
        )
        
        return [
            {"workflow_id": wf_id, "execution_count": count}
            for wf_id, count in sorted_workflows[:5]  # Top 5
        ]
