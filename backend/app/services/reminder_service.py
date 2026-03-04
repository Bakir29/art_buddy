"""
Reminder Service

Business logic for scheduling and managing user reminders.
"""

from typing import List, Optional
from sqlalchemy.orm import Session
from uuid import UUID
from datetime import datetime, timedelta

from ..repositories.reminder_repository import ReminderRepository, ReminderCreate, ReminderUpdate, Reminder


class ReminderService:
    """Service for reminder operations"""
    
    def __init__(self, db: Session):
        self.db = db
        self.reminder_repository = ReminderRepository(db)
    
    async def get_reminder(self, reminder_id: int) -> Optional[Reminder]:
        """Get reminder by ID"""
        return self.reminder_repository.get_reminder_by_id(reminder_id)
    
    async def get_user_reminders(self, user_id: UUID, active_only: bool = True) -> List[Reminder]:
        """Get all reminders for a user"""
        return self.reminder_repository.get_reminders_by_user(
            user_id=user_id,
            active_only=active_only
        )
    
    async def schedule_reminder(
        self,
        user_id: UUID,
        reminder_type: str,
        schedule_time: datetime,
        message: str,
        recurring: bool = False,
        recurring_pattern: Optional[str] = None
    ) -> Reminder:
        """Schedule a new reminder for a user"""
        
        reminder_data = ReminderCreate(
            user_id=user_id,
            reminder_type=reminder_type,
            message=message,
            schedule_time=schedule_time,
            status="scheduled",
            recurring=recurring,
            recurring_pattern=recurring_pattern
        )
        
        reminder = self.reminder_repository.create_reminder(reminder_data)
        
        # If recurring, schedule the next occurrence
        if recurring and recurring_pattern:
            await self._schedule_next_occurrence(reminder)
        
        return reminder
    
    async def update_reminder(self, reminder_id: int, reminder_update: ReminderUpdate) -> Optional[Reminder]:
        """Update reminder"""
        return self.reminder_repository.update_reminder(reminder_id, reminder_update)
    
    async def cancel_reminder(self, reminder_id: int) -> bool:
        """Cancel a reminder"""
        reminder_update = ReminderUpdate(status="cancelled")
        updated = await self.update_reminder(reminder_id, reminder_update)
        return updated is not None
    
    async def mark_reminder_sent(self, reminder_id: int) -> bool:
        """Mark reminder as sent"""
        reminder = await self.get_reminder(reminder_id)
        if not reminder:
            return False
        
        # Update status to sent
        reminder_update = ReminderUpdate(
            status="sent",
            sent_at=datetime.utcnow()
        )
        
        updated = await self.update_reminder(reminder_id, reminder_update)
        
        # If recurring, schedule next occurrence
        if updated and updated.recurring and updated.recurring_pattern:
            await self._schedule_next_occurrence(updated)
        
        return updated is not None
    
    async def get_pending_reminders(self, cutoff_time: Optional[datetime] = None) -> List[Reminder]:
        """Get reminders that are ready to be sent"""
        
        if cutoff_time is None:
            cutoff_time = datetime.utcnow()
        
        return self.reminder_repository.get_reminders_due_before(cutoff_time)
    
    async def schedule_practice_reminder(
        self,
        user_id: UUID,
        practice_time: datetime,
        message: Optional[str] = None
    ) -> Reminder:
        """Schedule a practice reminder for a user"""
        
        if message is None:
            message = "Time for your art practice session! 🎨"
        
        return await self.schedule_reminder(
            user_id=user_id,
            reminder_type="practice",
            schedule_time=practice_time,
            message=message,
            recurring=False
        )
    
    async def schedule_lesson_reminder(
        self,
        user_id: UUID,
        lesson_id: int,
        reminder_time: datetime,
        message: Optional[str] = None
    ) -> Reminder:
        """Schedule a lesson reminder for a user"""
        
        if message is None:
            message = f"Don't forget to continue with your lesson! 📚"
        
        return await self.schedule_reminder(
            user_id=user_id,
            reminder_type="lesson",
            schedule_time=reminder_time,
            message=message,
            recurring=False
        )
    
    async def schedule_daily_practice_reminders(
        self,
        user_id: UUID,
        practice_time_hour: int = 19,  # 7 PM default
        message: Optional[str] = None
    ) -> Reminder:
        """Schedule daily recurring practice reminders"""
        
        if message is None:
            message = "Daily practice time! Keep improving your art skills 🎨"
        
        # Schedule for today at the specified hour
        today = datetime.utcnow().replace(hour=practice_time_hour, minute=0, second=0, microsecond=0)
        
        # If time has passed today, schedule for tomorrow
        if today <= datetime.utcnow():
            today += timedelta(days=1)
        
        return await self.schedule_reminder(
            user_id=user_id,
            reminder_type="practice",
            schedule_time=today,
            message=message,
            recurring=True,
            recurring_pattern="daily"
        )
    
    async def schedule_weekly_progress_reminder(
        self,
        user_id: UUID,
        day_of_week: int = 6,  # Sunday = 6
        hour: int = 10,  # 10 AM
        message: Optional[str] = None
    ) -> Reminder:
        """Schedule weekly progress review reminders"""
        
        if message is None:
            message = "Time to review your weekly art progress! 📈"
        
        # Calculate next occurrence of the specified day
        now = datetime.utcnow()
        days_ahead = day_of_week - now.weekday()
        
        if days_ahead <= 0:  # Target day already happened this week
            days_ahead += 7
        
        next_reminder = (now + timedelta(days=days_ahead)).replace(
            hour=hour, minute=0, second=0, microsecond=0
        )
        
        return await self.schedule_reminder(
            user_id=user_id,
            reminder_type="progress",
            schedule_time=next_reminder,
            message=message,
            recurring=True,
            recurring_pattern="weekly"
        )
    
    async def _schedule_next_occurrence(self, reminder: Reminder) -> None:
        """Schedule the next occurrence of a recurring reminder"""
        
        if not reminder.recurring or not reminder.recurring_pattern:
            return
        
        next_time = None
        
        if reminder.recurring_pattern == "daily":
            next_time = reminder.schedule_time + timedelta(days=1)
        elif reminder.recurring_pattern == "weekly":
            next_time = reminder.schedule_time + timedelta(weeks=1)
        elif reminder.recurring_pattern == "monthly":
            # Approximate monthly (30 days)
            next_time = reminder.schedule_time + timedelta(days=30)
        
        if next_time:
            # Create new reminder for next occurrence
            await self.schedule_reminder(
                user_id=reminder.user_id,
                reminder_type=reminder.reminder_type,
                schedule_time=next_time,
                message=reminder.message,
                recurring=True,
                recurring_pattern=reminder.recurring_pattern
            )
