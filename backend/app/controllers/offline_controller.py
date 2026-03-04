from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional

from app.database import get_db
from app.auth.dependencies import get_current_user
from app.entities.offline import (
    OfflineContent, OfflineAction, SyncConflict, OfflineSession,
    OfflineCapabilities, SmartSync, OfflineAnalytics, OfflineWorkspace,
    OfflineQueue, SyncStatus, ConflictResolution, OfflineCapability
)
from app.services.offline_service import OfflineService

router = APIRouter(prefix="/api/offline", tags=["Advanced Offline"])
security = HTTPBearer()

def get_offline_service(db: Session = Depends(get_db)) -> OfflineService:
    """Dependency to get offline service."""
    return OfflineService(db)

@router.post("/prepare")
async def prepare_offline_content(
    device_id: str,
    content_types: Optional[List[str]] = None,
    priority_content: Optional[List[str]] = None,
    current_user = Depends(get_current_user),
    service: OfflineService = Depends(get_offline_service)
):
    """
    Prepare and package content for offline use.
    
    - **device_id**: Unique identifier for the user's device
    - **content_types**: Types of content to include (lessons, quizzes, etc.)
    - **priority_content**: Specific content IDs to prioritize for offline access
    
    Returns packaged content optimized for the user's storage constraints and preferences.
    """
    try:
        offline_package = await service.prepare_offline_content(
            user_id=current_user["user_id"],
            device_id=device_id,
            content_types=content_types,
            priority_content=priority_content
        )
        
        return {
            "session_id": offline_package["session"].session_id,
            "content_count": len(offline_package["content"]),
            "total_size_mb": offline_package["total_size_mb"],
            "expires_at": offline_package["expires_at"],
            "content_manifest": list(offline_package["content"].keys())
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to prepare offline content: {str(e)}"
        )

@router.post("/actions/queue")
async def queue_offline_action(
    device_id: str,
    action_type: str,
    entity_type: str,
    entity_id: str,
    action_data: Dict[str, Any],
    previous_state: Optional[Dict[str, Any]] = None,
    current_user = Depends(get_current_user),
    service: OfflineService = Depends(get_offline_service)
):
    """
    Queue an action performed while offline for later synchronization.
    
    - **action_type**: Type of action (create, update, delete, complete)
    - **entity_type**: Type of entity affected (lesson_progress, quiz_result, etc.)
    - **entity_id**: Unique identifier of the affected entity
    - **action_data**: Data for the action
    - **previous_state**: Previous state of entity (for conflict resolution)
    """
    try:
        action = await service.queue_offline_action(
            user_id=current_user["user_id"],
            device_id=device_id,
            action_type=action_type,
            entity_type=entity_type,
            entity_id=entity_id,
            action_data=action_data,
            previous_state=previous_state
        )
        
        return {
            "action_id": action.action_id,
            "status": action.sync_status,
            "queued_at": action.created_at_offline
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to queue offline action: {str(e)}"
        )

@router.post("/sync")
async def smart_sync(
    device_id: str,
    sync_type: str = "incremental",
    force_sync: bool = False,
    background_tasks: BackgroundTasks = None,
    current_user = Depends(get_current_user),
    service: OfflineService = Depends(get_offline_service)
):
    """
    Perform intelligent synchronization with conflict resolution.
    
    - **sync_type**: Type of sync (incremental, full, priority)
    - **force_sync**: Force sync even if recent sync occurred
    
    Returns sync session details and handles conflicts automatically.
    """
    try:
        sync_session = await service.smart_sync(
            user_id=current_user["user_id"],
            device_id=device_id,
            sync_type=sync_type,
            force_sync=force_sync
        )
        
        return {
            "sync_id": sync_session.sync_id,
            "status": sync_session.status,
            "synced_actions": sync_session.synced_actions,
            "failed_actions": sync_session.failed_actions,
            "conflicts_detected": sync_session.conflicts_detected,
            "duration_seconds": (
                (sync_session.completed_at - sync_session.started_at).total_seconds() 
                if sync_session.completed_at and sync_session.started_at else None
            )
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to perform sync: {str(e)}"
        )

@router.get("/sync/status/{sync_id}")
async def get_sync_status(
    sync_id: str,
    current_user = Depends(get_current_user)
):
    """Get the status of an ongoing or completed sync operation."""
    try:
        # In real implementation, would retrieve sync session from storage
        return {
            "sync_id": sync_id,
            "status": "completed",
            "progress_percentage": 100.0,
            "message": "Sync completed successfully"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get sync status: {str(e)}"
        )

