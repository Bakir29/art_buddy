import uuid
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func

from app.entities.collaboration import (
    CollaborationSession, SessionParticipant, CollaborationMessage,
    SessionInvitation, CollaborationFeedback, SessionSummary,
    CollaborationSessionType, SessionStatus, ParticipantRole, MessageType,
    ArtworkCritiqueSession, LiveSketchSession, RealTimeUpdate
)
from app.services.websocket_manager import websocket_manager
from app.entities.models import User

class CollaborationService:
    """Service for managing real-time collaboration sessions."""
    
    def __init__(self, db: Session):
        self.db = db
    
    async def create_session(
        self, 
        host_id: str, 
        title: str,
        session_type: CollaborationSessionType,
        description: Optional[str] = None,
        max_participants: int = 10,
        is_public: bool = True,
        skill_level_filter: Optional[str] = None,
        tags: List[str] = None,
        scheduled_start: Optional[datetime] = None,
        **session_specific_data
    ) -> CollaborationSession:
        """Create a new collaboration session."""
        
        session_id = str(uuid.uuid4())
        
        # Create base session
        session = CollaborationSession(
            id=session_id,
            title=title,
            description=description,
            session_type=session_type,
            status=SessionStatus.WAITING,
            host_id=host_id,
            max_participants=max_participants,
            is_public=is_public,
            requires_approval=not is_public,
            skill_level_filter=skill_level_filter,
            tags=tags or [],
            created_at=datetime.utcnow(),
            scheduled_start=scheduled_start,
            session_data=session_specific_data
        )
        
        # Add host as first participant
        await self.add_participant(
            session_id, 
            host_id, 
            ParticipantRole.HOST,
            auto_approve=True
        )
        
        # Store in database (you would need to create the table model)
        # For now, we'll keep it in memory or implement persistence separately
        
        return session
    
    async def join_session(
        self, 
        session_id: str, 
        user_id: str,
        role: ParticipantRole = ParticipantRole.PARTICIPANT
    ) -> Tuple[bool, str]:
        """Attempt to join a collaboration session."""
        
        session = await self.get_session(session_id)
        if not session:
            return False, "Session not found"
        
        if session.status not in [SessionStatus.WAITING, SessionStatus.ACTIVE]:
            return False, "Session is not currently accepting participants"
        
        # Check if already a participant
        existing = await self.get_participant(session_id, user_id)
        if existing:
            return False, "Already a participant in this session"
        
        # Check participant limit
        current_participants = await self.get_active_participants(session_id)
        if len(current_participants) >= session.max_participants:
            return False, "Session is full"
        
        # Check skill level filter
        if session.skill_level_filter:
            user = self.db.query(User).filter(User.id == user_id).first()
            if user and user.skill_level != session.skill_level_filter:
                return False, "Skill level doesn't match session requirements"
        
        # Add participant
        await self.add_participant(
            session_id, 
            user_id, 
            role,
            auto_approve=not session.requires_approval
        )
        
        return True, "Successfully joined session"
    
    async def add_participant(
        self,
        session_id: str,
        user_id: str, 
        role: ParticipantRole,
        auto_approve: bool = True
    ) -> SessionParticipant:
        """Add a participant to a session."""
        
        participant = SessionParticipant(
            user_id=user_id,
            session_id=session_id,
            role=role,
            joined_at=datetime.utcnow(),
            is_active=auto_approve,
            permissions={
                "can_draw": role in [ParticipantRole.HOST, ParticipantRole.PARTICIPANT],
                "can_comment": True,
                "can_voice_chat": True,
                "can_moderate": role == ParticipantRole.HOST
            }
        )
        
        # Store in database
        # ... database persistence logic
        
        return participant
    
    async def send_message(
        self,
        session_id: str,
        sender_id: str,
        message_type: MessageType,
        content: str,
        metadata: Dict[str, Any] = None,
        reply_to: Optional[str] = None
    ) -> CollaborationMessage:
        """Send a message in a collaboration session."""
        
        message = CollaborationMessage(
            id=str(uuid.uuid4()),
            session_id=session_id,
            sender_id=sender_id,
            message_type=message_type,
            content=content,
            metadata=metadata or {},
            timestamp=datetime.utcnow(),
            reply_to=reply_to,
            reactions={}
        )
        
        # Store message in database
        # ... database persistence logic
        
        # Broadcast to all session participants
        update = RealTimeUpdate(
            update_type="new_message",
            session_id=session_id,
            user_id=sender_id,
            data={
                "message": message.model_dump(),
                "sender_info": await self.get_user_info(sender_id)
            }
        )
        
        await websocket_manager.broadcast_to_session(session_id, update)
        
        return message
    
    async def start_session(self, session_id: str, host_id: str) -> bool:
        """Start a collaboration session."""
        
        session = await self.get_session(session_id)
        if not session or session.host_id != host_id:
            return False
        
        if session.status != SessionStatus.WAITING:
            return False
        
        # Update session status
        session.status = SessionStatus.ACTIVE
        session.actual_start = datetime.utcnow()
        
        # Broadcast session start to all participants
        update = RealTimeUpdate(
            update_type="session_started",
            session_id=session_id,
            user_id=host_id,
            data={
                "message": "Session has started!",
                "session_info": session.model_dump()
            }
        )
        
        await websocket_manager.broadcast_to_session(session_id, update)
        
        return True
    
    async def end_session(self, session_id: str, host_id: str) -> Optional[SessionSummary]:
        """End a collaboration session and generate summary."""
        
        session = await self.get_session(session_id)
        if not session or session.host_id != host_id:
            return None
        
        if session.status not in [SessionStatus.ACTIVE, SessionStatus.PAUSED]:
            return None
        
        # Update session status
        session.status = SessionStatus.COMPLETED
        session.ended_at = datetime.utcnow()
        
        # Generate session summary
        summary = await self.generate_session_summary(session_id)
        
        # Broadcast session end to all participants
        update = RealTimeUpdate(
            update_type="session_ended",
            session_id=session_id,
            user_id=host_id,
            data={
                "message": "Session has ended",
                "summary": summary.model_dump() if summary else None
            }
        )
        
        await websocket_manager.broadcast_to_session(session_id, update)
        
        return summary
    
    async def create_artwork_critique_session(
        self,
        host_id: str,
        artwork_url: str,
        artwork_owner_id: str,
        title: str,
        critique_focus: List[str] = None,
        anonymous_feedback: bool = False,
        **kwargs
    ) -> ArtworkCritiqueSession:
        """Create specialized artwork critique session."""
        
        session = ArtworkCritiqueSession(
            id=str(uuid.uuid4()),
            title=title,
            session_type=CollaborationSessionType.ART_CRITIQUE,
            status=SessionStatus.WAITING,
            host_id=host_id,
            artwork_url=artwork_url,
            artwork_owner_id=artwork_owner_id,
            critique_focus=critique_focus or [],
            anonymous_feedback=anonymous_feedback,
            created_at=datetime.utcnow(),
            **kwargs
        )
        
        # Add both host and artwork owner as participants
        await self.add_participant(session.id, host_id, ParticipantRole.HOST)
        if artwork_owner_id != host_id:
            await self.add_participant(session.id, artwork_owner_id, ParticipantRole.PARTICIPANT)
        
        return session
    
    async def create_live_sketch_session(
        self,
        host_id: str,
        title: str,
        canvas_data: str = "",
        **kwargs
    ) -> LiveSketchSession:
        """Create specialized collaborative sketching session."""
        
        session = LiveSketchSession(
            id=str(uuid.uuid4()),
            title=title,
            session_type=CollaborationSessionType.OPEN_STUDIO,
            status=SessionStatus.WAITING,
            host_id=host_id,
            canvas_data=canvas_data,
            brush_settings={
                "brush_size": 5,
                "brush_color": "#000000",
                "brush_type": "pen"
            },
            layers=[{"id": "layer_1", "name": "Background", "visible": True}],
            created_at=datetime.utcnow(),
            **kwargs
        )
        
        await self.add_participant(session.id, host_id, ParticipantRole.HOST)
        return session
    
    async def update_canvas(
        self,
        session_id: str,
        user_id: str,
        canvas_data: str,
        stroke_data: Dict[str, Any] = None
    ):
        """Update collaborative canvas in real-time."""
        
        session = await self.get_session(session_id)
        if not isinstance(session, LiveSketchSession):
            return False
        
        # Update canvas data
        session.canvas_data = canvas_data
        
        # Broadcast canvas update to other participants
        update = RealTimeUpdate(
            update_type="canvas_updated",
            session_id=session_id,
            user_id=user_id,
            data={
                "canvas_data": canvas_data,
                "stroke_data": stroke_data,
                "timestamp": datetime.utcnow().isoformat()
            }
        )
        
        await websocket_manager.broadcast_to_session(
            session_id, 
            update, 
            exclude_user=user_id
        )
        
        return True
    
    async def send_invitation(
        self,
        session_id: str,
        inviter_id: str,
        invitee_id: str,
        message: Optional[str] = None
    ) -> SessionInvitation:
        """Send invitation to join a session."""
        
        invitation = SessionInvitation(
            id=str(uuid.uuid4()),
            session_id=session_id,
            inviter_id=inviter_id,
            invitee_id=invitee_id,
            message=message,
            status="pending",
            created_at=datetime.utcnow(),
            expires_at=datetime.utcnow() + timedelta(hours=24)
        )
        
        # Store invitation in database
        # ... database persistence logic
        
        # Send real-time notification to invitee
        update = RealTimeUpdate(
            update_type="session_invitation",
            session_id=session_id,
            user_id=inviter_id,
            data={
                "invitation": invitation.model_dump(),
                "session_info": (await self.get_session(session_id)).model_dump(),
                "inviter_info": await self.get_user_info(inviter_id)
            }
        )
        
        await websocket_manager.send_personal_message(update, invitee_id)
        
        return invitation
    
    async def submit_feedback(
        self,
        session_id: str,
        reviewer_id: str,
        rating: float,
        feedback_text: str,
        target_user_id: Optional[str] = None
    ) -> CollaborationFeedback:
        """Submit feedback for a session or specific participant."""
        
        feedback = CollaborationFeedback(
            id=str(uuid.uuid4()),
            session_id=session_id,
            reviewer_id=reviewer_id,
            target_user_id=target_user_id,
            rating=max(1.0, min(5.0, rating)),  # Clamp to 1-5 range
            feedback_text=feedback_text,
            helpful_count=0,
            created_at=datetime.utcnow()
        )
        
        # Store in database
        # ... database persistence logic
        
        return feedback
    
    async def get_public_sessions(
        self,
        session_type: Optional[CollaborationSessionType] = None,
        skill_level: Optional[str] = None,
        limit: int = 20
    ) -> List[CollaborationSession]:
        """Get list of public sessions available to join."""
        
        # This would query the database for public sessions
        # For now, return mock data
        return []
    
    async def get_user_sessions(
        self,
        user_id: str,
        status_filter: Optional[SessionStatus] = None
    ) -> List[CollaborationSession]:
        """Get all sessions for a specific user."""
        
        # This would query the database for user's sessions
        # For now, return mock data
        return []
    
    async def generate_session_summary(self, session_id: str) -> Optional[SessionSummary]:
        """Generate AI-powered session summary."""
        
        session = await self.get_session(session_id)
        if not session:
            return None
        
        # Calculate session metrics
        duration = 0
        if session.actual_start and session.ended_at:
            duration = int((session.ended_at - session.actual_start).total_seconds() / 60)
        
        # Get session statistics
        participants = await self.get_all_participants(session_id)
        messages = await self.get_session_messages(session_id)
        
        # Generate insights (this could use AI to analyze content)
        key_insights = [
            "Active discussion about color theory and composition",
            "Multiple constructive feedback exchanges",
            "Demonstrated progress in technique understanding"
        ]
        
        feedback_highlights = [
            "Excellent use of negative space",
            "Strong improvement in proportion accuracy", 
            "Creative approach to lighting effects"
        ]
        
        summary = SessionSummary(
            session_id=session_id,
            total_duration_minutes=duration,
            participant_count=len(participants),
            message_count=len(messages) if messages else 0,
            key_insights=key_insights,
            feedback_highlights=feedback_highlights,
            generated_resources=[],  # URLs to saved content
            created_at=datetime.utcnow()
        )
        
        return summary
    
    # Helper methods (these would interact with actual database)
    async def get_session(self, session_id: str) -> Optional[CollaborationSession]:
        """Get session by ID."""
        # Database query implementation
        return None
    
    async def get_participant(self, session_id: str, user_id: str) -> Optional[SessionParticipant]:
        """Get participant in a session."""
        # Database query implementation
        return None
    
    async def get_active_participants(self, session_id: str) -> List[SessionParticipant]:
        """Get all active participants in a session."""
        # Database query implementation
        return []
    
    async def get_all_participants(self, session_id: str) -> List[SessionParticipant]:
        """Get all participants (including past) for a session."""
        # Database query implementation
        return []
    
    async def get_session_messages(self, session_id: str) -> List[CollaborationMessage]:
        """Get all messages for a session."""
        # Database query implementation
        return []
    
    async def get_user_info(self, user_id: str) -> Dict[str, Any]:
        """Get basic user information for display."""
        user = self.db.query(User).filter(User.id == user_id).first()
        if user:
            return {
                "id": user.id,
                "name": user.name,
                "skill_level": user.skill_level
            }
        return {"id": user_id, "name": "Unknown User", "skill_level": "unknown"}
