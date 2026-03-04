"""
Workflow Controller

REST API endpoints for managing workflows and automation.
"""

from typing import Dict, Any, Optional, List
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
import logging
from uuid import UUID
from datetime import datetime, timedelta

from ..database import get_db
from ..auth.dependencies import get_current_user
from ..entities.models import User
from ..config import settings
from .workflow_manager import WorkflowManager
from .event_system import WorkflowEvent, WorkflowEventType, WorkflowTrigger

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/workflows", tags=["Workflows"])


def get_workflow_manager(db: Session = Depends(get_db)) -> WorkflowManager:
    """Dependency to get workflow manager instance"""
    # Strip /webhook suffix to get the n8n API base URL (used for health/workflow listing)
    webhook_url = settings.n8n_webhook_url  # e.g. https://myinstance.n8n.cloud/webhook
    api_base = webhook_url.rsplit('/webhook', 1)[0] if '/webhook' in webhook_url else webhook_url
    return WorkflowManager(
        db,
        n8n_url=api_base,
        n8n_api_key=settings.n8n_api_key,
        n8n_webhook_url=webhook_url,
    )


@router.get("/status")
async def get_workflow_system_status(
    workflow_manager: WorkflowManager = Depends(get_workflow_manager),
    current_user: User = Depends(get_current_user)
):
    """Get the overall status of the workflow system"""
    
    try:
        status = await workflow_manager.get_workflow_status()
        return {
            "success": True,
            "data": status
        }
    except Exception as e:
        logger.error(f"Error getting workflow status: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get workflow status")


@router.get("/analytics")
async def get_workflow_analytics(
    days: int = 7,
    workflow_manager: WorkflowManager = Depends(get_workflow_manager),
    current_user: User = Depends(get_current_user)
):
    """Get workflow execution analytics"""
    
    if days < 1 or days > 30:
        raise HTTPException(status_code=400, detail="Days parameter must be between 1 and 30")
    
    try:
        analytics = await workflow_manager.get_workflow_analytics(days)
        return {
            "success": True,
            "data": analytics
        }
    except Exception as e:
        logger.error(f"Error getting workflow analytics: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get workflow analytics")


@router.get("/triggers")
async def get_workflow_triggers(
    workflow_manager: WorkflowManager = Depends(get_workflow_manager),
    current_user: User = Depends(get_current_user)
):
    """Get all registered workflow triggers"""
    
    try:
        triggers = workflow_manager.event_system.get_triggers()
        return {
            "success": True,
            "data": [
                {
                    "name": trigger.name,
                    "event_types": list(trigger.event_types),
                    "webhook_url": trigger.webhook_url,
                    "is_active": trigger.is_active,
                    "conditions": trigger.conditions,
                    "description": trigger.description
                }
                for trigger in triggers
            ]
        }
    except Exception as e:
        logger.error(f"Error getting workflow triggers: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get workflow triggers")