@router.post("/workspace")
async def create_offline_workspace(
    title: str,
    initial_content: Optional[Dict[str, Any]] = None,
    current_user = Depends(get_current_user),
    service: OfflineService = Depends(get_offline_service)
):
    """
    Create a new offline workspace for creative work.
    
    - **title**: Name for the workspace
    - **initial_content**: Optional initial content (sketches, notes, references)
    
    Returns workspace that can be used for offline creative activities.
    """
    try:
        workspace = await service.create_offline_workspace(
            user_id=current_user["user_id"],
            title=title,
            initial_content=initial_content
        )
        
        return {
            "workspace_id": workspace.workspace_id,
            "title": workspace.title,
            "created_at": workspace.created_at,
            "content_summary": {
                "sketches": len(workspace.sketches),
                "notes": len(workspace.notes),
                "references": len(workspace.reference_images)
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create offline workspace: {str(e)}"
        )

@router.post("/queue/{operation_type}")
async def add_to_offline_queue(
    operation_type: str,
    items: List[Dict[str, Any]],
    priority: int = 5,
    current_user = Depends(get_current_user),
    service: OfflineService = Depends(get_offline_service)
):
    """
    Add items to offline processing queue for when connectivity is available.
    
    - **operation_type**: Type of operation (ai_analysis, image_processing, etc.)
    - **items**: Items to process when online
    - **priority**: Processing priority (1-10, higher is more urgent)
    
    Useful for queuing AI analysis, complex processing, or uploads.
    """
    try:
        queue = await service.add_to_offline_queue(
            user_id=current_user["user_id"],
            operation_type=operation_type,
            items=items,
            priority=priority
        )
        
        return {
            "queue_id": queue.queue_id,
            "operation_type": queue.operation_type,
            "item_count": len(queue.items),
            "priority": queue.priority,
            "created_at": queue.created_at
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to add to offline queue: {str(e)}"
        )

@router.post("/queue/process")
async def process_offline_queues(
    operation_types: Optional[List[str]] = None,
    background_tasks: BackgroundTasks = None,
    current_user = Depends(get_current_user),
    service: OfflineService = Depends(get_offline_service)
):
    """
    Process offline queues when connectivity is available.
    
    - **operation_types**: Specific operation types to process (optional)
    
    Processes queued operations like AI analysis, uploads, etc.
    """
    try:
        results = await service.process_offline_queues(
            user_id=current_user["user_id"],
            operation_types=operation_types
        )
        
        return {
            "processed_queues": len(results),
            "results": results,
            "processed_at": datetime.utcnow()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process offline queues: {str(e)}"
        )

@router.get("/analytics", response_model=OfflineAnalytics)
async def get_offline_analytics(
    period: str = Query("month", regex="^(week|month)$"),
    current_user = Depends(get_current_user),
    service: OfflineService = Depends(get_offline_service)
):
    """
    Get analytics about offline usage patterns and sync performance.
    
    - **period**: Analytics period (week or month)
    
    Returns comprehensive metrics about offline learning effectiveness.
    """
    try:
        analytics = await service.get_offline_analytics(
            user_id=current_user["user_id"],
            period=period
        )
        
        return analytics
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate offline analytics: {str(e)}"
        )

@router.get("/capabilities", response_model=OfflineCapabilities)
async def get_offline_capabilities(
    device_id: str,
    current_user = Depends(get_current_user),
    service: OfflineService = Depends(get_offline_service)
):
    """
    Get current offline capabilities configuration for device.
    
    Returns user's offline preferences, storage limits, and enabled features.
    """
    try:
        capabilities = await service.get_offline_capabilities(
            user_id=current_user["user_id"],
            device_id=device_id
        )
        
        return capabilities
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get offline capabilities: {str(e)}"
        )

