"""
MCP Controller

REST API endpoints for Model Context Protocol server functionality.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, Any, List, Optional
from uuid import UUID
import logging

from ..database import get_db
from ..mcp.server import MCPServer
from ..mcp.schemas import MCPRequest, MCPResponse, MCPServerInfo
from ..mcp.tool_registry import tool_registry
from ..auth.dependencies import get_current_user
from ..entities.models import User

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/mcp",
    tags=["MCP (Model Context Protocol)"]
)


@router.get("/info", response_model=Dict[str, Any])
async def get_server_info(db: Session = Depends(get_db)):
    """
    Get MCP server information and capabilities
    
    Returns:
    - Server name, version, and description
    - Available tools count and categories
    - Server capabilities and features
    - Usage statistics
    """
    
    mcp_server = MCPServer(db)
    return mcp_server.get_server_info()


@router.get("/tools", response_model=Dict[str, Any])
async def list_tools(
    category: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    List available MCP tools
    
    Args:
    - category: Optional filter by tool category
    
    Returns:
    - Complete tool definitions with schemas
    - Tool categories and metadata
    - Usage statistics per tool
    """
    
    mcp_server = MCPServer(db)
    tool_definitions = mcp_server.get_tool_list()
    
    # Filter by category if specified
    if category:
        filtered_tools = {
            name: tool_def for name, tool_def in tool_definitions["tools"].items()
            if tool_def["category"] == category
        }
        tool_definitions["tools"] = filtered_tools
    
    # Add usage statistics
    tool_stats = tool_registry.get_tool_stats()
    for tool_name, tool_def in tool_definitions["tools"].items():
        tool_def["usage_stats"] = tool_stats.get(tool_name, {})
    
    return tool_definitions


@router.get("/tools/{tool_name}", response_model=Dict[str, Any])
async def get_tool_info(
    tool_name: str,
    db: Session = Depends(get_db)
):
    """
    Get detailed information about a specific MCP tool
    
    Args:
    - tool_name: Name of the tool to retrieve
    
    Returns:
    - Tool definition with parameters and return schemas
    - Usage statistics and performance metrics
    - Example usage patterns
    """
    
    tool = tool_registry.get_tool(tool_name)
    if not tool:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tool '{tool_name}' not found"
        )
    
    tool_stats = tool_registry.get_tool_stats(tool_name)
    
    return {
        "tool": tool.dict(),
        "usage_stats": tool_stats,
        "examples": _get_tool_examples(tool_name)
    }


@router.post("/execute", response_model=MCPResponse)
async def execute_tool(
    request: MCPRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Execute an MCP tool
    
    Args:
    - request: MCP tool execution request
    
    Returns:
    - Tool execution result or error
    - Execution metrics and timing
    """
    
    # Set user_id from authenticated user if not provided
    if not request.user_id:
        request.user_id = current_user.id
    
    # Validate user has permission to execute tool for this user_id
    if request.user_id != current_user.id:
        # Check if current user has admin privileges or special permissions
        if not hasattr(current_user, 'is_admin') or not current_user.is_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot execute tools for other users"
            )
    
    mcp_server = MCPServer(db)
    
    try:
        response = await mcp_server.execute_tool(request)
        
        if not response.success:
            logger.warning(f"MCP tool execution failed: {response.error}")
        
        return response
        
    except Exception as e:
        logger.error(f"MCP tool execution error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Tool execution failed: {str(e)}"
        )


@router.get("/categories", response_model=List[str])
async def get_tool_categories(db: Session = Depends(get_db)):
    """
    Get list of all available tool categories
    
    Returns:
    - List of tool categories
    """
    
    return tool_registry.get_categories()


@router.get("/stats", response_model=Dict[str, Any])
async def get_usage_stats(
    tool_name: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Get MCP server usage statistics
    
    Args:
    - tool_name: Optional specific tool to get stats for
    
    Returns:
    - Usage statistics per tool or specific tool stats
    - Performance metrics and trends
    """
    
    if tool_name:
        tool_stats = tool_registry.get_tool_stats(tool_name)
        if not tool_stats:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No stats found for tool '{tool_name}'"
            )
        return {tool_name: tool_stats}
    
    all_stats = tool_registry.get_tool_stats()
    
    # Add aggregate statistics
    total_calls = sum(stats["total_calls"] for stats in all_stats.values())
    successful_calls = sum(stats["successful_calls"] for stats in all_stats.values())
    failed_calls = sum(stats["failed_calls"] for stats in all_stats.values())
    
    return {
        "individual_tools": all_stats,
        "aggregate_stats": {
            "total_calls": total_calls,
            "successful_calls": successful_calls,
            "failed_calls": failed_calls,
            "success_rate": (successful_calls / total_calls * 100) if total_calls > 0 else 0.0,
            "total_tools": len(all_stats),
            "active_tools": len([name for name, stats in all_stats.items() if stats["total_calls"] > 0])
        }
    }


@router.post("/tools/batch", response_model=List[MCPResponse])
async def execute_tools_batch(
    requests: List[MCPRequest],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Execute multiple MCP tools in batch
    
    Args:
    - requests: List of MCP tool execution requests
    
    Returns:
    - List of tool execution results
    """
    
    if len(requests) > 10:  # Limit batch size
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Batch size cannot exceed 10 requests"
        )
    
    mcp_server = MCPServer(db)
    responses = []
    
    for request in requests:
        # Set user_id from authenticated user if not provided
        if not request.user_id:
            request.user_id = current_user.id
        
        # Validate permissions
        if request.user_id != current_user.id:
            if not hasattr(current_user, 'is_admin') or not current_user.is_admin:
                responses.append(MCPResponse(
                    success=False,
                    error="Cannot execute tools for other users",
                    tool_name=request.tool_name,
                    request_id=request.request_id
                ))
                continue
        
        try:
            response = await mcp_server.execute_tool(request)
            responses.append(response)
        except Exception as e:
            logger.error(f"Batch MCP tool execution error: {str(e)}")
            responses.append(MCPResponse(
                success=False,
                error=str(e),
                tool_name=request.tool_name,
                request_id=request.request_id
            ))
    
    return responses


def _get_tool_examples(tool_name: str) -> Dict[str, Any]:
    """
    Get example usage patterns for a specific tool
    """
    
    examples = {
        "get_user_progress": {
            "basic_usage": {
                "parameters": {
                    "user_id": "123e4567-e89b-12d3-a456-426614174000",
                    "include_quiz_scores": True
                },
                "description": "Get comprehensive progress for a user"
            },
            "specific_lessons": {
                "parameters": {
                    "user_id": "123e4567-e89b-12d3-a456-426614174000",
                    "lesson_ids": [1, 2, 3],
                    "include_time_spent": True
                },
                "description": "Get progress for specific lessons only"
            }
        },
        "update_progress": {
            "complete_lesson": {
                "parameters": {
                    "user_id": "123e4567-e89b-12d3-a456-426614174000",
                    "lesson_id": 1,
                    "completion_status": "completed",
                    "score": 85.5,
                    "time_spent_minutes": 45
                },
                "description": "Mark a lesson as completed with score"
            }
        },
        "generate_lesson": {
            "beginner_drawing": {
                "parameters": {
                    "user_id": "123e4567-e89b-12d3-a456-426614174000",
                    "topic": "Basic Sketching Techniques",
                    "difficulty_level": "beginner",
                    "lesson_type": "practical",
                    "duration_minutes": 30
                },
                "description": "Generate a beginner-level practical lesson"
            }
        }
    }
    
    return examples.get(tool_name, {"note": "No examples available for this tool"})
