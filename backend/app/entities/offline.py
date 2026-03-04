from pydantic import BaseModel
from datetime import datetime
from typing import List, Dict, Any, Optional, Union
from enum import Enum

class SyncStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CONFLICT = "conflict"

class OfflineAction(str, Enum):
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    COMPLETE = "complete"
    INTERACT = "interact"

class ConflictResolution(str, Enum):
    SERVER_WINS = "server_wins"
    CLIENT_WINS = "client_wins"
    MERGE = "merge"
    MANUAL = "manual"

class OfflineCapability(str, Enum):
    LESSONS = "lessons"
    QUIZZES = "quizzes"
    PROGRESS_TRACKING = "progress_tracking"
    ARTWORK_CREATION = "artwork_creation"
    AI_ANALYSIS_QUEUE = "ai_analysis_queue"
    NOTES_SKETCHES = "notes_sketches"

class OfflineContent(BaseModel):
    content_id: str
    content_type: str  # lesson, quiz, resource, etc.
    data: Dict[str, Any]
    metadata: Dict[str, Any]
    
    # Offline management
    downloaded_at: datetime
    expires_at: Optional[datetime] = None
    size_bytes: int
    dependencies: List[str] = []  # Other content IDs this depends on
    
    # Version control
    version: str
    last_modified: datetime
    checksum: str

class OfflineAction(BaseModel):
    action_id: str
    user_id: str
    action_type: OfflineAction
    entity_type: str  # lesson_progress, quiz_result, artwork, etc.
    entity_id: str
    
    # Action data
    action_data: Dict[str, Any]
    previous_state: Optional[Dict[str, Any]] = None
    
    # Metadata
    created_at_offline: datetime
    device_id: str
    app_version: str
    
    # Sync management
    sync_status: SyncStatus = SyncStatus.PENDING
    sync_attempts: int = 0
    last_sync_attempt: Optional[datetime] = None
    sync_error: Optional[str] = None

class SyncConflict(BaseModel):
    conflict_id: str
    entity_type: str
    entity_id: str
    
    # Conflict data
    local_version: Dict[str, Any]
    server_version: Dict[str, Any]
    local_timestamp: datetime
    server_timestamp: datetime
    
    # Resolution
    resolution_strategy: Optional[ConflictResolution] = None
    resolved_version: Optional[Dict[str, Any]] = None
    resolved_at: Optional[datetime] = None
    resolved_by: Optional[str] = None  # user_id or "auto"

class OfflineSession(BaseModel):
    session_id: str
    user_id: str
    device_id: str
    
    # Session details
    started_at: datetime
    ended_at: Optional[datetime] = None
    total_actions: int = 0
    synced_actions: int = 0
    
    # Content used offline
    accessed_content: List[str] = []  # content_ids
    created_content: List[str] = []  # new content created offline
    
    # Performance metrics
    data_usage_mb: float = 0.0
    activities_completed: int = 0

class OfflineCapabilities(BaseModel):
    user_id: str
    device_id: str
    
    # Storage management
    storage_quota_mb: int = 500  # Default 500MB
    storage_used_mb: float = 0.0
    content_retention_days: int = 30
    
    # Capability settings
    enabled_capabilities: List[OfflineCapability]
    auto_download_lessons: bool = True
    auto_download_resources: bool = False
    
    # Sync preferences
    sync_on_wifi_only: bool = True
    sync_frequency_minutes: int = 30
    conflict_resolution_preference: ConflictResolution = ConflictResolution.MERGE
    
    # Quality settings
    video_quality: str = "medium"  # low, medium, high
    image_compression: str = "optimal"  # minimal, optimal, aggressive
    
    last_updated: datetime

class SmartSync(BaseModel):
    """Intelligent sync orchestration model."""
    sync_id: str
    user_id: str
    device_id: str
    
    # Sync scope
    sync_type: str  # full, incremental, priority
    entities_to_sync: List[str]
    estimated_duration: int  # seconds
    
    # Sync progress
    status: SyncStatus
    progress_percentage: float = 0.0
    current_operation: Optional[str] = None
    
    # Results
    synced_actions: int = 0
    failed_actions: int = 0
    conflicts_detected: int = 0
    data_transferred_mb: float = 0.0
    
    # Timing
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    estimated_completion: Optional[datetime] = None

class OfflineAnalytics(BaseModel):
    """Analytics for offline usage patterns."""
    user_id: str
    analytics_period: str  # week, month
    
    # Usage patterns
    total_offline_time_minutes: int
    offline_sessions_count: int
    avg_session_length_minutes: float
    
    # Content consumption
    lessons_completed_offline: int
    quizzes_taken_offline: int
    artworks_created_offline: int
    
    # Sync performance
    successful_sync_rate: float
    avg_sync_duration_seconds: float
    conflicts_resolved: int
    
    # Storage efficiency
    avg_storage_usage_mb: float
    cache_hit_rate: float
    data_compression_ratio: float
    
    generated_at: datetime

class OfflineWorkspace(BaseModel):
    """User's offline workspace for creative work."""
    workspace_id: str
    user_id: str
    title: str
    
    # Workspace content
    sketches: List[Dict[str, Any]] = []
    notes: List[Dict[str, Any]] = []
    reference_images: List[str] = []
    work_in_progress: Dict[str, Any] = {}
    
    # Collaboration
    shared_with: List[str] = []  # user_ids
    collaboration_mode: str = "private"  # private, shared, public
    
    # Sync management
    last_modified_offline: datetime
    sync_status: SyncStatus = SyncStatus.PENDING
    version: int = 1
    
    created_at: datetime

class OfflineQueue(BaseModel):
    """Queue for offline operations that need online processing."""
    queue_id: str
    user_id: str
    operation_type: str  # ai_analysis, image_processing, etc.
    
    # Queue data
    items: List[Dict[str, Any]]
    priority: int = 5  # 1-10, 10 is highest
    
    # Processing
    status: SyncStatus = SyncStatus.PENDING
    processing_started: Optional[datetime] = None
    estimated_completion: Optional[datetime] = None
    
    # Results
    processed_items: List[Dict[str, Any]] = []
    failed_items: List[Dict[str, Any]] = []
    
    created_at: datetime
