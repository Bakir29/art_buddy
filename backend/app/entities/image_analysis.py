from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum

class ArtworkType(str, Enum):
    DRAWING = "drawing"
    PAINTING = "painting"
    SCULPTURE = "sculpture"
    DIGITAL_ART = "digital_art"
    PHOTOGRAPHY = "photography"
    MIXED_MEDIA = "mixed_media"
    SKETCH = "sketch"

class AnalysisType(str, Enum):
    COMPOSITION = "composition"
    COLOR_THEORY = "color_theory"
    TECHNIQUE = "technique"
    STYLE_IDENTIFICATION = "style_identification"
    PROPORTIONS = "proportions"
    LIGHTING = "lighting"
    OVERALL_CRITIQUE = "overall_critique"

class ImageAnalysisRequest(BaseModel):
    image_data: str  # Base64 encoded image
    artwork_type: ArtworkType
    analysis_types: List[AnalysisType]
    user_context: Optional[str] = None  # What the user wants to focus on
    skill_level: Optional[str] = None  # beginner, intermediate, advanced

class AnalysisInsight(BaseModel):
    type: AnalysisType
    score: float  # 0-10 rating
    feedback: str
    suggestions: List[str]
    strengths: List[str]
    areas_for_improvement: List[str]

class ImageAnalysisResult(BaseModel):
    id: str
    user_id: str
    image_url: str
    artwork_type: ArtworkType
    analysis_timestamp: datetime
    overall_score: float
    insights: List[AnalysisInsight]
    ai_summary: str
    recommended_resources: List[str]
    next_steps: List[str]

class ImageAnalysisEntity(BaseModel):
    id: Optional[str] = None
    user_id: str
    image_url: str
    artwork_type: str
    analysis_data: Dict[str, Any]  # JSON store for analysis results
    overall_score: float
    ai_summary: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
