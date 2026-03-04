from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from typing import Dict, Any, List, Optional

from app.database import get_db
from app.auth.dependencies import get_current_user
from app.entities.analytics import (
    ComprehensiveAnalytics, AnalyticsRequest, AnalyticsPeriod,
    LearningPattern, ProgressPrediction, LearningInsight
)
from app.services.analytics_service import AdvancedAnalyticsService

router = APIRouter(prefix="/api/analytics", tags=["Advanced Analytics"])
security = HTTPBearer()

def get_analytics_service(db: Session = Depends(get_db)) -> AdvancedAnalyticsService:
    """Dependency to get analytics service."""
    return AdvancedAnalyticsService(db)

@router.get("/comprehensive", response_model=ComprehensiveAnalytics)
async def get_comprehensive_analytics(
    period: AnalyticsPeriod = Query(AnalyticsPeriod.MONTH, description="Analysis time period"),
    include_predictions: bool = Query(True, description="Include ML-based progress predictions"),
    include_comparisons: bool = Query(True, description="Include peer comparisons"),
    detailed_insights: bool = Query(True, description="Include detailed learning insights"),
    current_user = Depends(get_current_user),
    service: AdvancedAnalyticsService = Depends(get_analytics_service)
):
    """
    Get comprehensive learning analytics for the current user.
    
    Provides deep insights into:
    - Performance metrics and trends  
    - Learning patterns and behaviors
    - Progress predictions using ML
    - Skill development analysis
    - Engagement patterns
    - Peer comparisons
    - Personalized recommendations
    - Upcoming milestones
    """
    try:
        request = AnalyticsRequest(
            period=period,
            include_predictions=include_predictions,
            include_comparisons=include_comparisons,
            detailed_insights=detailed_insights
        )
        
        analytics = await service.generate_comprehensive_analytics(
            current_user["user_id"], 
            request
        )
        
        return analytics
        
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to generate analytics: {str(e)}"
        )

@router.get("/performance-summary")
async def get_performance_summary(
    period: AnalyticsPeriod = Query(AnalyticsPeriod.MONTH),
    current_user = Depends(get_current_user),
    service: AdvancedAnalyticsService = Depends(get_analytics_service)
):
    """
    Get a quick performance summary with key metrics.
    
    Returns essential metrics without detailed analysis for dashboard widgets.
    """
    try:
        request = AnalyticsRequest(
            period=period,
            include_predictions=False,
            include_comparisons=False, 
            detailed_insights=False
        )
        
        analytics = await service.generate_comprehensive_analytics(
            current_user["user_id"], 
            request
        )
        
        # Extract key metrics for summary
        summary = {
            "period": period.value,
            "performance_overview": {
                metric.metric_type.value: {
                    "current_value": metric.current_value,
                    "trend": metric.trend,
                    "percentile_rank": metric.percentile_rank
                }
                for metric in analytics.performance_metrics
            },
            "engagement_score": analytics.engagement_analysis.get("consistency_score", 0),
            "total_insights": len(analytics.insights),
            "focus_areas_count": len(analytics.focus_areas),
            "upcoming_milestones": len(analytics.next_milestones)
        }
        
        return summary
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate performance summary: {str(e)}"
        )

@router.get("/learning-patterns", response_model=List[LearningPattern])
async def get_learning_patterns(
    period: AnalyticsPeriod = Query(AnalyticsPeriod.MONTH),
    current_user = Depends(get_current_user),
    service: AdvancedAnalyticsService = Depends(get_analytics_service)
):
    """
    Get identified learning patterns for the user.
    
    Analyzes behavioral data to identify patterns like:
    - Weekend warrior (higher activity on weekends)
    - Consistent learner (regular daily activity)
    - Intensive learner (longer sessions)
    """
    try:
        from datetime import datetime
        end_date = datetime.utcnow()
        start_date = service._get_period_start_date(end_date, period)
        
        patterns = await service._identify_learning_patterns(
            current_user["user_id"], 
            start_date, 
            end_date
        )
        
        return patterns
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="Failed to analyze learning patterns"
        )

