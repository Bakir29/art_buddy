from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException, Query
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
import json

from app.database import get_db
from app.auth.dependencies import get_current_user, get_current_user_websocket
from app.entities.collaboration import (
    CollaborationSession, CollaborationSessionType, SessionStatus,
    ParticipantRole, MessageType, SessionInvitation, CollaborationFeedback
)
from app.services.collaboration_service import CollaborationService
from app.services.websocket_manager import websocket_manager

router = APIRouter(prefix="/api/collaboration", tags=["Real-time Collaboration"])
security = HTTPBearer()

def get_collaboration_service(db: Session = Depends(get_db)) -> CollaborationService:
    """Dependency to get collaboration service."""
    return CollaborationService(db)

# WebSocket endpoint for real-time communication
@router.websocket("/ws/{session_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    session_id: str,
    token: str = Query(...),
    db: Session = Depends(get_db)
):
    """WebSocket endpoint for real-time collaboration."""
    
    try:
        # Authenticate user from token
        user_data = await get_current_user_websocket(token, db)
        user_id = user_data["user_id"]
        
        # Connect to WebSocket manager
        await websocket_manager.connect(websocket, session_id, user_id)
        
        try:
            while True:
                # Receive message from client
                data = await websocket.receive_text()
                
                # Handle the message
                await websocket_manager.handle_message(
                    websocket, session_id, user_id, data
                )
                
        except WebSocketDisconnect:
            # Handle client disconnect
            await websocket_manager.disconnect(session_id, user_id)
            
    except Exception as e:
        # Authentication or other error
        await websocket.close(code=1008, reason=f"Authentication failed: {str(e)}")

# REST API endpoints for session management

@router.post("/sessions", response_model=CollaborationSession)
async def create_session(
    title: str,
    session_type: CollaborationSessionType,
    description: Optional[str] = None,
    max_participants: int = 10,
    is_public: bool = True,
    skill_level_filter: Optional[str] = None,
    tags: Optional[List[str]] = None,
    current_user = Depends(get_current_user),
    service: CollaborationService = Depends(get_collaboration_service)
):
    """
    Create a new collaboration session.
    
    - **title**: Session title
    - **session_type**: Type of collaboration (art_critique, group_study, etc.)
    - **description**: Optional session description
    - **max_participants**: Maximum number of participants (default: 10)
    - **is_public**: Whether session is public (default: true)
    - **skill_level_filter**: Filter by skill level (beginner, intermediate, advanced)
    - **tags**: Optional tags for session categorization
    """
    try:
        session = await service.create_session(
            host_id=current_user["user_id"],
            title=title,
            session_type=session_type,
            description=description,
            max_participants=max_participants,
            is_public=is_public,
            skill_level_filter=skill_level_filter,
            tags=tags or []
        )
        return session
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create session: {str(e)}")

@router.post("/sessions/{session_id}/join")
async def join_session(
    session_id: str,
    role: ParticipantRole = ParticipantRole.PARTICIPANT,
    current_user = Depends(get_current_user),
    service: CollaborationService = Depends(get_collaboration_service)
):
    """Join an existing collaboration session."""
    try:
        success, message = await service.join_session(
            session_id, current_user["user_id"], role
        )
        
        if not success:
            raise HTTPException(status_code=400, detail=message)
        
        return {"message": message, "session_id": session_id}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to join session: {str(e)}")

@router.post("/sessions/{session_id}/start")
async def start_session(
    session_id: str,
    current_user = Depends(get_current_user),
    service: CollaborationService = Depends(get_collaboration_service)
):
    """Start a collaboration session (host only)."""
    try:
        success = await service.start_session(session_id, current_user["user_id"])
        
        if not success:
            raise HTTPException(status_code=403, detail="Not authorized to start this session")
        
        return {"message": "Session started successfully", "session_id": session_id}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start session: {str(e)}")

@router.post("/sessions/{session_id}/end")
async def end_session(
    session_id: str,
    current_user = Depends(get_current_user),
    service: CollaborationService = Depends(get_collaboration_service)
):
    """End a collaboration session (host only)."""
    try:
        summary = await service.end_session(session_id, current_user["user_id"])
        
        if not summary:
            raise HTTPException(status_code=403, detail="Not authorized to end this session")
        
        return {
            "message": "Session ended successfully", 
            "session_id": session_id,
            "summary": summary
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to end session: {str(e)}")

@router.post("/sessions/{session_id}/messages")
async def send_message(
    session_id: str,
    message_type: MessageType,
    content: str,
    metadata: Optional[Dict[str, Any]] = None,
    reply_to: Optional[str] = None,
    current_user = Depends(get_current_user),
    service: CollaborationService = Depends(get_collaboration_service)
):
    """Send a message in a collaboration session."""
    try:
        message = await service.send_message(
            session_id=session_id,
            sender_id=current_user["user_id"],
            message_type=message_type,
            content=content,
            metadata=metadata,
            reply_to=reply_to
        )
        
        return {"message": "Message sent successfully", "message_id": message.id}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send message: {str(e)}")

@router.post("/sessions/art-critique")
async def create_artwork_critique_session(
    title: str,
    artwork_url: str,
    artwork_owner_id: str,
    critique_focus: Optional[List[str]] = None,
    anonymous_feedback: bool = False,
    description: Optional[str] = None,
    max_participants: int = 8,
    current_user = Depends(get_current_user),
    service: CollaborationService = Depends(get_collaboration_service)
):
    """
    Create a specialized artwork critique session.
    
    - **artwork_url**: URL to the artwork image
    - **artwork_owner_id**: ID of the artwork owner
    - **critique_focus**: Areas to focus critique on (composition, color, etc.)
    - **anonymous_feedback**: Allow anonymous feedback
    """
    try:
        session = await service.create_artwork_critique_session(
            host_id=current_user["user_id"],
            artwork_url=artwork_url,
            artwork_owner_id=artwork_owner_id,
            title=title,
            critique_focus=critique_focus or [],
            anonymous_feedback=anonymous_feedback,
            description=description,
            max_participants=max_participants,
            is_public=True
        )
        
        return session
        
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to create artwork critique session: {str(e)}"
        )

