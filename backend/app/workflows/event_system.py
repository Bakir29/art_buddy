"""
Event System for n8n Workflow Integration

Handles event emission and routing to n8n workflows.
"""

from typing import Dict, Any, Optional, List
from enum import Enum
from pydantic import BaseModel, Field
from datetime import datetime
from uuid import UUID, uuid4
import httpx
import logging
import asyncio
from ..config import settings

logger = logging.getLogger(__name__)


class WorkflowEventType(str, Enum):
    """Types of workflow events that can trigger n8n workflows"""
    USER_REGISTERED = "user.registered"
    LESSON_COMPLETED = "lesson.completed"
    LESSON_STARTED = "lesson.started"
    QUIZ_COMPLETED = "quiz.completed"
    QUIZ_FAILED = "quiz.failed"
    PROGRESS_MILESTONE = "progress.milestone"
    DAILY_PRACTICE_DUE = "practice.daily_due"
    WEEKLY_SUMMARY_DUE = "summary.weekly_due"
    LOW_PERFORMANCE_DETECTED = "performance.low_detected"
    STREAK_ACHIEVED = "streak.achieved"
    GOAL_COMPLETED = "goal.completed"
    REMINDER_SCHEDULED = "reminder.scheduled"
    USER_INACTIVE = "user.inactive"


class WorkflowEvent(BaseModel):
    """Workflow event data structure"""
    event_id: str = Field(default_factory=lambda: str(uuid4()))
    event_type: WorkflowEventType
    user_id: Optional[UUID] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    data: Dict[str, Any] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    retry_count: int = 0
    max_retries: int = 3
    
    class Config:
        use_enum_values = True


class WorkflowTrigger(BaseModel):
    """Workflow trigger configuration"""
    name: str
    event_types: List[WorkflowEventType]
    webhook_url: str
    is_active: bool = True
    conditions: Dict[str, Any] = Field(default_factory=dict)
    timeout_seconds: int = 8   # short timeout — avoids blocking the server request
    description: Optional[str] = None


