"""
n8n Client for Workflow Management

Provides interface for managing n8n workflows and instances.
"""

from typing import Dict, Any, Optional, List
import httpx
import logging
from pydantic import BaseModel
from datetime import datetime

logger = logging.getLogger(__name__)


class N8nWorkflowStatus(BaseModel):
    """n8n workflow status information"""
    id: str
    name: str
    active: bool
    nodes: int
    connections: int
    last_execution: Optional[datetime] = None
    success_rate: float = 0.0


class N8nExecution(BaseModel):
    """n8n workflow execution information"""
    id: str
    workflow_id: str
    status: str  # 'success', 'error', 'running', 'waiting'
    started_at: datetime
    finished_at: Optional[datetime] = None
    execution_time_ms: Optional[int] = None
    error_message: Optional[str] = None


class N8nClient:
    """Client for interacting with n8n instance"""
    
    def __init__(self, base_url: str = "http://localhost:5678", api_key: Optional[str] = None):
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.headers = {"Content-Type": "application/json"}
        
        if api_key:
            self.headers["X-N8N-API-KEY"] = api_key
    
    async def health_check(self) -> bool:
        """Check if n8n instance is healthy"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.base_url}/healthz", timeout=10)
                return response.status_code == 200
        except Exception as e:
            logger.error(f"n8n health check failed: {str(e)}")
            return False
    
    async def get_workflows(self) -> List[Dict[str, Any]]:
        """Get all workflows from n8n instance"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/api/v1/workflows",
                    headers=self.headers,
                    timeout=30
                )
                
                if response.status_code == 200:
                    return response.json().get('data', [])
                else:
                    logger.error(f"Failed to get workflows: {response.status_code}")
                    return []
                    
        except Exception as e:
            logger.error(f"Error getting workflows: {str(e)}")
            return []
    
    async def get_workflow_status(self, workflow_id: str) -> Optional[N8nWorkflowStatus]:
        """Get status of a specific workflow"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/api/v1/workflows/{workflow_id}",
                    headers=self.headers,
                    timeout=30
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return N8nWorkflowStatus(
                        id=data.get('id', workflow_id),
                        name=data.get('name', 'Unknown'),
                        active=data.get('active', False),
                        nodes=len(data.get('nodes', [])),
                        connections=len(data.get('connections', {})),
                    )
                else:
                    logger.error(f"Failed to get workflow status: {response.status_code}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error getting workflow status: {str(e)}")
            return None
    
    async def activate_workflow(self, workflow_id: str) -> bool:
        """Activate a workflow"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.patch(
                    f"{self.base_url}/api/v1/workflows/{workflow_id}/activate",
                    headers=self.headers,
                    timeout=30
                )
                
                success = response.status_code == 200
                if success:
                    logger.info(f"Workflow activated: {workflow_id}")
                else:
                    logger.error(f"Failed to activate workflow: {response.status_code}")
                
                return success
                
        except Exception as e:
            logger.error(f"Error activating workflow: {str(e)}")
            return False
    
    async def deactivate_workflow(self, workflow_id: str) -> bool:
        """Deactivate a workflow"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.patch(
                    f"{self.base_url}/api/v1/workflows/{workflow_id}/deactivate",
                    headers=self.headers,
                    timeout=30
                )
                
                success = response.status_code == 200
                if success:
                    logger.info(f"Workflow deactivated: {workflow_id}")
                else:
                    logger.error(f"Failed to deactivate workflow: {response.status_code}")
                
                return success
                
        except Exception as e:
            logger.error(f"Error deactivating workflow: {str(e)}")
            return False
    
    async def execute_workflow(self, workflow_id: str, data: Optional[Dict[str, Any]] = None) -> Optional[str]:
        """Execute a workflow manually"""
        try:
            payload = {"workflowData": data} if data else {}
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/api/v1/workflows/{workflow_id}/execute",
                    headers=self.headers,
                    json=payload,
                    timeout=60
                )
                
                if response.status_code == 201:
                    result = response.json()
                    execution_id = result.get('data', {}).get('executionId')
                    logger.info(f"Workflow executed: {workflow_id} (Execution ID: {execution_id})")
                    return execution_id
                else:
                    logger.error(f"Failed to execute workflow: {response.status_code}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error executing workflow: {str(e)}")
            return None
    
    async def get_executions(self, workflow_id: Optional[str] = None, limit: int = 50) -> List[N8nExecution]:
        """Get workflow execution history"""
        try:
            url = f"{self.base_url}/api/v1/executions"
            params = {"limit": limit}
            
            if workflow_id:
                params["workflowId"] = workflow_id
            
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    url,
                    headers=self.headers,
                    params=params,
                    timeout=30
                )
                
                if response.status_code == 200:
                    executions_data = response.json().get('data', [])
                    executions = []
                    
                    for exec_data in executions_data:
                        executions.append(N8nExecution(
                            id=exec_data.get('id'),
                            workflow_id=exec_data.get('workflowId'),
                            status=exec_data.get('status', 'unknown'),
                            started_at=datetime.fromisoformat(exec_data.get('startedAt')),
                            finished_at=datetime.fromisoformat(exec_data.get('stoppedAt')) if exec_data.get('stoppedAt') else None,
                            execution_time_ms=exec_data.get('executionTime'),
                            error_message=exec_data.get('error')
                        ))
                    
                    return executions
                else:
                    logger.error(f"Failed to get executions: {response.status_code}")
                    return []
                    
        except Exception as e:
            logger.error(f"Error getting executions: {str(e)}")
            return []
    
    async def get_server_info(self) -> Dict[str, Any]:
        """Get n8n server information"""
        try:
            async with httpx.AsyncClient() as client:
                # Try to get version info
                response = await client.get(f"{self.base_url}/api/v1/", timeout=10)
                
                if response.status_code == 200:
                    return {
                        "status": "connected",
                        "url": self.base_url,
                        "api_available": True,
                        "version": "Unknown"  # n8n doesn't provide version in API
                    }
                else:
                    return {
                        "status": "connection_failed",
                        "url": self.base_url,
                        "api_available": False,
                        "error": f"HTTP {response.status_code}"
                    }
                    
        except Exception as e:
            return {
                "status": "connection_error",
                "url": self.base_url,
                "api_available": False,
                "error": str(e)
            }
