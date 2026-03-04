from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from typing import List, Optional
import base64

from app.database import get_db
from app.auth.dependencies import get_current_user
from app.entities.image_analysis import (
    ImageAnalysisRequest, ImageAnalysisResult, ArtworkType, AnalysisType
)
from app.services.image_analysis_service import ImageAnalysisService
from app.rag.rag_service import RAGService
from app.services.file_service import FileService
from app.config import get_openai_client

router = APIRouter(prefix="/api/analysis", tags=["Image Analysis"])
security = HTTPBearer()

def get_image_analysis_service(db: Session = Depends(get_db)) -> ImageAnalysisService:
    """Dependency to get image analysis service."""
    openai_client = get_openai_client()
    rag_service = RAGService(db, openai_client)
    file_service = FileService()
    return ImageAnalysisService(db, openai_client, rag_service, file_service)

@router.post("/analyze", response_model=ImageAnalysisResult)
async def analyze_artwork(
    request: ImageAnalysisRequest,
    current_user = Depends(get_current_user),
    service: ImageAnalysisService = Depends(get_image_analysis_service)
):
    """
    Analyze uploaded artwork using AI vision and provide educational feedback.
    
    - **image_data**: Base64 encoded image
    - **artwork_type**: Type of artwork (drawing, painting, etc.)
    - **analysis_types**: List of analysis aspects to focus on
    - **user_context**: Optional context about what user wants feedback on
    - **skill_level**: User's skill level (beginner, intermediate, advanced)
    """
    try:
        result = await service.analyze_artwork(current_user["user_id"], request)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Analysis failed. Please try again.")

@router.post("/analyze-upload", response_model=ImageAnalysisResult)
async def analyze_uploaded_file(
    file: UploadFile = File(...),
    artwork_type: ArtworkType = Form(...),
    analysis_types: str = Form(...),  # Comma-separated list
    user_context: Optional[str] = Form(None),
    skill_level: Optional[str] = Form(None),
    current_user = Depends(get_current_user),
    service: ImageAnalysisService = Depends(get_image_analysis_service)
):
    """
    Analyze artwork uploaded as file.
    """
    try:
        # Validate file type
        if not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        # Read and encode file
        file_data = await file.read()
        base64_data = base64.b64encode(file_data).decode()
        
        # Parse analysis types
        analysis_type_list = [
            AnalysisType(t.strip()) for t in analysis_types.split(',') 
            if t.strip() in [at.value for at in AnalysisType]
        ]
        
        if not analysis_type_list:
            analysis_type_list = [AnalysisType.OVERALL_CRITIQUE]
        
        # Create request
        request = ImageAnalysisRequest(
            image_data=base64_data,
            artwork_type=artwork_type,
            analysis_types=analysis_type_list,
            user_context=user_context,
            skill_level=skill_level
        )
        
        result = await service.analyze_artwork(current_user["user_id"], request)
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="Upload analysis failed. Please try again.")

@router.get("/history", response_model=List[ImageAnalysisResult])
async def get_analysis_history(
    current_user = Depends(get_current_user),
    service: ImageAnalysisService = Depends(get_image_analysis_service)
):
    """Get user's artwork analysis history."""
    try:
        history = await service.get_user_analysis_history(current_user["user_id"])
        return history
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to retrieve analysis history")

@router.get("/analytics")
async def get_user_analytics(
    current_user = Depends(get_current_user),
    service: ImageAnalysisService = Depends(get_image_analysis_service)
):
    """
    Get advanced analytics about user's artwork submissions.
    
    Returns:
    - Total analysis count
    - Artwork type distribution  
    - Average scores by type
    - Recent score trends
    - Improvement trajectory
    """
    try:
        analytics = await service.get_user_analytics(current_user["user_id"])
        return analytics
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to retrieve analytics")

@router.get("/{analysis_id}", response_model=ImageAnalysisResult)
async def get_analysis_by_id(
    analysis_id: str,
    current_user = Depends(get_current_user),
    service: ImageAnalysisService = Depends(get_image_analysis_service)
):
    """Get specific analysis by ID."""
    try:
        analysis = await service.get_analysis_by_id(analysis_id, current_user["user_id"])
        if not analysis:
            raise HTTPException(status_code=404, detail="Analysis not found")
        return analysis
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to retrieve analysis")

@router.delete("/{analysis_id}")
async def delete_analysis(
    analysis_id: str,
    current_user = Depends(get_current_user),
    service: ImageAnalysisService = Depends(get_image_analysis_service)
):
    """Delete an analysis (user can only delete their own analyses)."""
    try:
        success = await service.repository.delete_analysis(analysis_id, current_user["user_id"])
        if not success:
            raise HTTPException(status_code=404, detail="Analysis not found or unauthorized")
        return {"message": "Analysis deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to delete analysis")

@router.get("/types/artwork", response_model=List[str])
async def get_artwork_types():
    """Get available artwork types."""
    return [artwork_type.value for artwork_type in ArtworkType]

@router.get("/types/analysis", response_model=List[str])  
async def get_analysis_types():
    """Get available analysis types."""
    return [analysis_type.value for analysis_type in AnalysisType]