@router.get("/progress-prediction", response_model=ProgressPrediction)
async def get_progress_prediction(
    current_user = Depends(get_current_user),
    service: AdvancedAnalyticsService = Depends(get_analytics_service)
):
    """
    Get ML-based progress prediction for the user.
    
    Uses machine learning to predict:
    - Future skill level advancement
    - Progress trajectory (improving/stable/declining)
    - Estimated completion dates for milestones
    - Key factors influencing progress
    - Personalized recommendations
    """
    try:
        prediction = await service._predict_progress(current_user["user_id"])
        return prediction
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="Failed to generate progress prediction"
        )

@router.get("/insights", response_model=List[LearningInsight])
async def get_learning_insights(
    period: AnalyticsPeriod = Query(AnalyticsPeriod.MONTH),
    insight_type: Optional[str] = Query(None, description="Filter by insight type: strength, weakness, opportunity, trend"),
    current_user = Depends(get_current_user),
    service: AdvancedAnalyticsService = Depends(get_analytics_service)
):
    """
    Get actionable learning insights with personalized recommendations.
    
    Provides insights categorized as:
    - Strengths: Areas where user excels
    - Weaknesses: Areas needing improvement  
    - Opportunities: Potential growth areas
    - Trends: Patterns in learning behavior
    """
    try:
        request = AnalyticsRequest(
            period=period,
            include_predictions=False,
            include_comparisons=False,
            detailed_insights=True
        )
        
        analytics = await service.generate_comprehensive_analytics(
            current_user["user_id"], 
            request
        )
        
        insights = analytics.insights
        
        # Filter by type if specified
        if insight_type:
            insights = [i for i in insights if i.insight_type == insight_type]
        
        return insights
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="Failed to generate learning insights"
        )

@router.get("/skill-development")
async def get_skill_development_analysis(
    period: AnalyticsPeriod = Query(AnalyticsPeriod.MONTH),
    current_user = Depends(get_current_user),
    service: AdvancedAnalyticsService = Depends(get_analytics_service)
):
    """
    Get detailed skill development analysis across different art topics.
    
    Analyzes progress in different skill areas:
    - Drawing fundamentals
    - Color theory
    - Composition
    - Technique mastery
    - Style development
    """
    try:
        from datetime import datetime
        end_date = datetime.utcnow()
        start_date = service._get_period_start_date(end_date, period)
        
        skill_analysis = await service._analyze_skill_development(
            current_user["user_id"],
            start_date,
            end_date
        )
        
        return {
            "analysis_period": period.value,
            "skill_development": skill_analysis
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="Failed to analyze skill development"
        )

@router.get("/engagement-patterns")
async def get_engagement_analysis(
    period: AnalyticsPeriod = Query(AnalyticsPeriod.MONTH),
    current_user = Depends(get_current_user),
    service: AdvancedAnalyticsService = Depends(get_analytics_service)
):
    """
    Get detailed engagement pattern analysis.
    
    Analyzes learning engagement including:
    - Daily activity patterns
    - Peak learning hours
    - Consistency metrics
    - Session frequency and duration
    """
    try:
        from datetime import datetime
        end_date = datetime.utcnow()
        start_date = service._get_period_start_date(end_date, period)
        
        engagement_analysis = await service._analyze_engagement_patterns(
            current_user["user_id"],
            start_date,
            end_date
        )
        
        return {
            "analysis_period": period.value,
            "engagement_patterns": engagement_analysis
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="Failed to analyze engagement patterns"
        )

