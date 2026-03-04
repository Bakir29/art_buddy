import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import Column, String, Float, DateTime, Text, JSON
from app.database import Base
from app.entities.image_analysis import ImageAnalysisEntity, ArtworkType

class ImageAnalysisModel(Base):
    __tablename__ = "image_analyses"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, nullable=False, index=True)
    image_url = Column(String, nullable=False)
    artwork_type = Column(String, nullable=False)
    analysis_data = Column(JSON, nullable=False)  # Store complete analysis results
    overall_score = Column(Float, nullable=False)
    ai_summary = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class ImageAnalysisRepository:
    def __init__(self, db: Session):
        self.db = db
    
    async def create_analysis(self, analysis_data: ImageAnalysisEntity) -> ImageAnalysisEntity:
        """Create a new image analysis record."""
        db_analysis = ImageAnalysisModel(
            user_id=analysis_data.user_id,
            image_url=analysis_data.image_url,
            artwork_type=analysis_data.artwork_type,
            analysis_data=analysis_data.analysis_data,
            overall_score=analysis_data.overall_score,
            ai_summary=analysis_data.ai_summary
        )
        
        self.db.add(db_analysis)
        self.db.commit()
        self.db.refresh(db_analysis)
        
        return self._to_entity(db_analysis)
    
    async def get_analysis_by_id(self, analysis_id: str) -> Optional[ImageAnalysisEntity]:
        """Get analysis by ID."""
        db_analysis = self.db.query(ImageAnalysisModel).filter(
            ImageAnalysisModel.id == analysis_id
        ).first()
        
        return self._to_entity(db_analysis) if db_analysis else None
    
    async def get_analyses_by_user(self, user_id: str, limit: int = 50) -> List[ImageAnalysisEntity]:
        """Get all analyses for a user."""
        db_analyses = self.db.query(ImageAnalysisModel).filter(
            ImageAnalysisModel.user_id == user_id
        ).order_by(ImageAnalysisModel.created_at.desc()).limit(limit).all()
        
        return [self._to_entity(analysis) for analysis in db_analyses]
    
    async def get_analyses_by_artwork_type(self, user_id: str, artwork_type: ArtworkType) -> List[ImageAnalysisEntity]:
        """Get analyses filtered by artwork type."""
        db_analyses = self.db.query(ImageAnalysisModel).filter(
            ImageAnalysisModel.user_id == user_id,
            ImageAnalysisModel.artwork_type == artwork_type.value
        ).order_by(ImageAnalysisModel.created_at.desc()).all()
        
        return [self._to_entity(analysis) for analysis in db_analyses]
    
    async def delete_analysis(self, analysis_id: str, user_id: str) -> bool:
        """Delete an analysis (only by the owner)."""
        result = self.db.query(ImageAnalysisModel).filter(
            ImageAnalysisModel.id == analysis_id,
            ImageAnalysisModel.user_id == user_id
        ).delete()
        
        self.db.commit()
        return result > 0
    
    async def get_user_analytics(self, user_id: str) -> Dict[str, Any]:
        """Get analytics about user's artwork submissions."""
        from sqlalchemy import func, desc
        
        # Get analysis counts by artwork type
        type_counts = self.db.query(
            ImageAnalysisModel.artwork_type,
            func.count(ImageAnalysisModel.id).label('count')
        ).filter(
            ImageAnalysisModel.user_id == user_id
        ).group_by(ImageAnalysisModel.artwork_type).all()
        
        # Get average scores by artwork type
        avg_scores = self.db.query(
            ImageAnalysisModel.artwork_type,
            func.avg(ImageAnalysisModel.overall_score).label('avg_score')
        ).filter(
            ImageAnalysisModel.user_id == user_id
        ).group_by(ImageAnalysisModel.artwork_type).all()
        
        # Get recent progress (last 10 submissions)
        recent_analyses = self.db.query(ImageAnalysisModel).filter(
            ImageAnalysisModel.user_id == user_id
        ).order_by(desc(ImageAnalysisModel.created_at)).limit(10).all()
        
        return {
            "total_analyses": len(recent_analyses),
            "artwork_type_distribution": {item.artwork_type: item.count for item in type_counts},
            "average_scores_by_type": {item.artwork_type: float(item.avg_score) for item in avg_scores},
            "recent_scores": [float(analysis.overall_score) for analysis in recent_analyses],
            "improvement_trend": self._calculate_improvement_trend([float(a.overall_score) for a in recent_analyses])
        }
    
    def _calculate_improvement_trend(self, recent_scores: List[float]) -> str:
        """Calculate if user is improving, stable, or declining."""
        if len(recent_scores) < 3:
            return "insufficient_data"
        
        # Simple linear trend analysis
        first_half_avg = sum(recent_scores[:len(recent_scores)//2]) / (len(recent_scores)//2)
        second_half_avg = sum(recent_scores[len(recent_scores)//2:]) / (len(recent_scores) - len(recent_scores)//2)
        
        diff = second_half_avg - first_half_avg
        if abs(diff) < 0.3:
            return "stable"
        elif diff > 0:
            return "improving"
        else:
            return "needs_focus"
    
    def _to_entity(self, db_model: ImageAnalysisModel) -> ImageAnalysisEntity:
        """Convert database model to entity."""
        return ImageAnalysisEntity(
            id=db_model.id,
            user_id=db_model.user_id,
            image_url=db_model.image_url,
            artwork_type=db_model.artwork_type,
            analysis_data=db_model.analysis_data,
            overall_score=db_model.overall_score,
            ai_summary=db_model.ai_summary,
            created_at=db_model.created_at,
            updated_at=db_model.updated_at
        )
