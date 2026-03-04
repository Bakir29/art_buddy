import base64
import uuid
import io
from typing import List, Dict, Any, Tuple, Optional
from PIL import Image
import openai
from sqlalchemy.orm import Session

from app.entities.image_analysis import (
    ImageAnalysisRequest, ImageAnalysisResult, AnalysisInsight, 
    AnalysisType, ArtworkType, ImageAnalysisEntity
)
from app.repositories.image_analysis_repository import ImageAnalysisRepository
from app.rag.rag_service import RAGService
from app.services.file_service import FileService

class ImageAnalysisService:
    def __init__(self, db: Session, openai_client, rag_service: RAGService, file_service: FileService):
        self.db = db
        self.openai_client = openai_client
        self.rag_service = rag_service
        self.file_service = file_service
        self.repository = ImageAnalysisRepository(db)
    
    async def analyze_artwork(self, user_id: str, request: ImageAnalysisRequest) -> ImageAnalysisResult:
        """Main method to analyze artwork using AI vision and provide educational feedback."""
        
        # 1. Process and validate image
        processed_image = await self._process_image(request.image_data)
        
        # 2. Save image to storage
        image_url = await self._save_image(processed_image, user_id)
        
        # 3. Generate AI analysis for each requested type
        insights = []
        for analysis_type in request.analysis_types:
            insight = await self._generate_analysis_insight(
                processed_image, analysis_type, request.artwork_type, 
                request.user_context, request.skill_level
            )
            insights.append(insight)
        
        # 4. Calculate overall score and generate comprehensive summary
        overall_score = self._calculate_overall_score(insights)
        ai_summary = await self._generate_comprehensive_summary(insights, request.artwork_type)
        
        # 5. Get personalized recommendations from RAG
        recommended_resources = await self._get_contextual_recommendations(
            insights, request.artwork_type, request.skill_level
        )
        
        # 6. Generate next steps
        next_steps = await self._generate_next_steps(insights, request.skill_level)
        
        # 7. Create analysis result
        analysis_result = ImageAnalysisResult(
            id=str(uuid.uuid4()),
            user_id=user_id,
            image_url=image_url,
            artwork_type=request.artwork_type,
            analysis_timestamp=datetime.utcnow(),
            overall_score=overall_score,
            insights=insights,
            ai_summary=ai_summary,
            recommended_resources=recommended_resources,
            next_steps=next_steps
        )
        
        # 8. Save to database
        analysis_entity = ImageAnalysisEntity(
            user_id=user_id,
            image_url=image_url,
            artwork_type=request.artwork_type.value,
            analysis_data={
                "insights": [insight.model_dump() for insight in insights],
                "recommended_resources": recommended_resources,
                "next_steps": next_steps
            },
            overall_score=overall_score,
            ai_summary=ai_summary
        )
        
        await self.repository.create_analysis(analysis_entity)
        return analysis_result
    
    async def _process_image(self, image_data: str) -> str:
        """Process and validate uploaded image."""
        try:
            # Decode base64 image
            image_bytes = base64.b64decode(image_data)
            image = Image.open(io.BytesIO(image_bytes))
            
            # Validate image format
            if image.format not in ['JPEG', 'PNG', 'WEBP']:
                raise ValueError("Unsupported image format. Please use JPEG, PNG, or WEBP.")
            
            # Resize if too large (max 2048x2048 for vision API)
            if image.size[0] > 2048 or image.size[1] > 2048:
                image.thumbnail((2048, 2048), Image.Resampling.LANCZOS)
            
            # Convert back to base64
            buffer = io.BytesIO()
            image.save(buffer, format=image.format)
            return base64.b64encode(buffer.getvalue()).decode()
            
        except Exception as e:
            raise ValueError(f"Error processing image: {str(e)}")
    
    async def _save_image(self, processed_image: str, user_id: str) -> str:
        """Save processed image to storage and return URL."""
        filename = f"{user_id}_{uuid.uuid4().hex}.jpg"
        return await self.file_service.save_base64_image(processed_image, filename)
    
    async def _generate_analysis_insight(
        self, 
        image_data: str, 
        analysis_type: AnalysisType, 
        artwork_type: ArtworkType,
        user_context: Optional[str],
        skill_level: Optional[str]
    ) -> AnalysisInsight:
        """Generate specific analysis insight using OpenAI Vision."""
        
        # Create specialized prompts for each analysis type
        prompts = {
            AnalysisType.COMPOSITION: self._get_composition_prompt(artwork_type, skill_level),
            AnalysisType.COLOR_THEORY: self._get_color_theory_prompt(artwork_type, skill_level),
            AnalysisType.TECHNIQUE: self._get_technique_prompt(artwork_type, skill_level),
            AnalysisType.STYLE_IDENTIFICATION: self._get_style_prompt(artwork_type),
            AnalysisType.PROPORTIONS: self._get_proportions_prompt(artwork_type, skill_level),
            AnalysisType.LIGHTING: self._get_lighting_prompt(artwork_type, skill_level),
            AnalysisType.OVERALL_CRITIQUE: self._get_overall_critique_prompt(skill_level)
        }
        
        system_prompt = prompts[analysis_type]
        if user_context:
            system_prompt += f"\n\nUser's specific focus: {user_context}"
        
        try:
            response = await self.openai_client.chat.completions.create(
                model="gpt-4-vision-preview",
                messages=[
                    {
                        "role": "system",
                        "content": system_prompt
                    },
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": f"Please analyze this {artwork_type.value} artwork focusing on {analysis_type.value.replace('_', ' ')}. Provide constructive, educational feedback."
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{image_data}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=800
            )
            
            feedback_text = response.choices[0].message.content
            
            # Parse the structured response (expecting JSON-like format)
            parsed_response = self._parse_ai_feedback(feedback_text)
            
            return AnalysisInsight(
                type=analysis_type,
                score=parsed_response.get("score", 7.0),  # Default score if parsing fails
                feedback=parsed_response.get("feedback", feedback_text),
                suggestions=parsed_response.get("suggestions", []),
                strengths=parsed_response.get("strengths", []),
                areas_for_improvement=parsed_response.get("areas_for_improvement", [])
            )
            
        except Exception as e:
            print(f"Error in AI analysis: {str(e)}")
            # Fallback insight
            return AnalysisInsight(
                type=analysis_type,
                score=6.0,
                feedback=f"Analysis for {analysis_type.value} is temporarily unavailable. Please try again.",
                suggestions=["Review basic principles of art fundamentals"],
                strengths=["Artwork submitted for analysis"],
                areas_for_improvement=["Continue practicing and seek feedback"]
            )
    
    def _get_composition_prompt(self, artwork_type: ArtworkType, skill_level: Optional[str]) -> str:
        return f"""You are an expert art instructor analyzing the composition of a {artwork_type.value}. 
        Skill level: {skill_level or 'unknown'}. 
        
        Focus on: rule of thirds, focal points, balance, visual flow, negative space, and overall arrangement.
        
        Respond in this JSON format:
        {{
            "score": [0-10 rating],
            "feedback": "detailed analysis of composition",
            "strengths": ["list of compositional strengths"],
            "areas_for_improvement": ["specific areas to work on"],
            "suggestions": ["actionable tips for improvement"]
        }}"""
    
    def _get_color_theory_prompt(self, artwork_type: ArtworkType, skill_level: Optional[str]) -> str:
        return f"""You are an expert art instructor analyzing color theory in a {artwork_type.value}.
        Skill level: {skill_level or 'unknown'}.
        
        Focus on: color harmony, temperature, contrast, saturation, value relationships, and mood creation.
        
        Respond in this JSON format:
        {{
            "score": [0-10 rating],
            "feedback": "detailed color theory analysis",
            "strengths": ["list of color usage strengths"],
            "areas_for_improvement": ["specific color theory areas to work on"],
            "suggestions": ["actionable color improvement tips"]
        }}"""
    
    def _get_technique_prompt(self, artwork_type: ArtworkType, skill_level: Optional[str]) -> str:
        return f"""You are an expert art instructor analyzing technique in a {artwork_type.value}.
        Skill level: {skill_level or 'unknown'}.
        
        Focus on: medium-specific techniques, brush work/line quality, texture, blending, and technical execution.
        
        Respond in this JSON format:
        {{
            "score": [0-10 rating],
            "feedback": "detailed technique analysis",
            "strengths": ["list of technical strengths"],
            "areas_for_improvement": ["specific technical areas to develop"],
            "suggestions": ["actionable technique improvement tips"]
        }}"""
    
    def _get_style_prompt(self, artwork_type: ArtworkType) -> str:
        return f"""You are an art historian and expert instructor analyzing artistic style in a {artwork_type.value}.
        
        Identify: artistic movement/style influences, historical context, stylistic elements, and contemporary relevance.
        
        Respond in this JSON format:
        {{
            "score": [0-10 rating for style development],
            "feedback": "detailed style analysis and identification",
            "strengths": ["notable stylistic elements"],
            "areas_for_improvement": ["style development opportunities"],
            "suggestions": ["ways to develop personal artistic style"]
        }}"""
    
    def _get_proportions_prompt(self, artwork_type: ArtworkType, skill_level: Optional[str]) -> str:
        return f"""You are an expert art instructor analyzing proportions and form in a {artwork_type.value}.
        Skill level: {skill_level or 'unknown'}.
        
        Focus on: anatomical accuracy (if applicable), object proportions, scale relationships, and perspective.
        
        Respond in this JSON format:
        {{
            "score": [0-10 rating],
            "feedback": "detailed proportions analysis",
            "strengths": ["accurate proportional elements"],
            "areas_for_improvement": ["proportion issues to address"],
            "suggestions": ["methods to improve proportional accuracy"]
        }}"""
    
    def _get_lighting_prompt(self, artwork_type: ArtworkType, skill_level: Optional[str]) -> str:
        return f"""You are an expert art instructor analyzing lighting and shadows in a {artwork_type.value}.
        Skill level: {skill_level or 'unknown'}.
        
        Focus on: light source consistency, shadow accuracy, form modeling, atmospheric perspective, and dramatic effect.
        
        Respond in this JSON format:
        {{
            "score": [0-10 rating],
            "feedback": "detailed lighting analysis",
            "strengths": ["effective lighting elements"],
            "areas_for_improvement": ["lighting aspects to develop"],
            "suggestions": ["lighting technique improvements"]
        }}"""
    
    def _get_overall_critique_prompt(self, skill_level: Optional[str]) -> str:
        return f"""You are an expert art instructor providing an overall critique.
        Skill level: {skill_level or 'unknown'}.
        
        Provide holistic feedback considering: artistic impact, emotional expression, technical execution, originality, and overall effectiveness.
        
        Respond in this JSON format:
        {{
            "score": [0-10 overall rating],
            "feedback": "comprehensive overall assessment",
            "strengths": ["major artwork strengths"],
            "areas_for_improvement": ["key development areas"],
            "suggestions": ["primary recommendations for growth"]
        }}"""
    
    def _parse_ai_feedback(self, feedback_text: str) -> Dict[str, Any]:
        """Parse AI feedback, handling both JSON and text responses."""
        import json
        
        try:
            # Try to parse as JSON first
            if "{" in feedback_text and "}" in feedback_text:
                start_idx = feedback_text.find("{")
                end_idx = feedback_text.rfind("}") + 1
                json_str = feedback_text[start_idx:end_idx]
                return json.loads(json_str)
        except:
            pass
        
        # Fallback: extract information from text
        return {
            "score": 7.0,
            "feedback": feedback_text,
            "suggestions": [],
            "strengths": [],
            "areas_for_improvement": []
        }
    
    def _calculate_overall_score(self, insights: List[AnalysisInsight]) -> float:
        """Calculate weighted overall score from individual insights."""
        if not insights:
            return 0.0
        
        # Weight different analysis types
        weights = {
            AnalysisType.OVERALL_CRITIQUE: 0.3,
            AnalysisType.COMPOSITION: 0.2,
            AnalysisType.TECHNIQUE: 0.2,
            AnalysisType.COLOR_THEORY: 0.15,
            AnalysisType.PROPORTIONS: 0.1,
            AnalysisType.LIGHTING: 0.05,
            AnalysisType.STYLE_IDENTIFICATION: 0.05
        }
        
        total_weighted_score = 0.0
        total_weight = 0.0
        
        for insight in insights:
            weight = weights.get(insight.type, 0.1)
            total_weighted_score += insight.score * weight
            total_weight += weight
        
        return round(total_weighted_score / total_weight if total_weight > 0 else 0.0, 2)
    
    async def _generate_comprehensive_summary(self, insights: List[AnalysisInsight], artwork_type: ArtworkType) -> str:
        """Generate a comprehensive AI summary of all analysis insights."""
        summary_parts = [f"Analysis of your {artwork_type.value}:\n"]
        
        all_strengths = []
        all_improvements = []
        all_suggestions = []
        
        for insight in insights:
            summary_parts.append(f"**{insight.type.value.replace('_', ' ').title()}**: {insight.feedback}")
            all_strengths.extend(insight.strengths)
            all_improvements.extend(insight.areas_for_improvement)
            all_suggestions.extend(insight.suggestions)
        
        if all_strengths:
            summary_parts.append(f"\n**Key Strengths**: {', '.join(set(all_strengths[:3]))}")
        
        if all_improvements:
            summary_parts.append(f"\n**Focus Areas**: {', '.join(set(all_improvements[:3]))}")
        
        return " ".join(summary_parts)
    
    async def _get_contextual_recommendations(
        self, 
        insights: List[AnalysisInsight], 
        artwork_type: ArtworkType,
        skill_level: Optional[str]
    ) -> List[str]:
        """Get personalized learning resources using RAG system."""
        
        # Extract key areas for improvement
        focus_areas = []
        for insight in insights:
            focus_areas.extend(insight.areas_for_improvement)
        
        # Query RAG system for relevant resources
        search_queries = [
            f"{artwork_type.value} {area}" for area in focus_areas[:3]
        ]
        
        recommendations = []
        for query in search_queries:
            try:
                rag_results = await self.rag_service.search_knowledge_base(query, limit=2)
                for result in rag_results:
                    if result.title not in [r.split(":")[0] for r in recommendations]:
                        recommendations.append(f"{result.title}: {result.content[:100]}...")
            except:
                continue
        
        # Add default recommendations if RAG doesn't return enough
        if len(recommendations) < 2:
            default_recommendations = {
                ArtworkType.DRAWING: ["Basic Drawing Fundamentals", "Proportions and Perspective"],
                ArtworkType.PAINTING: ["Color Mixing Techniques", "Brushwork and Texture"],
                ArtworkType.DIGITAL_ART: ["Digital Painting Basics", "Layer Management"],
            }
            recommendations.extend(default_recommendations.get(artwork_type, ["Art Fundamentals"])[:2])
        
        return recommendations[:5]  # Return top 5 recommendations
    
    async def _generate_next_steps(self, insights: List[AnalysisInsight], skill_level: Optional[str]) -> List[str]:
        """Generate personalized next steps based on analysis."""
        next_steps = []
        
        # Collect suggestions from insights
        all_suggestions = []
        for insight in insights:
            all_suggestions.extend(insight.suggestions)
        
        # Prioritize based on skill level
        if skill_level == "beginner":
            next_steps = [
                "Focus on basic fundamentals first",
                "Practice daily sketching exercises",
                "Study master artworks for inspiration"
            ]
        elif skill_level == "advanced":
            next_steps = [
                "Experiment with new techniques or styles",
                "Consider developing a series of related works",
                "Share work for peer critique and feedback"
            ]
        else:  # intermediate or unknown
            next_steps = [
                "Continue practicing identified improvement areas",
                "Try new challenges to expand skills",
                "Document progress through regular practice"
            ]
        
        # Add specific suggestions from AI analysis
        if all_suggestions:
            next_steps.extend(all_suggestions[:2])
        
        return next_steps[:5]
    
    async def get_user_analysis_history(self, user_id: str) -> List[ImageAnalysisResult]:
        """Get user's analysis history."""
        entities = await self.repository.get_analyses_by_user(user_id)
        return [self._entity_to_result(entity) for entity in entities]
    
    async def get_analysis_by_id(self, analysis_id: str, user_id: str) -> Optional[ImageAnalysisResult]:
        """Get specific analysis by ID."""
        entity = await self.repository.get_analysis_by_id(analysis_id)
        if entity and entity.user_id == user_id:
            return self._entity_to_result(entity)
        return None
    
    async def get_user_analytics(self, user_id: str) -> Dict[str, Any]:
        """Get advanced analytics for user's artwork submissions."""
        return await self.repository.get_user_analytics(user_id)
    
    def _entity_to_result(self, entity: ImageAnalysisEntity) -> ImageAnalysisResult:
        """Convert entity to result format."""
        analysis_data = entity.analysis_data or {}
        insights = [
            AnalysisInsight(**insight_data) 
            for insight_data in analysis_data.get("insights", [])
        ]
        
        return ImageAnalysisResult(
            id=entity.id,
            user_id=entity.user_id,
            image_url=entity.image_url,
            artwork_type=ArtworkType(entity.artwork_type),
            analysis_timestamp=entity.created_at,
            overall_score=entity.overall_score,
            insights=insights,
            ai_summary=entity.ai_summary,
            recommended_resources=analysis_data.get("recommended_resources", []),
            next_steps=analysis_data.get("next_steps", [])
        )

# Import datetime for use in the service
from datetime import datetime
