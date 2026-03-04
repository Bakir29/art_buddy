import json
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Set, Optional, Any
from fastapi import WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
import asyncio

from app.entities.collaboration import (
    RealTimeUpdate, CollaborationSession, SessionParticipant, 
    CollaborationMessage, MessageType, SessionStatus, ParticipantRole
)

class WebSocketManager:
    """Manages WebSocket connections for real-time collaboration."""
    
    def __init__(self):
        # session_id -> {user_id -> websocket}
        self.active_connections: Dict[str, Dict[str, WebSocket]] = {}
        # user_id -> set of session_ids they're connected to
        self.user_sessions: Dict[str, Set[str]] = {}
        
    async def connect(self, websocket: WebSocket, session_id: str, user_id: str):
        """Accept WebSocket connection and add to session."""
        await websocket.accept()
        
        if session_id not in self.active_connections:
            self.active_connections[session_id] = {}
        
        self.active_connections[session_id][user_id] = websocket
        
        if user_id not in self.user_sessions:
            self.user_sessions[user_id] = set()
        self.user_sessions[user_id].add(session_id)
        
        # Notify other participants about new connection
        await self.broadcast_to_session(
            session_id, 
            RealTimeUpdate(
                update_type="participant_joined",
                session_id=session_id,
                user_id=user_id,
                data={"message": f"User {user_id} joined the session"}
            ),
            exclude_user=user_id
        )
    
    async def disconnect(self, session_id: str, user_id: str):
        """Handle WebSocket disconnection."""
        if (session_id in self.active_connections and 
            user_id in self.active_connections[session_id]):
            
            del self.active_connections[session_id][user_id]
            
            # Clean up empty session
            if not self.active_connections[session_id]:
                del self.active_connections[session_id]
        
        if user_id in self.user_sessions:
            self.user_sessions[user_id].discard(session_id)
            if not self.user_sessions[user_id]:
                del self.user_sessions[user_id]
        
        # Notify other participants about disconnection
        await self.broadcast_to_session(
            session_id,
            RealTimeUpdate(
                update_type="participant_left",
                session_id=session_id,
                user_id=user_id,
                data={"message": f"User {user_id} left the session"}
            )
        )
    
    async def send_personal_message(self, message: RealTimeUpdate, user_id: str):
        """Send message to specific user across all their sessions."""
        if user_id in self.user_sessions:
            for session_id in self.user_sessions[user_id]:
                if (session_id in self.active_connections and 
                    user_id in self.active_connections[session_id]):
                    websocket = self.active_connections[session_id][user_id]
                    try:
                        await websocket.send_text(message.model_dump_json())
                    except:
                        # Connection might be closed
                        await self.disconnect(session_id, user_id)
    
    async def broadcast_to_session(
        self, 
        session_id: str, 
        message: RealTimeUpdate, 
        exclude_user: Optional[str] = None
    ):
        """Broadcast message to all participants in a session."""
        if session_id not in self.active_connections:
            return
        
        disconnected_users = []
        
        for user_id, websocket in self.active_connections[session_id].items():
            if exclude_user and user_id == exclude_user:
                continue
            
            try:
                await websocket.send_text(message.model_dump_json())
            except:
                # Connection is closed, mark for cleanup
                disconnected_users.append(user_id)
        
        # Clean up disconnected users
        for user_id in disconnected_users:
            await self.disconnect(session_id, user_id)
    
    def get_session_participants(self, session_id: str) -> List[str]:
        """Get list of connected users in a session."""
        if session_id in self.active_connections:
            return list(self.active_connections[session_id].keys())
        return []
    
    def get_user_sessions(self, user_id: str) -> Set[str]:
        """Get all sessions a user is connected to."""
        return self.user_sessions.get(user_id, set())
    
    async def handle_message(self, websocket: WebSocket, session_id: str, user_id: str, raw_message: str):
        """Process incoming WebSocket message."""
        try:
            message_data = json.loads(raw_message)
            
            # Create real-time update
            update = RealTimeUpdate(
                update_type=message_data.get("type", "message"),
                session_id=session_id,
                user_id=user_id, 
                data=message_data.get("data", {}),
                timestamp=datetime.utcnow()
            )
            
            # Broadcast to all other participants
            await self.broadcast_to_session(session_id, update, exclude_user=user_id)
            
        except json.JSONDecodeError:
            # Invalid JSON, send error back to sender
            error_update = RealTimeUpdate(
                update_type="error",
                session_id=session_id,
                user_id=user_id,
                data={"error": "Invalid message format"}
            )
            await websocket.send_text(error_update.model_dump_json())

# Global WebSocket manager instance
websocket_manager = WebSocketManager()
