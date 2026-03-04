from pydantic import BaseModel
from datetime import datetime
from typing import List, Dict, Any, Optional
from enum import Enum

class CollaborationSessionType(str, Enum):
    ART_CRITIQUE = "art_critique"
    GROUP_STUDY = "group_study"
    PEER_REVIEW = "peer_review"
    LIVE_TUTORIAL = "live_tutorial"
    OPEN_STUDIO = "open_studio"

class SessionStatus(str, Enum):
    WAITING = "waiting"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class ParticipantRole(str, Enum):
    HOST = "host"
    PARTICIPANT = "participant"
    OBSERVER = "observer"
    MENTOR = "mentor"

class MessageType(str, Enum):
    TEXT = "text"
    VOICE_NOTE = "voice_note"
    IMAGE_ANNOTATION = "image_annotation"
    SKETCH_OVERLAY = "sketch_overlay"
    SYSTEM = "system"

class CollaborationSession(BaseModel):
    id: str
    title: str
    description: Optional[str] = None
    session_type: CollaborationSessionType
    status: SessionStatus
    host_id: str
    max_participants: int = 10
    is_public: bool = True
    requires_approval: bool = False
    skill_level_filter: Optional[str] = None  # beginner, intermediate, advanced
    tags: List[str] = []
    created_at: datetime
    scheduled_start: Optional[datetime] = None
    actual_start: Optional[datetime] = None
    ended_at: Optional[datetime] = None
    session_data: Dict[str, Any] = {}  # Session-specific data

class SessionParticipant(BaseModel):
    user_id: str
    session_id: str
    role: ParticipantRole
    joined_at: datetime
    left_at: Optional[datetime] = None
    is_active: bool = True
    permissions: Dict[str, bool] = {}  # can_draw, can_comment, etc.

class CollaborationMessage(BaseModel):
    id: str
    session_id: str
    sender_id: str
    message_type: MessageType
    content: str
    metadata: Dict[str, Any] = {}  # For images, coordinates, etc.
    timestamp: datetime
    reply_to: Optional[str] = None  # For threaded conversations
    reactions: Dict[str, List[str]] = {}  # emoji -> list of user_ids

class ArtworkCritiqueSession(CollaborationSession):
    """Specialized session for artwork critique."""
    artwork_url: str
    artwork_owner_id: str
    critique_focus: List[str] = []  # composition, color, technique, etc.
    anonymous_feedback: bool = False

class LiveSketchSession(CollaborationSession):
    """Specialized session for collaborative sketching."""
    canvas_data: str  # Base64 encoded canvas state
    brush_settings: Dict[str, Any] = {}
    layers: List[Dict[str, Any]] = []

class SessionInvitation(BaseModel):
    id: str
    session_id: str
    inviter_id: str
    invitee_id: str
    message: Optional[str] = None
    status: str = "pending"  # pending, accepted, declined
    created_at: datetime
    expires_at: Optional[datetime] = None

class CollaborationFeedback(BaseModel):
    id: str
    session_id: str
    reviewer_id: str
    target_user_id: Optional[str] = None  # None for general session feedback
    rating: float  # 1-5 stars
    feedback_text: str
    helpful_count: int = 0
    created_at: datetime

class RealTimeUpdate(BaseModel):
    """Real-time update message for WebSocket communication."""
    update_type: str  # participant_joined, message_sent, canvas_updated, etc.
    session_id: str
    user_id: str
    data: Dict[str, Any]
    timestamp: datetime = datetime.utcnow()

class SessionSummary(BaseModel):
    """Summary generated after session completion."""
    session_id: str
    total_duration_minutes: int
    participant_count: int
    message_count: int
    key_insights: List[str]
    feedback_highlights: List[str]
    generated_resources: List[str]  # URLs to saved sketches, notes, etc.
    created_at: datetime