class EventSystem:
    """Event system for triggering n8n workflows"""
    
    def __init__(self, webhook_base_url: Optional[str] = None):
        self.triggers: Dict[str, WorkflowTrigger] = {}
        self.event_queue: List[WorkflowEvent] = []
        self.processing_events = False
        # Use provided base URL, fall back to settings, then localhost
        self.webhook_base = (webhook_base_url or settings.n8n_webhook_url or "http://localhost:5678/webhook").rstrip('/')
        self._register_default_triggers()
    
    def _register_default_triggers(self):
        """Register default workflow triggers using configured n8n webhook base URL"""
        base = self.webhook_base

        # Daily Practice Reminder Workflow
        self.register_trigger(
            WorkflowTrigger(
                name="daily_practice_reminder",
                event_types=[WorkflowEventType.DAILY_PRACTICE_DUE],
                webhook_url=f"{base}/daily-practice",
                description="Sends daily practice reminders to users"
            )
        )
        
        # Low Performance Intervention Workflow
        self.register_trigger(
            WorkflowTrigger(
                name="low_performance_intervention",
                event_types=[
                    WorkflowEventType.QUIZ_FAILED,
                    WorkflowEventType.LOW_PERFORMANCE_DETECTED
                ],
                webhook_url=f"{base}/low-performance",
                conditions={"min_score_threshold": 60},
                description="Triggers intervention for low performance"
            )
        )
        
        # Weekly Progress Summary Workflow
        self.register_trigger(
            WorkflowTrigger(
                name="weekly_progress_summary",
                event_types=[WorkflowEventType.WEEKLY_SUMMARY_DUE],
                webhook_url=f"{base}/weekly-summary",
                description="Generates and sends weekly progress reports"
            )
        )
        
        # Lesson Completion Workflow
        self.register_trigger(
            WorkflowTrigger(
                name="lesson_completion_handler",
                event_types=[
                    WorkflowEventType.LESSON_COMPLETED,
                    WorkflowEventType.PROGRESS_MILESTONE
                ],
                webhook_url=f"{base}/lesson-complete",
                description="Handles lesson completion rewards and next steps"
            )
        )
        
        # User Engagement Workflow
        self.register_trigger(
            WorkflowTrigger(
                name="user_engagement_tracker",
                event_types=[
                    WorkflowEventType.USER_INACTIVE,
                    WorkflowEventType.STREAK_ACHIEVED
                ],
                webhook_url=f"{self.webhook_base}/engagement",
                description="Manages user engagement and motivation"
            )
        )
        
        logger.info(f"Registered {len(self.triggers)} default workflow triggers pointing to {self.webhook_base}")
    
    def register_trigger(self, trigger: WorkflowTrigger) -> None:
        """Register a new workflow trigger"""
        self.triggers[trigger.name] = trigger
        logger.debug(f"Registered workflow trigger: {trigger.name}")
    
    def remove_trigger(self, trigger_name: str) -> bool:
        """Remove a workflow trigger"""
        if trigger_name in self.triggers:
            del self.triggers[trigger_name]
            logger.debug(f"Removed workflow trigger: {trigger_name}")
            return True
        return False
    
    async def emit_event(self, event: WorkflowEvent) -> bool:
        """Emit a workflow event for processing (fire-and-forget: does not block on n8n)"""

        try:
            # Add to queue
            self.event_queue.append(event)
            logger.info(f"Event queued: {event.event_type} (ID: {event.event_id})")

            # Kick off queue processing as a background task so the HTTP response
            # is not delayed waiting for the n8n webhook call to complete.
            if not self.processing_events:
                asyncio.create_task(self._process_event_queue())

            return True

        except Exception as e:
            logger.error(f"Failed to emit event {event.event_id}: {str(e)}")
            return False
    
    async def _process_event_queue(self) -> None:
        """Process queued events"""
        
        if self.processing_events:
            return
        
        self.processing_events = True
        
        try:
            while self.event_queue:
                event = self.event_queue.pop(0)
                await self._process_single_event(event)
                
                # Small delay to prevent overwhelming
                await asyncio.sleep(0.1)
                
        except Exception as e:
            logger.error(f"Error processing event queue: {str(e)}")
        finally:
            self.processing_events = False
    
    async def _process_single_event(self, event: WorkflowEvent) -> None:
        """Process a single event by triggering matching workflows"""
        
        triggered_count = 0
        
        for trigger_name, trigger in self.triggers.items():
            if not trigger.is_active:
                continue
            
            # Check if event type matches
            if event.event_type not in trigger.event_types:
                continue
            
            # Check conditions
            if not self._check_trigger_conditions(event, trigger):
                continue
            
            # Trigger workflow
            success = await self._trigger_workflow(event, trigger)
            if success:
                triggered_count += 1
                logger.info(f"Triggered workflow: {trigger_name} for event {event.event_id}")
            else:
                logger.warning(f"Failed to trigger workflow: {trigger_name} for event {event.event_id}")
        
        if triggered_count == 0:
            logger.debug(f"No workflows triggered for event: {event.event_type}")
    
    def _check_trigger_conditions(self, event: WorkflowEvent, trigger: WorkflowTrigger) -> bool:
        """Check if event meets trigger conditions"""
        
        if not trigger.conditions:
            return True
        
        # Example condition checking
        for condition_key, condition_value in trigger.conditions.items():
            if condition_key == "min_score_threshold":
                # Accept either "score" (quiz events) or "average_score" (low-performance events)
                score = event.data.get("score", event.data.get("average_score", 100))
                if score >= condition_value:
                    return False
            
            # Add more condition types as needed
        
        return True
    
    async def _trigger_workflow(self, event: WorkflowEvent, trigger: WorkflowTrigger) -> bool:
        """Trigger n8n workflow via webhook"""
        
        try:
            payload = {
                "event_id": event.event_id,
                "event_type": event.event_type,
                "user_id": str(event.user_id) if event.user_id else None,
                "timestamp": event.timestamp.isoformat(),
                "data": event.data,
                "metadata": event.metadata,
                "trigger_name": trigger.name
            }
            
            async with httpx.AsyncClient(timeout=trigger.timeout_seconds) as client:
                response = await client.post(
                    trigger.webhook_url,
                    json=payload,
                    headers={"Content-Type": "application/json"}
                )
                
                if response.status_code == 200:
                    logger.info(f"Workflow triggered successfully: {trigger.name}")
                    return True
                else:
                    logger.warning(f"Workflow trigger failed: {trigger.name} (Status: {response.status_code})")
                    return False
                    
        except httpx.TimeoutException:
            logger.error(f"Workflow trigger timeout: {trigger.name}")
            return False
        except Exception as e:
            logger.error(f"Workflow trigger error: {trigger.name} - {str(e)}")
            return False
    
    def get_triggers(self) -> List[WorkflowTrigger]:
        """Get all registered triggers"""
        return list(self.triggers.values())
    
    def get_trigger(self, name: str) -> Optional[WorkflowTrigger]:
        """Get a specific trigger by name"""
        return self.triggers.get(name)
    
    def get_event_queue_size(self) -> int:
        """Get current event queue size"""
        return len(self.event_queue)


# Global event system instance — reads n8n_webhook_url from settings at startup
event_system = EventSystem()