@router.post("/sessions/live-sketch")
async def create_live_sketch_session(
    title: str,
    description: Optional[str] = None,
    max_participants: int = 6,
    current_user = Depends(get_current_user),
    service: CollaborationService = Depends(get_collaboration_service)
):
    """
    Create a collaborative live sketching session.
    
    Allows multiple users to draw on a shared canvas in real-time.
    """
    try:
        session = await service.create_live_sketch_session(
            host_id=current_user["user_id"],
            title=title,
            description=description,
            max_participants=max_participants,
            is_public=True
        )
        
        return session
        
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to create live sketch session: {str(e)}"
        )

@router.post("/sessions/{session_id}/canvas")
async def update_canvas(
    session_id: str,
    canvas_data: str,
    stroke_data: Optional[Dict[str, Any]] = None,
    current_user = Depends(get_current_user),
    service: CollaborationService = Depends(get_collaboration_service)
):
    """Update collaborative canvas with new drawing data."""
    try:
        success = await service.update_canvas(
            session_id=session_id,
            user_id=current_user["user_id"],
            canvas_data=canvas_data,
            stroke_data=stroke_data
        )
        
        if not success:
            raise HTTPException(status_code=400, detail="Failed to update canvas")
        
        return {"message": "Canvas updated successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update canvas: {str(e)}")

@router.post("/sessions/{session_id}/invite")
async def send_invitation(
    session_id: str,
    invitee_id: str,
    message: Optional[str] = None,
    current_user = Depends(get_current_user),
    service: CollaborationService = Depends(get_collaboration_service)
):
    """Send invitation to join a session."""
    try:
        invitation = await service.send_invitation(
            session_id=session_id,
            inviter_id=current_user["user_id"],
            invitee_id=invitee_id,
            message=message
        )
        
        return {"message": "Invitation sent successfully", "invitation_id": invitation.id}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send invitation: {str(e)}")

@router.post("/sessions/{session_id}/feedback")
async def submit_feedback(
    session_id: str,
    rating: float,
    feedback_text: str,
    target_user_id: Optional[str] = None,
    current_user = Depends(get_current_user),
    service: CollaborationService = Depends(get_collaboration_service)
):
    """
    Submit feedback for a session or specific participant.
    
    - **rating**: Rating from 1-5 stars
    - **feedback_text**: Written feedback
    - **target_user_id**: Optional - specific user to give feedback about
    """
    try:
        feedback = await service.submit_feedback(
            session_id=session_id,
            reviewer_id=current_user["user_id"],
            rating=rating,
            feedback_text=feedback_text,
            target_user_id=target_user_id
        )
        
        return {"message": "Feedback submitted successfully", "feedback_id": feedback.id}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to submit feedback: {str(e)}")

@router.get("/sessions/public", response_model=List[CollaborationSession])
async def get_public_sessions(
    session_type: Optional[CollaborationSessionType] = Query(None),
    skill_level: Optional[str] = Query(None),
    limit: int = Query(20, le=50),
    service: CollaborationService = Depends(get_collaboration_service)
):
    """Get list of public sessions available to join."""
    try:
        sessions = await service.get_public_sessions(
            session_type=session_type,
            skill_level=skill_level,
            limit=limit
        )
        return sessions
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch sessions: {str(e)}")

@router.get("/sessions/my-sessions", response_model=List[CollaborationSession])
async def get_my_sessions(
    status_filter: Optional[SessionStatus] = Query(None),
    current_user = Depends(get_current_user),
    service: CollaborationService = Depends(get_collaboration_service)
):
    """Get user's collaboration sessions."""
    try:
        sessions = await service.get_user_sessions(
            user_id=current_user["user_id"],
            status_filter=status_filter
        )
        return sessions
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch user sessions: {str(e)}")

@router.get("/sessions/{session_id}/participants")
async def get_session_participants(
    session_id: str,
    current_user = Depends(get_current_user),
    service: CollaborationService = Depends(get_collaboration_service)
):
    """Get all participants in a session."""
    try:
        participants = await service.get_active_participants(session_id)
        
        # Get connected users from WebSocket manager
        connected_users = websocket_manager.get_session_participants(session_id)
        
        return {
            "participants": [p.model_dump() for p in participants],
            "connected_users": connected_users,
            "total_count": len(participants)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to fetch participants: {str(e)}"
        )

@router.get("/sessions/{session_id}/messages")
async def get_session_messages(
    session_id: str,
    limit: int = Query(50, le=200),
    offset: int = Query(0, ge=0),
    current_user = Depends(get_current_user),
    service: CollaborationService = Depends(get_collaboration_service)
):
    """Get messages from a collaboration session."""
    try:
        messages = await service.get_session_messages(session_id)
        
        # Apply pagination
        paginated_messages = messages[offset:offset + limit] if messages else []
        
        return {
            "messages": [m.model_dump() for m in paginated_messages],
            "total_count": len(messages) if messages else 0,
            "has_more": len(messages) > offset + limit if messages else False
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to fetch messages: {str(e)}"
        )