@router.patch("/triggers/{trigger_name}/toggle")
async def toggle_workflow_trigger(
    trigger_name: str,
    workflow_manager: WorkflowManager = Depends(get_workflow_manager),
    current_user: User = Depends(get_current_user)
):
    """Toggle a workflow trigger on/off"""
    
    try:
        trigger = workflow_manager.event_system.get_trigger(trigger_name)
        if not trigger:
            raise HTTPException(status_code=404, detail="Workflow trigger not found")
        
        # Toggle the trigger
        trigger.is_active = not trigger.is_active
        
        return {
            "success": True,
            "message": f"Workflow trigger '{trigger_name}' {'activated' if trigger.is_active else 'deactivated'}",
            "data": {
                "trigger_name": trigger_name,
                "is_active": trigger.is_active
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error toggling workflow trigger: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to toggle workflow trigger")


@router.post("/events/test")
async def emit_test_event(
    event_data: Dict[str, Any],
    background_tasks: BackgroundTasks,
    workflow_manager: WorkflowManager = Depends(get_workflow_manager),
    current_user: User = Depends(get_current_user)
):
    """Emit a test workflow event (for testing purposes)"""
    
    try:
        event_type_str = event_data.get("event_type")
        if not event_type_str:
            raise HTTPException(status_code=400, detail="event_type is required")
        
        # Validate event type
        try:
            event_type = WorkflowEventType(event_type_str)
        except ValueError:
            valid_types = [e.value for e in WorkflowEventType]
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid event_type. Valid types: {valid_types}"
            )
        
        # Create test event
        event = WorkflowEvent(
            event_type=event_type,
            user_id=current_user.id,
            data=event_data.get("data", {}),
            metadata={
                "source": "test_api",
                "triggered_by": str(current_user.id)
            }
        )
        
        # Emit event in background
        async def emit_event():
            await workflow_manager.event_system.emit_event(event)
        
        background_tasks.add_task(emit_event)
        
        return {
            "success": True,
            "message": "Test event queued for processing",
            "data": {
                "event_id": event.event_id,
                "event_type": event.event_type,
                "user_id": str(event.user_id)
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error emitting test event: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to emit test event")


@router.post("/simulate/lesson-completion")
async def simulate_lesson_completion(
    lesson_data: Dict[str, Any],
    background_tasks: BackgroundTasks,
    workflow_manager: WorkflowManager = Depends(get_workflow_manager),
    current_user: User = Depends(get_current_user)
):
    """Simulate lesson completion for workflow testing"""
    
    try:
        lesson_id = lesson_data.get("lesson_id", 1)
        completion_data = {
            "completion_status": "completed",
            "score": lesson_data.get("score", 85),
            "time_spent_minutes": lesson_data.get("time_spent_minutes", 45)
        }
        
        # Capture user info before DB session closes
        user_email = current_user.email
        user_name = current_user.name

        # Trigger lesson completion workflow
        async def handle_completion():
            await workflow_manager.handle_lesson_completion(
                user_id=current_user.id,
                lesson_id=lesson_id,
                completion_data=completion_data,
                user_email=user_email,
                user_name=user_name
            )
        
        background_tasks.add_task(handle_completion)
        
        return {
            "success": True,
            "message": "Lesson completion workflow triggered",
            "data": {
                "user_id": str(current_user.id),
                "lesson_id": lesson_id,
                "completion_data": completion_data
            }
        }
    except Exception as e:
        logger.error(f"Error simulating lesson completion: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to simulate lesson completion")


@router.post("/simulate/quiz-completion")
async def simulate_quiz_completion(
    quiz_data: Dict[str, Any],
    background_tasks: BackgroundTasks,
    workflow_manager: WorkflowManager = Depends(get_workflow_manager),
    current_user: User = Depends(get_current_user)
):
    """Simulate quiz completion for workflow testing"""
    
    try:
        quiz_id = quiz_data.get("quiz_id", 1)
        quiz_results = {
            "score_percentage": quiz_data.get("score", 75),
            "total_questions": quiz_data.get("total_questions", 10),
            "correct_answers": quiz_data.get("correct_answers", 7),
            "time_taken_minutes": quiz_data.get("time_taken_minutes", 15),
            "areas_to_review": quiz_data.get("areas_to_review", [])
        }
        
        # Capture user info before DB session closes
        user_email = current_user.email
        user_name = current_user.name

        # Trigger quiz completion workflow
        async def handle_completion():
            await workflow_manager.handle_quiz_completion(
                user_id=current_user.id,
                quiz_id=quiz_id,
                quiz_results=quiz_results,
                user_email=user_email,
                user_name=user_name
            )
        
        background_tasks.add_task(handle_completion)
        
        return {
            "success": True,
            "message": "Quiz completion workflow triggered",
            "data": {
                "user_id": str(current_user.id),
                "quiz_id": quiz_id,
                "quiz_results": quiz_results
            }
        }
    except Exception as e:
        logger.error(f"Error simulating quiz completion: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to simulate quiz completion")


@router.post("/simulate/low-performance")
async def simulate_low_performance(
    background_tasks: BackgroundTasks,
    workflow_manager: WorkflowManager = Depends(get_workflow_manager),
    current_user: User = Depends(get_current_user)
):
    """Simulate low performance intervention workflow"""
    
    try:
        # Capture user info before DB session closes
        user_email = current_user.email
        user_name = current_user.name

        performance_data = {
            "average_score": 42,
            "recent_scores": [38, 45, 42, 50, 35],
            "struggling_areas": ["perspective", "shading", "proportions"]
        }

        async def handle_low_perf():
            await workflow_manager.handle_low_performance_detection(
                user_id=current_user.id,
                performance_data=performance_data,
                user_email=user_email,
                user_name=user_name
            )
        
        background_tasks.add_task(handle_low_perf)
        
        return {
            "success": True,
            "message": "Low performance intervention workflow triggered",
            "data": {
                "user_id": str(current_user.id),
                "triggered_at": datetime.utcnow().isoformat()
            }
        }
    except Exception as e:
        logger.error(f"Error simulating low performance: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to simulate low performance")


@router.post("/simulate/daily-reminder")
async def simulate_daily_reminder(
    background_tasks: BackgroundTasks,
    workflow_manager: WorkflowManager = Depends(get_workflow_manager),
    current_user: User = Depends(get_current_user)
):
    """Simulate daily practice reminder workflow"""
    
    try:
        # Capture user info before DB session closes
        user_email = current_user.email
        user_name = current_user.name

        # Trigger daily reminder workflow
        async def handle_reminder():
            await workflow_manager.handle_daily_practice_reminder(current_user.id, user_email=user_email, user_name=user_name)
        
        background_tasks.add_task(handle_reminder)
        
        return {
            "success": True,
            "message": "Daily practice reminder workflow triggered",
            "data": {
                "user_id": str(current_user.id),
                "triggered_at": datetime.utcnow().isoformat()
            }
        }
    except Exception as e:
        logger.error(f"Error simulating daily reminder: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to simulate daily reminder")


@router.post("/simulate/weekly-summary")
async def simulate_weekly_summary(
    background_tasks: BackgroundTasks,
    workflow_manager: WorkflowManager = Depends(get_workflow_manager),
    current_user: User = Depends(get_current_user)
):
    """Simulate weekly progress summary workflow"""
    
    try:
        # Capture user info before DB session closes
        user_email = current_user.email
        user_name = current_user.name

        # Trigger weekly summary workflow
        async def handle_summary():
            await workflow_manager.handle_weekly_summary_generation(current_user.id, user_email=user_email, user_name=user_name)
        
        background_tasks.add_task(handle_summary)
        
        return {
            "success": True,
            "message": "Weekly progress summary workflow triggered",
            "data": {
                "user_id": str(current_user.id),
                "triggered_at": datetime.utcnow().isoformat()
            }
        }
    except Exception as e:
        logger.error(f"Error simulating weekly summary: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to simulate weekly summary")


@router.get("/n8n/workflows")
async def get_n8n_workflows(
    workflow_manager: WorkflowManager = Depends(get_workflow_manager),
    current_user: User = Depends(get_current_user)
):
    """Get all n8n workflows"""
    
    try:
        workflows = await workflow_manager.n8n_client.get_workflows()
        return {
            "success": True,
            "data": {
                "workflows": workflows,
                "count": len(workflows)
            }
        }
    except Exception as e:
        logger.error(f"Error getting n8n workflows: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get n8n workflows")


@router.get("/n8n/executions")
async def get_n8n_executions(
    workflow_id: Optional[str] = None,
    limit: int = 20,
    workflow_manager: WorkflowManager = Depends(get_workflow_manager),
    current_user: User = Depends(get_current_user)
):
    """Get n8n workflow execution history"""
    
    if limit < 1 or limit > 100:
        raise HTTPException(status_code=400, detail="Limit must be between 1 and 100")
    
    try:
        executions = await workflow_manager.n8n_client.get_executions(workflow_id, limit)
        return {
            "success": True,
            "data": {
                "executions": [
                    {
                        "id": exec.id,
                        "workflow_id": exec.workflow_id,
                        "status": exec.status,
                        "started_at": exec.started_at.isoformat(),
                        "finished_at": exec.finished_at.isoformat() if exec.finished_at else None,
                        "execution_time_ms": exec.execution_time_ms,
                        "error_message": exec.error_message
                    }
                    for exec in executions
                ],
                "count": len(executions)
            }
        }
    except Exception as e:
        logger.error(f"Error getting n8n executions: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get n8n executions")


@router.post("/n8n/workflows/{workflow_id}/execute")
async def execute_n8n_workflow(
    workflow_id: str,
    execution_data: Optional[Dict[str, Any]] = None,
    workflow_manager: WorkflowManager = Depends(get_workflow_manager),
    current_user: User = Depends(get_current_user)
):
    """Execute an n8n workflow manually"""
    
    try:
        execution_id = await workflow_manager.n8n_client.execute_workflow(
            workflow_id, execution_data
        )
        
        if execution_id:
            return {
                "success": True,
                "message": "Workflow executed successfully",
                "data": {
                    "workflow_id": workflow_id,
                    "execution_id": execution_id
                }
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to execute workflow")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error executing n8n workflow: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to execute workflow")


@router.patch("/n8n/workflows/{workflow_id}/activate")
async def activate_n8n_workflow(
    workflow_id: str,
    workflow_manager: WorkflowManager = Depends(get_workflow_manager),
    current_user: User = Depends(get_current_user)
):
    """Activate an n8n workflow"""
    
    try:
        success = await workflow_manager.n8n_client.activate_workflow(workflow_id)
        
        if success:
            return {
                "success": True,
                "message": f"Workflow {workflow_id} activated successfully"
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to activate workflow")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error activating n8n workflow: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to activate workflow")


@router.patch("/n8n/workflows/{workflow_id}/deactivate")
async def deactivate_n8n_workflow(
    workflow_id: str,
    workflow_manager: WorkflowManager = Depends(get_workflow_manager),
    current_user: User = Depends(get_current_user)
):
    """Deactivate an n8n workflow"""
    
    try:
        success = await workflow_manager.n8n_client.deactivate_workflow(workflow_id)
        
        if success:
            return {
                "success": True,
                "message": f"Workflow {workflow_id} deactivated successfully"
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to deactivate workflow")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deactivating n8n workflow: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to deactivate workflow")