@router.get("/peer-comparison")
async def get_peer_comparison(
    period: AnalyticsPeriod = Query(AnalyticsPeriod.MONTH),
    current_user = Depends(get_current_user),
    service: AdvancedAnalyticsService = Depends(get_analytics_service)
):
    """
    Compare user performance with similar learners.
    
    Provides comparison metrics:
    - Performance vs. peers at same skill level
    - Activity level comparisons
    - Percentile rankings
    - Relative strengths and improvement areas
    """
    try:
        from datetime import datetime
        end_date = datetime.utcnow()
        start_date = service._get_period_start_date(end_date, period)
        
        comparison = await service._compare_with_peers(
            current_user["user_id"],
            start_date,
            end_date
        )
        
        return {
            "analysis_period": period.value,
            "peer_comparison": comparison
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="Failed to generate peer comparison"
        )

@router.get("/recommendations")
async def get_personalized_recommendations(
    current_user = Depends(get_current_user),
    service: AdvancedAnalyticsService = Depends(get_analytics_service)
):
    """
    Get AI-generated personalized learning recommendations.
    
    Provides actionable recommendations based on:
    - Current performance metrics
    - Learning patterns and behaviors
    - Identified strengths and weaknesses
    - Progress predictions
    - Peer comparisons
    """
    try:
        request = AnalyticsRequest(
            period=AnalyticsPeriod.MONTH,
            include_predictions=True,
            include_comparisons=True,
            detailed_insights=True
        )
        
        analytics = await service.generate_comprehensive_analytics(
            current_user["user_id"], 
            request
        )
        
        return {
            "personalized_recommendations": analytics.personalized_recommendations,
            "focus_areas": analytics.focus_areas,
            "next_milestones": analytics.next_milestones,
            "generated_at": analytics.generated_at
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="Failed to generate recommendations"
        )

@router.get("/dashboard-data")
async def get_analytics_dashboard_data(
    current_user = Depends(get_current_user),
    service: AdvancedAnalyticsService = Depends(get_analytics_service)
):
    """
    Get comprehensive data for analytics dashboard.
    
    Optimized endpoint that provides all essential analytics data
    in a single request for dashboard visualization.
    """
    try:
        request = AnalyticsRequest(
            period=AnalyticsPeriod.MONTH,
            include_predictions=True,
            include_comparisons=True,
            detailed_insights=True
        )
        
        analytics = await service.generate_comprehensive_analytics(
            current_user["user_id"], 
            request
        )
        
        # Structure data for dashboard components
        dashboard_data = {
            "overview_metrics": [
                {
                    "type": metric.metric_type.value,
                    "value": metric.current_value,
                    "trend": metric.trend,
                    "change": metric.change_percentage,
                    "percentile": metric.percentile_rank
                }
                for metric in analytics.performance_metrics
            ],
            "learning_insights": [
                {
                    "type": insight.insight_type,
                    "title": insight.title,
                    "description": insight.description,
                    "impact": insight.impact_score,
                    "actions": insight.actionable_steps[:2]  # Limit for dashboard
                }
                for insight in analytics.insights[:5]  # Top 5 insights
            ],
            "skill_progress": analytics.skill_development,
            "engagement_summary": {
                "consistency_score": analytics.engagement_analysis.get("consistency_score", 0),
                "active_days": analytics.engagement_analysis.get("active_days", 0),
                "peak_hours": analytics.engagement_analysis.get("peak_learning_hours", [])
            },
            "predictions": {
                "trajectory": analytics.progress_prediction.current_trajectory if analytics.progress_prediction else "unknown",
                "next_level": analytics.progress_prediction.predicted_skill_level if analytics.progress_prediction else "unknown",
                "confidence": analytics.progress_prediction.confidence_interval if analytics.progress_prediction else 0
            },
            "quick_actions": analytics.personalized_recommendations[:4],  # Top 4 for quick actions
            "next_milestones": analytics.next_milestones[:3],  # Next 3 milestones
            "generated_at": analytics.generated_at
        }
        
        return dashboard_data
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="Failed to generate dashboard data"
        )
