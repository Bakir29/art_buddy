import uuid
import json
import hashlib
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc
import asyncio

from app.entities.offline import (
    OfflineContent, OfflineAction, SyncConflict, OfflineSession,
    OfflineCapabilities, SmartSync, OfflineAnalytics, OfflineWorkspace,
    OfflineQueue, SyncStatus, ConflictResolution, OfflineCapability
)
from app.entities.models import User, Lesson, Progress, QuizQuestion, QuizResponse

class OfflineService:
    """Advanced offline capabilities service with intelligent sync and conflict resolution."""
    
    def __init__(self, db: Session):
        self.db = db
        self.max_retry_attempts = 3
        self.sync_batch_size = 50
    
    async def prepare_offline_content(
        self, 
        user_id: str, 
        device_id: str,
        content_types: List[str] = None,
        priority_content: List[str] = None
    ) -> Dict[str, Any]:
        """Prepare and package content for offline use."""
        
        # Get user's offline capabilities and preferences
        capabilities = await self.get_offline_capabilities(user_id, device_id)
        
        # Determine what content to include
        content_to_package = await self.determine_offline_content(
            user_id, capabilities, content_types, priority_content
        )
        
        # Package content with dependencies
        packaged_content = {}
        total_size = 0
        
        for content_id, content_info in content_to_package.items():
            # Get content with dependencies
            content_package = await self.package_content_with_dependencies(
                content_id, content_info
            )
            
            # Check storage constraints
            if total_size + content_package["size_bytes"] > capabilities.storage_quota_mb * 1024 * 1024:
                break  # Stop if would exceed quota
            
            packaged_content[content_id] = content_package
            total_size += content_package["size_bytes"]
        
        # Create offline session
        session = OfflineSession(
            session_id=str(uuid.uuid4()),
            user_id=user_id,
            device_id=device_id,
            started_at=datetime.utcnow(),
            accessed_content=list(packaged_content.keys())
        )
        
        return {
            "session": session,
            "content": packaged_content,
            "total_size_mb": total_size / (1024 * 1024),
            "expires_at": datetime.utcnow() + timedelta(days=capabilities.content_retention_days)
        }
    
    async def queue_offline_action(
        self, 
        user_id: str, 
        device_id: str,
        action_type: str,
        entity_type: str,
        entity_id: str,
        action_data: Dict[str, Any],
        previous_state: Optional[Dict[str, Any]] = None
    ) -> OfflineAction:
        """Queue an action performed while offline for later synchronization."""
        
        action = OfflineAction(
            action_id=str(uuid.uuid4()),
            user_id=user_id,
            action_type=action_type,
            entity_type=entity_type,
            entity_id=entity_id,
            action_data=action_data,
            previous_state=previous_state,
            created_at_offline=datetime.utcnow(),
            device_id=device_id,
            app_version="1.0.0",  # Should come from client
            sync_status=SyncStatus.PENDING
        )
        
        # Store in local queue (in real implementation, this would be in local storage)
        await self.store_offline_action(action)
        
        return action
    
    async def smart_sync(
        self, 
        user_id: str, 
        device_id: str,
        sync_type: str = "incremental",
        force_sync: bool = False
    ) -> SmartSync:
        """Perform intelligent synchronization with conflict resolution."""
        
        sync_session = SmartSync(
            sync_id=str(uuid.uuid4()),
            user_id=user_id,
            device_id=device_id,
            sync_type=sync_type,
            entities_to_sync=[],
            estimated_duration=300,  # 5 minutes default
            status=SyncStatus.IN_PROGRESS,
            started_at=datetime.utcnow()
        )
        
        try:
            # Phase 1: Get pending offline actions
            pending_actions = await self.get_pending_offline_actions(user_id, device_id)
            
            # Phase 2: Prioritize actions based on type and dependencies
            prioritized_actions = await self.prioritize_sync_actions(pending_actions)
            
            # Phase 3: Detect conflicts
            conflicts = await self.detect_sync_conflicts(prioritized_actions)
            
            # Phase 4: Resolve conflicts
            if conflicts:
                resolved_conflicts = await self.resolve_conflicts(conflicts, user_id)
                sync_session.conflicts_detected = len(conflicts)
            
            # Phase 5: Apply actions to server
            sync_results = await self.apply_offline_actions(prioritized_actions, sync_session)
            
            # Phase 6: Update sync status
            sync_session.synced_actions = sync_results["success_count"]
            sync_session.failed_actions = sync_results["failed_count"]
            sync_session.status = SyncStatus.COMPLETED if sync_results["failed_count"] == 0 else SyncStatus.FAILED
            sync_session.completed_at = datetime.utcnow()
            sync_session.progress_percentage = 100.0
            
            # Phase 7: Clean up successfully synced actions
            await self.cleanup_synced_actions(user_id, device_id)
            
        except Exception as e:
            sync_session.status = SyncStatus.FAILED
            sync_session.completed_at = datetime.utcnow()
            # Log error for debugging
        
        return sync_session
    
    async def create_offline_workspace(
        self, 
        user_id: str, 
        title: str,
        initial_content: Dict[str, Any] = None
    ) -> OfflineWorkspace:
        """Create a new offline workspace for creative work."""
        
        workspace = OfflineWorkspace(
            workspace_id=str(uuid.uuid4()),
            user_id=user_id,
            title=title,
            sketches=initial_content.get("sketches", []) if initial_content else [],
            notes=initial_content.get("notes", []) if initial_content else [],
            reference_images=initial_content.get("references", []) if initial_content else [],
            work_in_progress={},
            last_modified_offline=datetime.utcnow(),
            created_at=datetime.utcnow()
        )
        
        return workspace
    
    async def add_to_offline_queue(
        self, 
        user_id: str, 
        operation_type: str,
        items: List[Dict[str, Any]],
        priority: int = 5
    ) -> OfflineQueue:
        """Add items to offline processing queue for when online."""
        
        queue = OfflineQueue(
            queue_id=str(uuid.uuid4()),
            user_id=user_id,
            operation_type=operation_type,
            items=items,
            priority=priority,
            created_at=datetime.utcnow()
        )
        
        return queue
    
    async def process_offline_queues(
        self, 
        user_id: str,
        operation_types: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """Process offline queues when connectivity is available."""
        
        # Get all pending queues for user
        queues = await self.get_pending_offline_queues(user_id, operation_types)
        
        results = []
        
        for queue in queues:
            try:
                queue.status = SyncStatus.IN_PROGRESS
                queue.processing_started = datetime.utcnow()
                
                # Process based on operation type
                if queue.operation_type == "ai_analysis":
                    result = await self.process_ai_analysis_queue(queue)
                elif queue.operation_type == "image_processing":
                    result = await self.process_image_processing_queue(queue)
                elif queue.operation_type == "content_sync":
                    result = await self.process_content_sync_queue(queue)
                else:
                    result = {"status": "unsupported_operation"}
                
                queue.status = SyncStatus.COMPLETED
                queue.processed_items = result.get("processed", [])
                queue.failed_items = result.get("failed", [])
                
                results.append({
                    "queue_id": queue.queue_id,
                    "operation_type": queue.operation_type,
                    "result": result
                })
                
            except Exception as e:
                queue.status = SyncStatus.FAILED
                results.append({
                    "queue_id": queue.queue_id,
                    "operation_type": queue.operation_type,
                    "error": str(e)
                })
        
        return results
    
    async def get_offline_analytics(
        self, 
        user_id: str, 
        period: str = "month"
    ) -> OfflineAnalytics:
        """Generate analytics about offline usage patterns."""
        
        # Calculate date range
        end_date = datetime.utcnow()
        if period == "week":
            start_date = end_date - timedelta(weeks=1)
        else:  # month
            start_date = end_date - timedelta(days=30)
        
        # Get offline sessions in period
        sessions = await self.get_offline_sessions_in_period(user_id, start_date, end_date)
        
        # Calculate metrics
        total_offline_time = sum([
            (s.ended_at - s.started_at).total_seconds() / 60 
            for s in sessions if s.ended_at
        ], 0)
        
        # Get sync performance data
        sync_sessions = await self.get_sync_sessions_in_period(user_id, start_date, end_date)
        
        successful_syncs = [s for s in sync_sessions if s.status == SyncStatus.COMPLETED]
        success_rate = len(successful_syncs) / max(len(sync_sessions), 1) * 100
        
        avg_sync_duration = sum([
            (s.completed_at - s.started_at).total_seconds()
            for s in successful_syncs if s.completed_at and s.started_at
        ], 0) / max(len(successful_syncs), 1)
        
        analytics = OfflineAnalytics(
            user_id=user_id,
            analytics_period=period,
            total_offline_time_minutes=int(total_offline_time),
            offline_sessions_count=len(sessions),
            avg_session_length_minutes=total_offline_time / max(len(sessions), 1),
            lessons_completed_offline=sum([s.activities_completed for s in sessions]),
            quizzes_taken_offline=0,  # Would calculate from session data
            artworks_created_offline=sum([len(s.created_content) for s in sessions]),
            successful_sync_rate=success_rate,
            avg_sync_duration_seconds=avg_sync_duration,
            conflicts_resolved=sum([s.conflicts_detected for s in sync_sessions]),
            avg_storage_usage_mb=250.0,  # Would calculate from actual usage
            cache_hit_rate=85.0,  # Would calculate from cache statistics
            data_compression_ratio=0.65,  # Would calculate from compression stats
            generated_at=datetime.utcnow()
        )
        
        return analytics
    
    # Helper methods for internal operations
    
    async def determine_offline_content(
        self, 
        user_id: str, 
        capabilities: OfflineCapabilities,
        content_types: Optional[List[str]] = None,
        priority_content: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Determine what content should be available offline."""
        
        content_to_include = {}
        
        # Always include priority content
        if priority_content:
            for content_id in priority_content:
                content_to_include[content_id] = {"priority": 10, "type": "manual"}
        
        # Include based on user preferences and capabilities
        if OfflineCapability.LESSONS in capabilities.enabled_capabilities:
            # Get user's current and next lessons
            user_lessons = await self.get_user_lesson_recommendations(user_id, limit=10)
            for lesson in user_lessons:
                content_to_include[lesson["id"]] = {"priority": 8, "type": "lesson"}
        
        if OfflineCapability.QUIZZES in capabilities.enabled_capabilities:
            # Get related quizzes
            user_quizzes = await self.get_user_quiz_recommendations(user_id, limit=5)
            for quiz in user_quizzes:
                content_to_include[quiz["id"]] = {"priority": 6, "type": "quiz"}
        
        # Include recently accessed content
        recent_content = await self.get_recently_accessed_content(user_id, days=7)
        for content in recent_content:
            if content["id"] not in content_to_include:
                content_to_include[content["id"]] = {"priority": 4, "type": content["type"]}
        
        return content_to_include
    
    async def package_content_with_dependencies(
        self, 
        content_id: str, 
        content_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Package content with all its dependencies."""
        
        # Get base content
        content = await self.get_content_by_id(content_id)
        if not content:
            raise ValueError(f"Content {content_id} not found")
        
        # Calculate dependencies (images, videos, linked resources)
        dependencies = await self.resolve_content_dependencies(content)
        
        # Calculate total size
        total_size = content.get("size_bytes", 0)
        dependency_data = []
        
        for dep_id in dependencies:
            dep_content = await self.get_content_by_id(dep_id)
            if dep_content:
                dependency_data.append(dep_content)
                total_size += dep_content.get("size_bytes", 0)
        
        # Create content package
        package = {
            "content_id": content_id,
            "content_type": content_info["type"],
            "main_content": content,
            "dependencies": dependency_data,
            "size_bytes": total_size,
            "version": content.get("version", "1.0"),
            "checksum": self.calculate_content_checksum(content),
            "packaged_at": datetime.utcnow()
        }
        
        return package
    
    async def detect_sync_conflicts(
        self, 
        actions: List[OfflineAction]
    ) -> List[SyncConflict]:
        """Detect conflicts between offline actions and server state."""
        
        conflicts = []
        
        for action in actions:
            # Get current server state
            server_state = await self.get_server_entity_state(
                action.entity_type, action.entity_id
            )
            
            if not server_state:
                continue  # No conflict if entity doesn't exist on server
            
            # Check for conflicts based on timestamps and content
            local_timestamp = action.created_at_offline
            server_timestamp = server_state.get("last_modified")
            
            if server_timestamp and server_timestamp > local_timestamp:
                # Potential conflict - server was modified after offline action
                conflict = SyncConflict(
                    conflict_id=str(uuid.uuid4()),
                    entity_type=action.entity_type,
                    entity_id=action.entity_id,
                    local_version=action.action_data,
                    server_version=server_state,
                    local_timestamp=local_timestamp,
                    server_timestamp=server_timestamp
                )
                conflicts.append(conflict)
        
        return conflicts
    
    async def resolve_conflicts(
        self, 
        conflicts: List[SyncConflict], 
        user_id: str
    ) -> List[SyncConflict]:
        """Resolve sync conflicts using configured strategy."""
        
        resolved_conflicts = []
        
        # Get user's conflict resolution preferences
        capabilities = await self.get_offline_capabilities(user_id, "default")
        default_strategy = capabilities.conflict_resolution_preference
        
        for conflict in conflicts:
            resolution_strategy = await self.determine_conflict_strategy(
                conflict, default_strategy
            )
            
            if resolution_strategy == ConflictResolution.SERVER_WINS:
                conflict.resolved_version = conflict.server_version
            elif resolution_strategy == ConflictResolution.CLIENT_WINS:
                conflict.resolved_version = conflict.local_version
            elif resolution_strategy == ConflictResolution.MERGE:
                conflict.resolved_version = await self.merge_conflict_versions(conflict)
            else:  # MANUAL
                # Flag for manual resolution by user
                conflict.resolution_strategy = ConflictResolution.MANUAL
                resolved_conflicts.append(conflict)
                continue
            
            conflict.resolution_strategy = resolution_strategy
            conflict.resolved_at = datetime.utcnow()
            conflict.resolved_by = "auto"
            resolved_conflicts.append(conflict)
        
        return resolved_conflicts
    
    async def apply_offline_actions(
        self, 
        actions: List[OfflineAction], 
        sync_session: SmartSync
    ) -> Dict[str, int]:
        """Apply offline actions to server with transaction safety."""
        
        success_count = 0
        failed_count = 0
        
        for i, action in enumerate(actions):
            try:
                # Update progress
                sync_session.progress_percentage = (i / len(actions)) * 100
                sync_session.current_operation = f"Syncing {action.entity_type} {action.entity_id}"
                
                # Apply action based on type
                if action.action_type == "create":
                    await self.apply_create_action(action)
                elif action.action_type == "update":
                    await self.apply_update_action(action)
                elif action.action_type == "delete":
                    await self.apply_delete_action(action)
                elif action.action_type == "complete":
                    await self.apply_completion_action(action)
                
                # Mark as synced
                action.sync_status = SyncStatus.COMPLETED
                success_count += 1
                
            except Exception as e:
                action.sync_status = SyncStatus.FAILED
                action.sync_error = str(e)
                action.sync_attempts += 1
                failed_count += 1
        
        return {
            "success_count": success_count,
            "failed_count": failed_count
        }
    
    # Placeholder methods for actual implementation
    
    async def get_offline_capabilities(self, user_id: str, device_id: str) -> OfflineCapabilities:
        """Get user's offline capabilities configuration."""
        # This would retrieve from database or create default
        return OfflineCapabilities(
            user_id=user_id,
            device_id=device_id,
            enabled_capabilities=[
                OfflineCapability.LESSONS,
                OfflineCapability.PROGRESS_TRACKING,
                OfflineCapability.ARTWORK_CREATION
            ],
            last_updated=datetime.utcnow()
        )
    
    async def store_offline_action(self, action: OfflineAction):
        """Store offline action in local storage/database."""
        pass  # Implementation would store in appropriate storage
    
    async def get_pending_offline_actions(self, user_id: str, device_id: str) -> List[OfflineAction]:
        """Get all pending offline actions for sync."""
        return []  # Implementation would retrieve from storage
    
    async def prioritize_sync_actions(self, actions: List[OfflineAction]) -> List[OfflineAction]:
        """Prioritize actions for synchronization."""
        # Sort by importance: creates first, then updates, then deletes
        priority_map = {"create": 3, "update": 2, "delete": 1, "complete": 2}
        return sorted(actions, key=lambda a: priority_map.get(a.action_type, 0), reverse=True)
    
    # Additional placeholder methods...
    
    async def get_user_lesson_recommendations(self, user_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        return []
    
    async def get_user_quiz_recommendations(self, user_id: str, limit: int = 5) -> List[Dict[str, Any]]:
        return []
    
    async def get_recently_accessed_content(self, user_id: str, days: int = 7) -> List[Dict[str, Any]]:
        return []
    
    async def get_content_by_id(self, content_id: str) -> Optional[Dict[str, Any]]:
        return None
    
    async def resolve_content_dependencies(self, content: Dict[str, Any]) -> List[str]:
        return []
    
    def calculate_content_checksum(self, content: Dict[str, Any]) -> str:
        content_str = json.dumps(content, sort_keys=True)
        return hashlib.md5(content_str.encode()).hexdigest()
    
    async def get_server_entity_state(self, entity_type: str, entity_id: str) -> Optional[Dict[str, Any]]:
        return None
    
    async def determine_conflict_strategy(
        self, 
        conflict: SyncConflict, 
        default: ConflictResolution
    ) -> ConflictResolution:
        return default
    
    async def merge_conflict_versions(self, conflict: SyncConflict) -> Dict[str, Any]:
        # Simple merge - in practice would be more sophisticated
        merged = conflict.server_version.copy()
        merged.update(conflict.local_version)
        return merged
    
    async def apply_create_action(self, action: OfflineAction):
        pass  # Implementation would create entity on server
    
    async def apply_update_action(self, action: OfflineAction):
        pass  # Implementation would update entity on server
    
    async def apply_delete_action(self, action: OfflineAction):
        pass  # Implementation would delete entity on server
    
    async def apply_completion_action(self, action: OfflineAction):
        pass  # Implementation would mark completion on server
    
    async def cleanup_synced_actions(self, user_id: str, device_id: str):
        pass  # Implementation would clean up successfully synced actions
    
    async def get_pending_offline_queues(
        self, 
        user_id: str, 
        operation_types: Optional[List[str]] = None
    ) -> List[OfflineQueue]:
        return []
    
    async def process_ai_analysis_queue(self, queue: OfflineQueue) -> Dict[str, Any]:
        return {"processed": [], "failed": []}
    
    async def process_image_processing_queue(self, queue: OfflineQueue) -> Dict[str, Any]:
        return {"processed": [], "failed": []}
    
    async def process_content_sync_queue(self, queue: OfflineQueue) -> Dict[str, Any]:
        return {"processed": [], "failed": []}
    
    async def get_offline_sessions_in_period(
        self, 
        user_id: str, 
        start_date: datetime, 
        end_date: datetime
    ) -> List[OfflineSession]:
        return []
    
    async def get_sync_sessions_in_period(
        self, 
        user_id: str, 
        start_date: datetime, 
        end_date: datetime
    ) -> List[SmartSync]:
        return []
