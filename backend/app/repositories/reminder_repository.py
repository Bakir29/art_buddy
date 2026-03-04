"""
Reminder Repository - Simplified for MCP compatibility

Data access layer for Reminder entities.
"""

from typing import List, Optional, Any
from sqlalchemy.orm import Session
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel

# Simplified schemas for MCP compatibility
class ReminderCreate(BaseModel):
    user_id: UUID
    reminder_type: str
    message: str
    schedule_time: datetime
    status: Optional[str] = "scheduled"
    recurring: Optional[bool] = False
    recurring_pattern: Optional[str] = None

class ReminderUpdate(BaseModel):
    reminder_type: Optional[str] = None
    message: Optional[str] = None
    schedule_time: Optional[datetime] = None
    status: Optional[str] = None
    recurring: Optional[bool] = None
    recurring_pattern: Optional[str] = None
    sent_at: Optional[datetime] = None

# Mock Reminder class for compatibility
class Reminder:
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
        self.id = kwargs.get('id', 1)
        self.status = kwargs.get('status', 'scheduled')
        self.recurring = kwargs.get('recurring', False)
        self.recurring_pattern = kwargs.get('recurring_pattern')
        self.schedule_time = kwargs.get('schedule_time', datetime.utcnow())

class ReminderRepository:
    """Repository for reminder data operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_reminder_by_id(self, reminder_id: int) -> Optional[Reminder]:
        """Get reminder by ID - Mock implementation"""
        return Reminder(id=reminder_id, message=f"Mock reminder {reminder_id}")
    
    def get_reminders_by_user(
        self, 
        user_id: UUID, 
        active_only: bool = True,
        skip: int = 0,
        limit: int = 100
    ) -> List[Reminder]:
        """Get reminders for a user - Mock implementation"""
        return [Reminder(id=1, user_id=user_id, message="Mock reminder")]
    
    def get_reminders_due_before(self, cutoff_time: datetime) -> List[Reminder]:
        """Get reminders that are due before the specified time - Mock implementation"""
        return []
    
    def create_reminder(self, reminder_data: ReminderCreate) -> Reminder:
        """Create a new reminder - Mock implementation"""
        return Reminder(
            id=1,
            user_id=reminder_data.user_id,
            reminder_type=reminder_data.reminder_type,
            message=reminder_data.message,
            schedule_time=reminder_data.schedule_time,
            status=reminder_data.status,
            recurring=reminder_data.recurring,
            recurring_pattern=reminder_data.recurring_pattern
        )
    
    def update_reminder(self, reminder_id: int, reminder_update: ReminderUpdate) -> Optional[Reminder]:
        """Update reminder - Mock implementation"""
        return self.get_reminder_by_id(reminder_id)
    
    def delete_reminder(self, reminder_id: int) -> bool:
        """Delete reminder - Mock implementation"""
        return True
