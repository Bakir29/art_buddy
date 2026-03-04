import uuid
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import openai

from app.entities.personalization import (
    UserPersonalizationProfile, PersonalizedRecommendation, AdaptiveLearningPath,
    LearningGoal, PersonalizationInsight, ContentPersonalization,
    LearningStyle, PersonalityType, ContentType, DifficultyPreference
)
from app.entities.models import User, Lesson, Progress, QuizQuestion, QuizResponse
from app.repositories.image_analysis_repository import ImageAnalysisModel
from app.rag.rag_service import RAGService

class PersonalizationService:
    """AI-powered personalization engine for adaptive learning experiences."""
    
    def __init__(self, db: Session, openai_client, rag_service: RAGService):
        self.db = db
        self.openai_client = openai_client
        self.rag_service = rag_service
    
    async def get_or_create_user_profile(self, user_id: str) -> UserPersonalizationProfile:
        """Get existing personalization profile or create new one with AI analysis."""
        
        # Check if profile exists (in real implementation, this would be from database)
        # For now, create a new profile based on user behavior analysis
        
        profile = await self.analyze_and_create_profile(user_id)
        return profile
    
    async def analyze_and_create_profile(self, user_id: str) -> UserPersonalizationProfile:
        """Analyze user behavior and create personalized profile using AI."""
        
        # Gather user behavioral data
        behavior_data = await self.gather_user_behavior_data(user_id)
        
        # Analyze learning style using ML
        learning_style = await self.infer_learning_style(behavior_data)
        
        # Determine personality type from patterns
        personality_type = await self.infer_personality_type(behavior_data)
        
        # Analyze performance patterns
        difficulty_preference = await self.analyze_difficulty_preference(behavior_data)
        
        # Infer content preferences
        preferred_content_types = await self.infer_content_preferences(behavior_data)
        
        # Analyze temporal patterns
        temporal_patterns = await self.analyze_temporal_patterns(behavior_data)
        
        # Generate artistic interest profile
        artistic_interests = await self.analyze_artistic_interests(user_id, behavior_data)
        
        # Calculate behavioral scores
        behavioral_scores = await self.calculate_behavioral_scores(behavior_data)
        
        profile = UserPersonalizationProfile(
            user_id=user_id,
            learning_style=learning_style,
            personality_type=personality_type,
            difficulty_preference=difficulty_preference,
            preferred_content_types=preferred_content_types,
            
            # Temporal preferences
            session_length_preference=temporal_patterns.get("avg_session_length", 30),
            preferred_learning_times=temporal_patterns.get("peak_hours", [19, 20, 21]),
            notification_preferences={
                "daily_reminders": True,
                "achievement_notifications": True,
                "collaboration_invites": True,
                "progress_updates": behavior_data.get("engagement_level", 0.5) > 0.7
            },
            
            # Artistic interests
            favorite_art_styles=artistic_interests.get("styles", []),
            interested_techniques=artistic_interests.get("techniques", []),
            skill_focus_areas=artistic_interests.get("focus_areas", []),
            
            # Behavioral patterns
            engagement_patterns=temporal_patterns,
            learning_velocity=behavior_data.get("lessons_per_week", 2.0),
            consistency_score=behavioral_scores.get("consistency", 0.5),
            
            # Personality scores
            curiosity_score=behavioral_scores.get("curiosity", 0.5),
            persistence_score=behavioral_scores.get("persistence", 0.5),
            collaboration_preference=behavioral_scores.get("collaboration", 0.5),
            
            # Adaptive parameters
            current_difficulty_level=behavior_data.get("avg_performance", 0.7),
            motivation_level=behavioral_scores.get("motivation", 0.7),
            confidence_level=behavioral_scores.get("confidence", 0.6),
            
            last_updated=datetime.utcnow(),
            created_at=datetime.utcnow()
        )
        
        return profile
    
    async def generate_personalized_recommendations(
        self, 
        user_id: str, 
        profile: Optional[UserPersonalizationProfile] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> List[PersonalizedRecommendation]:
        """Generate AI-powered personalized content recommendations."""
        
        if not profile:
            profile = await self.get_or_create_user_profile(user_id)
        
        # Get current user context
        user_context = context or await self.get_current_user_context(user_id)
        
        # Generate different types of recommendations
        recommendations = []
        
        # 1. Skill-building recommendations
        skill_recs = await self.recommend_skill_building_content(user_id, profile, user_context)
        recommendations.extend(skill_recs)
        
        # 2. Interest-based recommendations
        interest_recs = await self.recommend_interest_based_content(user_id, profile)
        recommendations.extend(interest_recs)
        
        # 3. Performance-based recommendations
        performance_recs = await self.recommend_performance_improvement(user_id, profile)
        recommendations.extend(performance_recs)
        
        # 4. Social/collaboration recommendations
        social_recs = await self.recommend_social_activities(user_id, profile)
        recommendations.extend(social_recs)
        
        # Sort by relevance and personalization fit
        recommendations.sort(key=lambda x: x.relevance_score, reverse=True)
        
        return recommendations[:10]  # Return top 10 recommendations
    
    async def create_adaptive_learning_path(
        self, 
        user_id: str, 
        goal: LearningGoal,
        profile: Optional[UserPersonalizationProfile] = None
    ) -> AdaptiveLearningPath:
        """Create personalized learning path adapted to user's style and goals."""
        
        if not profile:
            profile = await self.get_or_create_user_profile(user_id)
        
        # Analyze available content for the goal
        relevant_content = await self.find_relevant_content_for_goal(goal)
        
        # Create difficulty progression curve based on user preference
        difficulty_curve = self.generate_difficulty_curve(
            profile.difficulty_preference,
            profile.current_difficulty_level,
            len(relevant_content)
        )
        
        # Organize content based on learning style and preferences
        organized_lessons = await self.organize_content_for_user(
            relevant_content, profile, difficulty_curve
        )
        
        path = AdaptiveLearningPath(
            path_id=str(uuid.uuid4()),
            user_id=user_id,
            title=f"Personalized Path: {goal.title}",
            description=f"Adaptive learning path tailored to your {profile.learning_style.value} learning style",
            
            total_lessons=len(organized_lessons),
            estimated_completion_weeks=self.estimate_completion_time(
                len(organized_lessons), profile.learning_velocity
            ),
            difficulty_curve=difficulty_curve,
            
            current_position=0,
            completion_percentage=0.0,
            lessons_completed=[],
            
            pace_adjustments=[],
            difficulty_adjustments=[],
            content_substitutions=[],
            
            completion_likelihood=await self.predict_completion_likelihood(user_id, profile, goal),
            
            created_at=datetime.utcnow(),
            last_adjusted=None
        )
        
        return path
    
    async def adapt_content_presentation(
        self, 
        content_id: str, 
        user_id: str,
        profile: Optional[UserPersonalizationProfile] = None
    ) -> ContentPersonalization:
        """Adapt content presentation based on user's learning profile."""
        
        if not profile:
            profile = await self.get_or_create_user_profile(user_id)
        
        # Analyze content difficulty relative to user
        difficulty_adjustment = await self.calculate_difficulty_adjustment(
            content_id, profile.current_difficulty_level
        )
        
        # Determine content emphasis based on learning style
        content_emphasis = self.get_content_emphasis_for_learning_style(profile.learning_style)
        
        # Get additional resources based on user interests
        additional_resources = await self.get_relevant_additional_resources(
            content_id, profile
        )
        
        # Generate adaptive scaffolding
        scaffolding = await self.generate_adaptive_scaffolding(content_id, profile)
        
        personalization = ContentPersonalization(
            content_id=content_id,
            user_id=user_id,
            
            difficulty_adjustment=difficulty_adjustment,
            content_emphasis=content_emphasis,
            additional_resources=additional_resources,
            
            prerequisite_reminders=scaffolding.get("prerequisites", []),
            concept_reinforcements=scaffolding.get("reinforcements", []),
            extension_activities=scaffolding.get("extensions", []),
            
            preferred_explanation_style=self.get_explanation_style(profile.learning_style),
            visual_aid_preferences=self.get_visual_preferences(profile),
            interaction_preferences=self.get_interaction_preferences(profile),
            
            created_at=datetime.utcnow()
        )
        
        return personalization
    
    async def update_profile_from_interaction(
        self, 
        user_id: str, 
        interaction_data: Dict[str, Any]
    ):
        """Update personalization profile based on user interactions."""
        
        profile = await self.get_or_create_user_profile(user_id)
        
        # Analyze interaction for learning insights
        insights = await self.analyze_interaction_for_insights(interaction_data)
        
        # Update relevant profile attributes
        updates = {}
        
        # Update difficulty level based on performance
        if "performance_score" in interaction_data:
            score = interaction_data["performance_score"]
            if score > 0.9:
                updates["current_difficulty_level"] = min(1.0, profile.current_difficulty_level + 0.02)
            elif score < 0.6:
                updates["current_difficulty_level"] = max(0.1, profile.current_difficulty_level - 0.02)
        
        # Update engagement patterns
        if "session_duration" in interaction_data:
            duration = interaction_data["session_duration"]
            # Exponential moving average for session length preference
            alpha = 0.1
            updates["session_length_preference"] = int(
                alpha * duration + (1 - alpha) * profile.session_length_preference
            )
        
        # Update motivation based on completion patterns
        if "completion_rate" in interaction_data:
            completion_rate = interaction_data["completion_rate"]
            updates["motivation_level"] = min(1.0, max(0.1, 
                0.9 * profile.motivation_level + 0.1 * completion_rate
            ))
        
        # Apply updates and save
        for key, value in updates.items():
            setattr(profile, key, value)
        
        profile.last_updated = datetime.utcnow()
        
        # In real implementation, save to database
        return profile
    
    async def generate_personalization_insights(
        self, 
        user_id: str,
        profile: Optional[UserPersonalizationProfile] = None
    ) -> List[PersonalizationInsight]:
        """Generate AI insights about user's learning patterns and recommendations."""
        
        if not profile:
            profile = await self.get_or_create_user_profile(user_id)
        
        insights = []
        
        # Analyze learning velocity patterns
        velocity_insight = await self.analyze_learning_velocity_patterns(user_id, profile)
        if velocity_insight:
            insights.append(velocity_insight)
        
        # Analyze engagement patterns
        engagement_insight = await self.analyze_engagement_effectiveness(user_id, profile)
        if engagement_insight:
            insights.append(engagement_insight)
        
        # Analyze difficulty preferences
        difficulty_insight = await self.analyze_difficulty_optimization(user_id, profile)
        if difficulty_insight:
            insights.append(difficulty_insight)
        
        # Analyze content type effectiveness
        content_insight = await self.analyze_content_type_effectiveness(user_id, profile)
        if content_insight:
            insights.append(content_insight)
        
        return insights
    
    # Helper methods for behavior analysis
    
    async def gather_user_behavior_data(self, user_id: str) -> Dict[str, Any]:
        """Gather comprehensive user behavior data for analysis."""
        
        # Get progress data
        progress_data = self.db.query(Progress).filter(
            Progress.user_id == user_id
        ).order_by(desc(Progress.created_at)).limit(100).all()
        
        # Get quiz performance
        quiz_data = self.db.query(QuizResponse).filter(
            QuizResponse.user_id == user_id
        ).order_by(desc(QuizResponse.created_at)).limit(50).all()
        
        # Get artwork analysis data
        artwork_data = self.db.query(ImageAnalysisModel).filter(
            ImageAnalysisModel.user_id == user_id
        ).order_by(desc(ImageAnalysisModel.created_at)).limit(20).all()
        
        # Analyze patterns
        behavior = {
            "total_activities": len(progress_data),
            "avg_performance": np.mean([p.score for p in progress_data]) if progress_data else 0.5,
            "quiz_accuracy": np.mean([q.score for q in quiz_data]) if quiz_data else 0.5,
            "artwork_scores": [a.overall_score for a in artwork_data] if artwork_data else [],
            "activity_timestamps": [p.created_at for p in progress_data],
            "engagement_level": len(progress_data) / max(30, 1),  # activities per month approximation
            "lessons_per_week": len(progress_data) / max(4, 1)  # rough estimate
        }
        
        return behavior
    
    async def infer_learning_style(self, behavior_data: Dict[str, Any]) -> LearningStyle:
        """Infer learning style from behavior patterns."""
        
        # Analyze artwork submission patterns
        artwork_scores = behavior_data.get("artwork_scores", [])
        has_visual_preference = len(artwork_scores) > 2 and np.mean(artwork_scores) > 7.0
        
        # Analyze activity frequency (kinesthetic learners tend to be more active)
        activity_level = behavior_data.get("engagement_level", 0.5)
        
        # Simple heuristic-based inference (could be replaced with ML model)
        if has_visual_preference and activity_level > 0.7:
            return LearningStyle.MULTIMODAL
        elif has_visual_preference:
            return LearningStyle.VISUAL
        elif activity_level > 0.8:
            return LearningStyle.KINESTHETIC
        else:
            return LearningStyle.VISUAL  # Default for art learning
    
    async def infer_personality_type(self, behavior_data: Dict[str, Any]) -> PersonalityType:
        """Infer personality type from behavioral patterns."""
        
        avg_performance = behavior_data.get("avg_performance", 0.5)
        engagement_level = behavior_data.get("engagement_level", 0.5)
        
        # Simple rules-based inference
        if avg_performance > 0.85 and engagement_level > 0.8:
            return PersonalityType.PERFECTIONIST
        elif engagement_level > 0.9:
            return PersonalityType.EXPLORER
        elif avg_performance > 0.8:
            return PersonalityType.FOCUSED_LEARNER
        else:
            return PersonalityType.CASUAL_LEARNER
    
    async def analyze_difficulty_preference(self, behavior_data: Dict[str, Any]) -> DifficultyPreference:
        """Analyze user's difficulty preference from performance patterns."""
        
        avg_performance = behavior_data.get("avg_performance", 0.5)
        
        if avg_performance > 0.9:
            return DifficultyPreference.CHALLENGE_SEEKER
        elif avg_performance < 0.6:
            return DifficultyPreference.GRADUAL_PROGRESSION
        else:
            return DifficultyPreference.ADAPTIVE
    
    async def infer_content_preferences(self, behavior_data: Dict[str, Any]) -> List[ContentType]:
        """Infer preferred content types from engagement patterns."""
        
        # Default preferences based on activity patterns
        preferences = [ContentType.INTERACTIVE_EXERCISE, ContentType.AI_GUIDED_PRACTICE]
        
        artwork_scores = behavior_data.get("artwork_scores", [])
        if len(artwork_scores) > 0:
            preferences.extend([ContentType.PRACTICE_PROJECT, ContentType.PEER_COLLABORATION])
        
        if behavior_data.get("engagement_level", 0) > 0.7:
            preferences.append(ContentType.VIDEO_TUTORIAL)
        
        return preferences[:4]  # Limit to top 4
    
    async def analyze_temporal_patterns(self, behavior_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze temporal learning patterns."""
        
        timestamps = behavior_data.get("activity_timestamps", [])
        
        if not timestamps:
            return {
                "avg_session_length": 30,
                "peak_hours": [19, 20, 21],
                "preferred_days": [1, 2, 3, 4, 5]  # Weekdays
            }
        
        # Analyze hour patterns
        hours = [ts.hour for ts in timestamps]
        hour_counts = {}
        for hour in hours:
            hour_counts[hour] = hour_counts.get(hour, 0) + 1
        
        peak_hours = sorted(hour_counts, key=hour_counts.get, reverse=True)[:3]
        
        return {
            "avg_session_length": 30,  # Default for now
            "peak_hours": peak_hours,
            "activity_frequency": len(timestamps) / max(30, 1),
            "total_sessions": len(timestamps)
        }
    
    async def analyze_artistic_interests(self, user_id: str, behavior_data: Dict[str, Any]) -> Dict[str, List[str]]:
        """Analyze user's artistic interests from behavior."""
        
        # This would analyze lesson topics, artwork submissions, etc.
        # For now, return defaults based on engagement level
        
        engagement = behavior_data.get("engagement_level", 0.5)
        
        if engagement > 0.7:
            return {
                "styles": ["impressionism", "contemporary", "realism"],
                "techniques": ["color_theory", "composition", "lighting"],
                "focus_areas": ["painting", "drawing", "digital_art"]
            }
        else:
            return {
                "styles": ["basics", "fundamentals"],
                "techniques": ["drawing_basics", "color_basics"],
                "focus_areas": ["drawing"]
            }
    
    async def calculate_behavioral_scores(self, behavior_data: Dict[str, Any]) -> Dict[str, float]:
        """Calculate various behavioral scores."""
        
        return {
            "consistency": min(1.0, behavior_data.get("engagement_level", 0.5)),
            "curiosity": min(1.0, len(behavior_data.get("artwork_scores", [])) / 10.0),
            "persistence": min(1.0, behavior_data.get("avg_performance", 0.5)),
            "collaboration": 0.5,  # Default for now
            "motivation": min(1.0, behavior_data.get("engagement_level", 0.5) * 1.2),
            "confidence": min(1.0, behavior_data.get("avg_performance", 0.5) * 1.1)
        }
    
    # Additional helper methods would be implemented here...
    
    async def get_current_user_context(self, user_id: str) -> Dict[str, Any]:
        """Get current user context for recommendations."""
        return {
            "time_of_day": datetime.now().hour,
            "day_of_week": datetime.now().weekday(),
            "recent_performance": 0.75  # Placeholder
        }
    
    def generate_difficulty_curve(
        self, 
        preference: DifficultyPreference, 
        current_level: float, 
        num_lessons: int
    ) -> List[float]:
        """Generate difficulty progression curve."""
        
        if preference == DifficultyPreference.GRADUAL_PROGRESSION:
            # Gentle increase
            return [current_level + i * 0.02 for i in range(num_lessons)]
        elif preference == DifficultyPreference.CHALLENGE_SEEKER:
            # Steeper increase
            return [current_level + i * 0.05 for i in range(num_lessons)]
        else:  # ADAPTIVE
            # Variable progression
            return [current_level + np.sin(i * 0.3) * 0.1 + i * 0.03 for i in range(num_lessons)]
    
    # Placeholder methods for recommendation generation
    async def recommend_skill_building_content(self, user_id: str, profile: UserPersonalizationProfile, context: Dict[str, Any]) -> List[PersonalizedRecommendation]:
        return []
    
    async def recommend_interest_based_content(self, user_id: str, profile: UserPersonalizationProfile) -> List[PersonalizedRecommendation]:
        return []
    
    async def recommend_performance_improvement(self, user_id: str, profile: UserPersonalizationProfile) -> List[PersonalizedRecommendation]:
        return []
    
    async def recommend_social_activities(self, user_id: str, profile: UserPersonalizationProfile) -> List[PersonalizedRecommendation]:
        return []
    
    # Additional placeholder methods...
    async def find_relevant_content_for_goal(self, goal: LearningGoal) -> List[Dict[str, Any]]:
        return []
    
    async def organize_content_for_user(self, content: List[Dict[str, Any]], profile: UserPersonalizationProfile, difficulty_curve: List[float]) -> List[Dict[str, Any]]:
        return content
    
    def estimate_completion_time(self, num_lessons: int, learning_velocity: float) -> int:
        return max(1, int(num_lessons / learning_velocity))
    
    async def predict_completion_likelihood(self, user_id: str, profile: UserPersonalizationProfile, goal: LearningGoal) -> float:
        return profile.persistence_score * profile.motivation_level
    
    # More placeholder methods for completeness...
    async def calculate_difficulty_adjustment(self, content_id: str, user_level: float) -> float:
        return 0.0
    
    def get_content_emphasis_for_learning_style(self, learning_style: LearningStyle) -> Dict[str, float]:
        return {"visual_elements": 0.8, "interactive_elements": 0.6}
    
    async def get_relevant_additional_resources(self, content_id: str, profile: UserPersonalizationProfile) -> List[str]:
        return []
    
    async def generate_adaptive_scaffolding(self, content_id: str, profile: UserPersonalizationProfile) -> Dict[str, List[str]]:
        return {"prerequisites": [], "reinforcements": [], "extensions": []}
    
    def get_explanation_style(self, learning_style: LearningStyle) -> str:
        style_map = {
            LearningStyle.VISUAL: "visual_focused",
            LearningStyle.KINESTHETIC: "hands_on",
            LearningStyle.AUDITORY: "verbal_detailed",
            LearningStyle.READING_WRITING: "text_based",
            LearningStyle.MULTIMODAL: "comprehensive"
        }
        return style_map.get(learning_style, "balanced")
    
    def get_visual_preferences(self, profile: UserPersonalizationProfile) -> List[str]:
        return ["diagrams", "step_by_step_images", "example_artwork"]
    
    def get_interaction_preferences(self, profile: UserPersonalizationProfile) -> List[str]:
        return ["guided_practice", "interactive_exercises", "immediate_feedback"]
    
    # Insight generation methods (placeholders)
    async def analyze_interaction_for_insights(self, interaction_data: Dict[str, Any]) -> List[str]:
        return []
    
    async def analyze_learning_velocity_patterns(self, user_id: str, profile: UserPersonalizationProfile) -> Optional[PersonalizationInsight]:
        return None
    
    async def analyze_engagement_effectiveness(self, user_id: str, profile: UserPersonalizationProfile) -> Optional[PersonalizationInsight]:
        return None
    
    async def analyze_difficulty_optimization(self, user_id: str, profile: UserPersonalizationProfile) -> Optional[PersonalizationInsight]:
        return None
    
    async def analyze_content_type_effectiveness(self, user_id: str, profile: UserPersonalizationProfile) -> Optional[PersonalizationInsight]:
        return None
