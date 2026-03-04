import uuid
from datetime import datetime, timedelta
from typing import List, Dict, Any, Tuple, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, desc
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler

from app.entities.analytics import (
    AnalyticsPeriod, MetricType, LearningPattern, ProgressPrediction,
    LearningInsight, PerformanceMetrics, ComprehensiveAnalytics, AnalyticsRequest
)
from app.entities.models import User, Lesson, QuizQuestion, QuizResponse, Progress, Reminder
from app.repositories.image_analysis_repository import ImageAnalysisModel

class AdvancedAnalyticsService:
    def __init__(self, db: Session):
        self.db = db
    
    async def generate_comprehensive_analytics(
        self, 
        user_id: str, 
        request: AnalyticsRequest
    ) -> ComprehensiveAnalytics:
        """Generate comprehensive analytics for a user."""
        
        # Get date range for analysis period
        end_date = datetime.utcnow()
        start_date = self._get_period_start_date(end_date, request.period)
        
        # Gather all metrics
        performance_metrics = await self._calculate_performance_metrics(
            user_id, start_date, end_date
        )
        
        # Identify learning patterns
        learning_patterns = await self._identify_learning_patterns(
            user_id, start_date, end_date
        )
        
        # Generate insights
        insights = await self._generate_learning_insights(
            user_id, start_date, end_date, performance_metrics
        )
        
        # Predict progress
        progress_prediction = None
        if request.include_predictions:
            progress_prediction = await self._predict_progress(user_id)
        
        # Detailed analyses
        skill_development = await self._analyze_skill_development(
            user_id, start_date, end_date
        )
        engagement_analysis = await self._analyze_engagement_patterns(
            user_id, start_date, end_date
        )
        
        comparative_analysis = {}
        if request.include_comparisons:
            comparative_analysis = await self._compare_with_peers(
                user_id, start_date, end_date
            )
        
        # Generate recommendations
        recommendations = await self._generate_personalized_recommendations(
            user_id, insights, performance_metrics
        )
        
        focus_areas = await self._identify_focus_areas(insights, performance_metrics)
        next_milestones = await self._generate_next_milestones(user_id, progress_prediction)
        
        return ComprehensiveAnalytics(
            user_id=user_id,
            analysis_period=request.period,
            generated_at=datetime.utcnow(),
            performance_metrics=performance_metrics,
            learning_patterns=learning_patterns,
            insights=insights,
            progress_prediction=progress_prediction,
            skill_development=skill_development,
            engagement_analysis=engagement_analysis,
            comparative_analysis=comparative_analysis,
            personalized_recommendations=recommendations,
            focus_areas=focus_areas,
            next_milestones=next_milestones
        )
    
    async def _calculate_performance_metrics(
        self, 
        user_id: str, 
        start_date: datetime, 
        end_date: datetime
    ) -> List[PerformanceMetrics]:
        """Calculate comprehensive performance metrics."""
        metrics = []
        
        # Progress Score Metrics
        current_progress = self.db.query(func.avg(Progress.score)).filter(
            Progress.user_id == user_id,
            Progress.created_at >= start_date,
            Progress.created_at <= end_date
        ).scalar() or 0.0
        
        # Previous period for comparison
        prev_start = start_date - (end_date - start_date)
        previous_progress = self.db.query(func.avg(Progress.score)).filter(
            Progress.user_id == user_id,
            Progress.created_at >= prev_start,
            Progress.created_at < start_date
        ).scalar() or 0.0
        
        metrics.append(PerformanceMetrics(
            metric_type=MetricType.PROGRESS_SCORE,
            current_value=current_progress,
            previous_value=previous_progress,
            change_percentage=self._calculate_percentage_change(previous_progress, current_progress),
            trend=self._determine_trend(previous_progress, current_progress),
            percentile_rank=await self._get_percentile_rank(user_id, MetricType.PROGRESS_SCORE)
        ))
        
        # Lesson Completion Rate
        total_lessons = self.db.query(func.count(Lesson.id)).scalar() or 1
        completed_lessons = self.db.query(func.count(distinct(Progress.lesson_id))).filter(
            Progress.user_id == user_id,
            Progress.created_at >= start_date,
            Progress.created_at <= end_date
        ).scalar() or 0
        
        completion_rate = (completed_lessons / total_lessons) * 100
        
        metrics.append(PerformanceMetrics(
            metric_type=MetricType.LESSON_COMPLETION,
            current_value=completion_rate,
            previous_value=None,  # Could calculate if needed
            change_percentage=None,
            trend="stable",
            percentile_rank=await self._get_percentile_rank(user_id, MetricType.LESSON_COMPLETION)
        ))
        
        # Quiz Accuracy
        avg_quiz_score = self.db.query(func.avg(QuizResponse.score)).filter(
            QuizResponse.user_id == user_id,
            QuizResponse.created_at >= start_date,
            QuizResponse.created_at <= end_date
        ).scalar() or 0.0
        
        metrics.append(PerformanceMetrics(
            metric_type=MetricType.QUIZ_ACCURACY,
            current_value=avg_quiz_score,
            previous_value=None,
            change_percentage=None,
            trend="stable",
            percentile_rank=await self._get_percentile_rank(user_id, MetricType.QUIZ_ACCURACY)
        ))
        
        # Artwork Analysis Score (from our new feature)
        avg_artwork_score = self.db.query(func.avg(ImageAnalysisModel.overall_score)).filter(
            ImageAnalysisModel.user_id == user_id,
            ImageAnalysisModel.created_at >= start_date,
            ImageAnalysisModel.created_at <= end_date
        ).scalar() or 0.0
        
        metrics.append(PerformanceMetrics(
            metric_type=MetricType.ARTWORK_ANALYSIS_SCORE,
            current_value=avg_artwork_score,
            previous_value=None,
            change_percentage=None,
            trend="stable",
            percentile_rank=await self._get_percentile_rank(user_id, MetricType.ARTWORK_ANALYSIS_SCORE)
        ))
        
        # Learning Streak
        streak_days = await self._calculate_learning_streak(user_id)
        metrics.append(PerformanceMetrics(
            metric_type=MetricType.STREAK_DAYS,
            current_value=float(streak_days),
            previous_value=None,
            change_percentage=None,
            trend="stable",
            percentile_rank=None
        ))
        
        return metrics
    
    async def _identify_learning_patterns(
        self, 
        user_id: str, 
        start_date: datetime, 
        end_date: datetime
    ) -> List[LearningPattern]:
        """Identify learning patterns using behavioral analysis."""
        patterns = []
        
        # Analyze activity patterns by day of week and time
        activity_data = self.db.query(
            func.extract('dow', Progress.created_at).label('day_of_week'),
            func.extract('hour', Progress.created_at).label('hour_of_day'),
            func.count('*').label('activity_count')
        ).filter(
            Progress.user_id == user_id,
            Progress.created_at >= start_date,
            Progress.created_at <= end_date
        ).group_by('day_of_week', 'hour_of_day').all()
        
        # Analyze consistency
        daily_activity = {}
        for row in activity_data:
            day = int(row.day_of_week)
            if day not in daily_activity:
                daily_activity[day] = 0
            daily_activity[day] += row.activity_count
        
        # Determine learning pattern
        weekend_activity = daily_activity.get(0, 0) + daily_activity.get(6, 0)  # Sunday + Saturday
        weekday_activity = sum(daily_activity.get(i, 0) for i in range(1, 6))
        
        if weekend_activity > weekday_activity * 0.5:
            patterns.append(LearningPattern(
                pattern_id=str(uuid.uuid4()),
                user_id=user_id,
                pattern_type="weekend_warrior",
                confidence_score=0.8,
                description="User shows high learning activity on weekends",
                identified_at=datetime.utcnow()
            ))
        elif len(daily_activity) >= 5:
            patterns.append(LearningPattern(
                pattern_id=str(uuid.uuid4()),
                user_id=user_id,
                pattern_type="consistent_learner",
                confidence_score=0.9,
                description="User demonstrates consistent daily learning habits",
                identified_at=datetime.utcnow()
            ))
        
        # Analyze session length patterns
        avg_session_activities = weekday_activity / max(len(daily_activity), 1)
        if avg_session_activities > 10:
            patterns.append(LearningPattern(
                pattern_id=str(uuid.uuid4()),
                user_id=user_id,
                pattern_type="intensive_learner",
                confidence_score=0.7,
                description="User prefers longer, intensive learning sessions",
                identified_at=datetime.utcnow()
            ))
        
        return patterns
    
    async def _generate_learning_insights(
        self, 
        user_id: str, 
        start_date: datetime, 
        end_date: datetime,
        performance_metrics: List[PerformanceMetrics]
    ) -> List[LearningInsight]:
        """Generate actionable learning insights."""
        insights = []
        
        # Analyze progress trends
        progress_metric = next((m for m in performance_metrics if m.metric_type == MetricType.PROGRESS_SCORE), None)
        if progress_metric and progress_metric.change_percentage:
            if progress_metric.change_percentage > 10:
                insights.append(LearningInsight(
                    insight_id=str(uuid.uuid4()),
                    user_id=user_id,
                    insight_type="strength",
                    title="Strong Progress Improvement",
                    description=f"Your progress score improved by {progress_metric.change_percentage:.1f}% this period!",
                    impact_score=8.5,
                    actionable_steps=[
                        "Continue your current learning approach",
                        "Consider challenging yourself with advanced topics",
                        "Share your success story with other learners"
                    ],
                    created_at=datetime.utcnow()
                ))
            elif progress_metric.change_percentage < -5:
                insights.append(LearningInsight(
                    insight_id=str(uuid.uuid4()),
                    user_id=user_id,
                    insight_type="opportunity",
                    title="Focus Needed on Consistency",
                    description=f"Your progress score declined by {abs(progress_metric.change_percentage):.1f}% this period.",
                    impact_score=7.0,
                    actionable_steps=[
                        "Review your study schedule and make adjustments",
                        "Focus on fundamental concepts before advanced topics",
                        "Consider setting smaller, achievable daily goals"
                    ],
                    created_at=datetime.utcnow()
                ))
        
        # Analyze artwork submissions
        artwork_metric = next((m for m in performance_metrics if m.metric_type == MetricType.ARTWORK_ANALYSIS_SCORE), None)
        if artwork_metric and artwork_metric.current_value > 0:
            if artwork_metric.current_value >= 8.0:
                insights.append(LearningInsight(
                    insight_id=str(uuid.uuid4()),
                    user_id=user_id,
                    insight_type="strength",
                    title="Excellent Artwork Quality",
                    description=f"Your artwork submissions show high quality with an average score of {artwork_metric.current_value:.1f}/10",
                    impact_score=9.0,
                    actionable_steps=[
                        "Consider exploring more advanced techniques",
                        "Experiment with different art styles",
                        "Consider mentoring other beginning artists"
                    ],
                    created_at=datetime.utcnow()
                ))
        
        # Analyze engagement frequency
        recent_activities = self.db.query(func.count('*')).filter(
            Progress.user_id == user_id,
            Progress.created_at >= end_date - timedelta(days=7)
        ).scalar() or 0
        
        if recent_activities == 0:
            insights.append(LearningInsight(
                insight_id=str(uuid.uuid4()),
                user_id=user_id,
                insight_type="opportunity",
                title="Re-engage with Learning",
                description="No recent learning activity detected in the past week.",
                impact_score=8.0,
                actionable_steps=[
                    "Set aside 15 minutes daily for art practice",
                    "Start with short, achievable lessons",
                    "Enable reminder notifications to stay consistent"
                ],
                created_at=datetime.utcnow()
            ))
        
        return insights
    
    async def _predict_progress(self, user_id: str) -> ProgressPrediction:
        """Predict future learning progress using ML models."""
        
        # Get historical progress data
        progress_data = self.db.query(
            Progress.created_at,
            Progress.score
        ).filter(
            Progress.user_id == user_id
        ).order_by(Progress.created_at).all()
        
        if len(progress_data) < 5:
            return ProgressPrediction(
                user_id=user_id,
                predicted_skill_level="insufficient_data",
                current_trajectory="unknown",
                estimated_completion_date=None,
                confidence_interval=0.0,
                key_factors=["Need more learning data for accurate predictions"],
                recommendations=["Continue regular learning activities to enable progress tracking"]
            )
        
        # Prepare data for ML model
        X = np.array([(d.created_at - progress_data[0].created_at).days for d in progress_data]).reshape(-1, 1)
        y = np.array([d.score for d in progress_data])
        
        # Fit linear regression model
        model = LinearRegression()
        model.fit(X, y)
        
        # Predict future progress
        days_ahead = 30  # Predict 30 days ahead
        future_X = np.array([[(progress_data[-1].created_at - progress_data[0].created_at).days + days_ahead]])
        predicted_score = model.predict(future_X)[0]
        
        # Determine trajectory
        slope = model.coef_[0]
        if slope > 0.01:
            trajectory = "improving"
        elif slope < -0.01:
            trajectory = "declining"
        else:
            trajectory = "stable"
        
        # Calculate confidence based on R² score
        confidence = max(0.0, min(1.0, model.score(X, y)))
        
        # Determine predicted skill level
        current_avg = np.mean(y[-5:])  # Last 5 scores
        if predicted_score >= 8.5:
            skill_level = "advanced"
        elif predicted_score >= 6.5:
            skill_level = "intermediate"
        else:
            skill_level = "beginner"
        
        # Key factors influencing prediction
        key_factors = []
        if slope > 0:
            key_factors.append("Consistent improvement trend")
        else:
            key_factors.append("Need for increased practice consistency")
        
        if len(progress_data) >= 20:
            key_factors.append("Sufficient learning history for reliable prediction")
        
        # Generate recommendations
        recommendations = []
        if trajectory == "improving":
            recommendations.extend([
                "Continue current learning pace",
                "Consider challenging yourself with advanced topics"
            ])
        elif trajectory == "declining": 
            recommendations.extend([
                "Review and reinforce fundamental concepts",
                "Increase practice frequency",
                "Consider seeking additional guidance"
            ])
        else:
            recommendations.extend([
                "Introduce variety in learning activities",
                "Set new learning challenges"
            ])
        
        return ProgressPrediction(
            user_id=user_id,
            predicted_skill_level=skill_level,
            current_trajectory=trajectory,
            estimated_completion_date=datetime.utcnow() + timedelta(days=days_ahead),
            confidence_interval=confidence,
            key_factors=key_factors,
            recommendations=recommendations
        )
    
    async def _analyze_skill_development(
        self, 
        user_id: str, 
        start_date: datetime, 
        end_date: datetime
    ) -> Dict[str, Any]:
        """Analyze skill development across different art topics."""
        
        # Group progress by lesson topics (assuming lessons have topics/categories)
        skill_progress = self.db.query(
            Lesson.category,
            func.avg(Progress.score).label('avg_score'),
            func.count(Progress.id).label('activity_count')
        ).join(Progress, Lesson.id == Progress.lesson_id).filter(
            Progress.user_id == user_id,
            Progress.created_at >= start_date,
            Progress.created_at <= end_date
        ).group_by(Lesson.category).all()
        
        skill_data = {}
        for row in skill_progress:
            skill_data[row.category or "general"] = {
                "average_score": float(row.avg_score or 0),
                "activity_count": row.activity_count,
                "proficiency_level": self._determine_proficiency_level(row.avg_score or 0)
            }
        
        return {
            "skills_breakdown": skill_data,
            "strongest_skills": sorted(
                skill_data.items(), 
                key=lambda x: x[1]["average_score"], 
                reverse=True
            )[:3],
            "developing_skills": [
                skill for skill, data in skill_data.items() 
                if data["average_score"] < 7.0 and data["activity_count"] >= 2
            ]
        }
    
    async def _analyze_engagement_patterns(
        self, 
        user_id: str, 
        start_date: datetime, 
        end_date: datetime
    ) -> Dict[str, Any]:
        """Analyze user engagement patterns."""
        
        # Daily activity distribution
        daily_activity = self.db.query(
            func.date(Progress.created_at).label('date'),
            func.count('*').label('activities')
        ).filter(
            Progress.user_id == user_id,
            Progress.created_at >= start_date,
            Progress.created_at <= end_date
        ).group_by(func.date(Progress.created_at)).all()
        
        # Calculate engagement metrics
        total_days = (end_date - start_date).days
        active_days = len(daily_activity)
        engagement_rate = (active_days / total_days) * 100 if total_days > 0 else 0
        
        # Peak activity times
        hourly_activity = self.db.query(
            func.extract('hour', Progress.created_at).label('hour'),
            func.count('*').label('activities')
        ).filter(
            Progress.user_id == user_id,
            Progress.created_at >= start_date,
            Progress.created_at <= end_date
        ).group_by(func.extract('hour', Progress.created_at)).all()
        
        peak_hours = sorted(hourly_activity, key=lambda x: x.activities, reverse=True)[:3]
        
        return {
            "engagement_rate": engagement_rate,
            "active_days": active_days,
            "total_activities": sum(day.activities for day in daily_activity),
            "average_daily_activities": sum(day.activities for day in daily_activity) / max(active_days, 1),
            "peak_learning_hours": [int(hour.hour) for hour in peak_hours],
            "consistency_score": min(100, engagement_rate * 1.2)  # Bonus for consistency
        }
    
    async def _compare_with_peers(
        self, 
        user_id: str, 
        start_date: datetime, 
        end_date: datetime
    ) -> Dict[str, Any]:
        """Compare user performance with similar learners."""
        
        # Get user's skill level
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            return {}
        
        # Find peers with similar skill level
        peer_progress = self.db.query(
            func.avg(Progress.score).label('avg_score'),
            func.count(Progress.id).label('activity_count')
        ).join(User, User.id == Progress.user_id).filter(
            User.skill_level == user.skill_level,
            User.id != user_id,
            Progress.created_at >= start_date,
            Progress.created_at <= end_date
        ).first()
        
        # User's stats
        user_progress = self.db.query(
            func.avg(Progress.score).label('avg_score'),
            func.count(Progress.id).label('activity_count')
        ).filter(
            Progress.user_id == user_id,
            Progress.created_at >= start_date,
            Progress.created_at <= end_date
        ).first()
        
        if not peer_progress or not user_progress:
            return {"message": "Insufficient peer data for comparison"}
        
        return {
            "skill_level_group": user.skill_level,
            "your_average_score": float(user_progress.avg_score or 0),
            "peer_average_score": float(peer_progress.avg_score or 0),
            "your_activity_count": user_progress.activity_count,
            "peer_average_activity": float(peer_progress.activity_count or 0),
            "performance_percentile": self._calculate_percentile(
                float(user_progress.avg_score or 0),
                float(peer_progress.avg_score or 0)
            )
        }
    
    async def _generate_personalized_recommendations(
        self, 
        user_id: str, 
        insights: List[LearningInsight], 
        metrics: List[PerformanceMetrics]
    ) -> List[str]:
        """Generate personalized recommendations based on analytics."""
        recommendations = []
        
        # Extract recommendations from insights
        for insight in insights:
            recommendations.extend(insight.actionable_steps[:2])  # Limit to top 2 per insight
        
        # Add metric-based recommendations
        quiz_metric = next((m for m in metrics if m.metric_type == MetricType.QUIZ_ACCURACY), None)
        if quiz_metric and quiz_metric.current_value < 70:
            recommendations.append("Focus on reviewing quiz materials and practice questions")
        
        streak_metric = next((m for m in metrics if m.metric_type == MetricType.STREAK_DAYS), None)
        if streak_metric and streak_metric.current_value < 3:
            recommendations.append("Build a consistent daily learning habit for better retention")
        
        # Remove duplicates and limit
        unique_recommendations = list(set(recommendations))
        return unique_recommendations[:8]  # Limit to top 8 recommendations
    
    async def _identify_focus_areas(
        self, 
        insights: List[LearningInsight], 
        metrics: List[PerformanceMetrics]
    ) -> List[str]:
        """Identify key areas that need focus."""
        focus_areas = []
        
        # Areas from insights marked as opportunities or weaknesses
        opportunity_insights = [i for i in insights if i.insight_type in ["opportunity", "weakness"]]
        for insight in opportunity_insights:
            if "consistency" in insight.title.lower():
                focus_areas.append("Learning Consistency")
            elif "progress" in insight.title.lower():
                focus_areas.append("Progress Rate")
            elif "engagement" in insight.title.lower():
                focus_areas.append("Active Engagement")
        
        # Areas from low-performing metrics
        low_metrics = [m for m in metrics if m.current_value < 70]
        for metric in low_metrics:
            if metric.metric_type == MetricType.QUIZ_ACCURACY:
                focus_areas.append("Concept Understanding")
            elif metric.metric_type == MetricType.ARTWORK_ANALYSIS_SCORE:
                focus_areas.append("Practical Application")
        
        return list(set(focus_areas))[:5]  # Remove duplicates, limit to 5
    
    async def _generate_next_milestones(
        self, 
        user_id: str, 
        prediction: Optional[ProgressPrediction]
    ) -> List[Dict[str, Any]]:
        """Generate next learning milestones."""
        milestones = []
        
        # Get current user progress
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            return milestones
        
        # Skill level advancement milestones
        current_level = user.skill_level
        if current_level == "beginner":
            milestones.extend([
                {
                    "title": "Complete 10 Basic Lessons",
                    "description": "Master fundamental art concepts",
                    "target_date": datetime.utcnow() + timedelta(days=30),
                    "progress_indicator": "lesson_completion"
                },
                {
                    "title": "Achieve 80% Quiz Accuracy",
                    "description": "Demonstrate solid understanding of concepts",
                    "target_date": datetime.utcnow() + timedelta(days=45),
                    "progress_indicator": "quiz_performance"
                }
            ])
        elif current_level == "intermediate":
            milestones.extend([
                {
                    "title": "Submit 5 Artwork Analyses",
                    "description": "Get AI feedback on your artistic work",
                    "target_date": datetime.utcnow() + timedelta(days=60),
                    "progress_indicator": "artwork_submissions"
                },
                {
                    "title": "Maintain 7-Day Learning Streak", 
                    "description": "Build consistent learning habits",
                    "target_date": datetime.utcnow() + timedelta(days=14),
                    "progress_indicator": "consistency"
                }
            ])
        
        # Prediction-based milestones
        if prediction and prediction.predicted_skill_level != current_level:
            milestones.append({
                "title": f"Advance to {prediction.predicted_skill_level.title()} Level",
                "description": f"Based on your current progress trajectory",
                "target_date": prediction.estimated_completion_date,
                "progress_indicator": "skill_advancement"
            })
        
        return milestones[:4]  # Limit to 4 milestones
    
    # Helper methods
    def _get_period_start_date(self, end_date: datetime, period: AnalyticsPeriod) -> datetime:
        """Get start date for analysis period."""
        if period == AnalyticsPeriod.WEEK:
            return end_date - timedelta(weeks=1)
        elif period == AnalyticsPeriod.MONTH:
            return end_date - timedelta(days=30)
        elif period == AnalyticsPeriod.QUARTER:
            return end_date - timedelta(days=90) 
        elif period == AnalyticsPeriod.YEAR:
            return end_date - timedelta(days=365)
        else:  # ALL_TIME
            return datetime.min
    
    def _calculate_percentage_change(self, old_value: float, new_value: float) -> Optional[float]:
        """Calculate percentage change between two values."""
        if old_value == 0:
            return None
        return ((new_value - old_value) / old_value) * 100
    
    def _determine_trend(self, old_value: float, new_value: float) -> str:
        """Determine trend direction."""
        if new_value > old_value * 1.05:  # 5% threshold
            return "increasing"
        elif new_value < old_value * 0.95:
            return "decreasing"
        else:
            return "stable"
    
    async def _get_percentile_rank(self, user_id: str, metric_type: MetricType) -> Optional[float]:
        """Get user's percentile rank for a metric."""
        # Simplified percentile calculation - would need more complex logic for real implementation
        return 75.0  # Placeholder
    
    async def _calculate_learning_streak(self, user_id: str) -> int:
        """Calculate current learning streak in days."""
        # Get recent daily activities
        recent_dates = self.db.query(
            func.date(Progress.created_at).label('date')
        ).filter(
            Progress.user_id == user_id,
            Progress.created_at >= datetime.utcnow() - timedelta(days=30)
        ).distinct().order_by(desc('date')).all()
        
        if not recent_dates:
            return 0
        
        # Calculate consecutive days
        streak = 0
        current_date = datetime.utcnow().date()
        
        for date_record in recent_dates:
            activity_date = date_record.date
            if activity_date == current_date or activity_date == current_date - timedelta(days=streak):
                streak += 1
                current_date = activity_date - timedelta(days=1)
            else:
                break
        
        return streak
    
    def _determine_proficiency_level(self, score: float) -> str:
        """Determine proficiency level from score."""
        if score >= 8.5:
            return "advanced"
        elif score >= 6.5:
            return "intermediate"
        else:
            return "beginner"
    
    def _calculate_percentile(self, user_score: float, peer_average: float) -> float:
        """Calculate approximate percentile based on comparison with peers."""
        if user_score >= peer_average:
            return min(95.0, 50.0 + (user_score - peer_average) * 10)
        else:
            return max(5.0, 50.0 - (peer_average - user_score) * 10)

# Import required modules for analysis
from sqlalchemy import distinct