@router.put("/capabilities")
async def update_offline_capabilities(
    device_id: str,
    storage_quota_mb: Optional[int] = None,
    enabled_capabilities: Optional[List[OfflineCapability]] = None,
    auto_download_lessons: Optional[bool] = None,
    sync_on_wifi_only: Optional[bool] = None,
    conflict_resolution_preference: Optional[ConflictResolution] = None,
    current_user = Depends(get_current_user),
    service: OfflineService = Depends(get_offline_service)
):
    """
    Update offline capabilities and preferences.
    
    - **storage_quota_mb**: Maximum storage for offline content
    - **enabled_capabilities**: List of enabled offline features
    - **auto_download_lessons**: Automatically download new lessons
    - **sync_on_wifi_only**: Only sync when on WiFi connection
    - **conflict_resolution_preference**: Default conflict resolution strategy
    """
    try:
        capabilities = await service.get_offline_capabilities(
            user_id=current_user["user_id"],
            device_id=device_id
        )
        
        # Update specified fields
        updates = {}
        if storage_quota_mb is not None:
            updates["storage_quota_mb"] = storage_quota_mb
        if enabled_capabilities is not None:
            updates["enabled_capabilities"] = enabled_capabilities
        if auto_download_lessons is not None:
            updates["auto_download_lessons"] = auto_download_lessons
        if sync_on_wifi_only is not None:
            updates["sync_on_wifi_only"] = sync_on_wifi_only
        if conflict_resolution_preference is not None:
            updates["conflict_resolution_preference"] = conflict_resolution_preference
        
        # Apply updates
        for key, value in updates.items():
            setattr(capabilities, key, value)
        
        capabilities.last_updated = datetime.utcnow()
        
        return {
            "message": "Offline capabilities updated successfully",
            "updated_fields": list(updates.keys()),
            "capabilities": capabilities
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update offline capabilities: {str(e)}"
        )

@router.get("/conflicts")
async def get_sync_conflicts(
    device_id: str,
    status: Optional[SyncStatus] = None,
    current_user = Depends(get_current_user)
):
    """
    Get list of sync conflicts requiring manual resolution.
    
    - **status**: Filter by conflict status
    
    Returns conflicts that need user intervention.
    """
    try:
        # In real implementation, would query database for conflicts
        conflicts = []  # Placeholder
        
        return {
            "conflicts": conflicts,
            "total_count": len(conflicts),
            "unresolved_count": len([c for c in conflicts if c.get("status") == "unresolved"])
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get sync conflicts: {str(e)}"
        )

@router.post("/conflicts/{conflict_id}/resolve")
async def resolve_sync_conflict(
    conflict_id: str,
    resolution_strategy: ConflictResolution,
    custom_resolution: Optional[Dict[str, Any]] = None,
    current_user = Depends(get_current_user)
):
    """
    Manually resolve a sync conflict.
    
    - **resolution_strategy**: How to resolve the conflict
    - **custom_resolution**: Custom merged data (for manual resolution)
    """
    try:
        # In real implementation, would apply conflict resolution
        return {
            "conflict_id": conflict_id,
            "resolution_strategy": resolution_strategy,
            "resolved_at": datetime.utcnow(),
            "resolved_by": current_user["user_id"]
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to resolve conflict: {str(e)}"
        )

@router.get("/storage/usage")
async def get_storage_usage(
    device_id: str,
    current_user = Depends(get_current_user)
):
    """
    Get detailed storage usage information for offline content.
    
    Returns breakdown of storage usage by content type and recommendations.
    """
    try:
        # In real implementation, would calculate actual storage usage
        usage_data = {
            "total_quota_mb": 500,
            "used_mb": 237.5,
            "available_mb": 262.5,
            "usage_percentage": 47.5,
            "breakdown": {
                "lessons": {"mb": 150.3, "count": 45},
                "images": {"mb": 67.2, "count": 234},
                "videos": {"mb": 20.0, "count": 8},
                "cache": {"mb": 12.5, "count": 1}
            },
            "recommendations": [
                "Clear old cached content to free up 12.5 MB",
                "Remove completed lessons from 2+ weeks ago",
                "Compress high-resolution images"
            ]
        }
        
        return usage_data
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get storage usage: {str(e)}"
        )

@router.post("/storage/cleanup")
async def cleanup_storage(
    device_id: str,
    cleanup_types: List[str] = Query(..., description="Types of content to clean up"),
    current_user = Depends(get_current_user)
):
    """
    Clean up offline storage to free space.
    
    - **cleanup_types**: Types of content to remove (cache, old_lessons, etc.)
    
    Intelligently removes content based on usage patterns and age.
    """
    try:
        # In real implementation, would perform cleanup operations
        cleanup_results = {
            "cleaned_types": cleanup_types,
            "space_freed_mb": 45.7,
            "items_removed": 23,
            "cleanup_completed_at": datetime.utcnow()
        }
        
        return cleanup_results
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to cleanup storage: {str(e)}"
        )

# Import datetime for controller
from datetime import datetime
