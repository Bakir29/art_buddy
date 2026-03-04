"""
Quiz Service

Business logic for quiz management and evaluation.
"""

from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from uuid import UUID
from datetime import datetime

from ..repositories.quiz_repository import QuizRepository, QuizCreate, QuizUpdate, Quiz


class QuizService:
    """Service for quiz operations"""
    
    def __init__(self, db: Session):
        self.db = db
        self.quiz_repository = QuizRepository(db)
    
    async def get_quiz(self, quiz_id: int) -> Optional[Quiz]:
        """Get quiz by ID"""
        return self.quiz_repository.get_quiz_by_id(quiz_id)
    
    async def get_quizzes_for_lesson(self, lesson_id: int) -> List[Quiz]:
        """Get all quizzes for a lesson"""
        return self.quiz_repository.get_quizzes_by_lesson(lesson_id)
    
    async def create_quiz(self, quiz_data: QuizCreate) -> Quiz:
        """Create a new quiz"""
        return self.quiz_repository.create_quiz(quiz_data)
    
    async def update_quiz(self, quiz_id: int, quiz_update: QuizUpdate) -> Optional[Quiz]:
        """Update quiz"""
        return self.quiz_repository.update_quiz(quiz_id, quiz_update)
    
    async def delete_quiz(self, quiz_id: int) -> bool:
        """Delete quiz"""
        return self.quiz_repository.delete_quiz(quiz_id)
    
    async def evaluate_quiz_submission(
        self,
        user_id: UUID,
        quiz_id: int,
        answers: Dict[int, Any],
        time_taken_minutes: Optional[int] = None
    ) -> Dict[str, Any]:
        """Evaluate quiz submission and provide feedback"""
        
        quiz = await self.get_quiz(quiz_id)
        if not quiz:
            raise ValueError(f"Quiz {quiz_id} not found")
        
        # Parse quiz questions and correct answers
        questions = quiz.questions_data if hasattr(quiz, 'questions_data') else []
        if not questions:
            # Fallback: generate mock evaluation for development
            return self._generate_mock_evaluation(user_id, quiz_id, answers, time_taken_minutes)
        
        correct_answers = 0
        total_questions = len(questions)
        detailed_feedback = []
        areas_to_review = []
        
        for question in questions:
            question_id = question.get('id')
            correct_answer = question.get('correct_answer')
            user_answer = answers.get(question_id)
            
            is_correct = self._evaluate_answer(user_answer, correct_answer, question.get('type', 'multiple_choice'))
            
            if is_correct:
                correct_answers += 1
            else:
                topic = question.get('topic', 'General')
                if topic not in areas_to_review:
                    areas_to_review.append(topic)
            
            detailed_feedback.append({
                "question_id": question_id,
                "question": question.get('question', ''),
                "user_answer": user_answer,
                "correct_answer": correct_answer,
                "is_correct": is_correct,
                "explanation": question.get('explanation', ''),
                "topic": topic
            })
        
        score_percentage = (correct_answers / total_questions * 100) if total_questions > 0 else 0
        
        # Generate overall feedback and recommendations
        overall_feedback = self._generate_overall_feedback(score_percentage, areas_to_review)
        recommended_actions = self._generate_recommendations(score_percentage, areas_to_review)
        
        return {
            "quiz_id": quiz_id,
            "user_id": str(user_id),
            "total_questions": total_questions,
            "correct_answers": correct_answers,
            "score_percentage": round(score_percentage, 1),
            "time_taken_minutes": time_taken_minutes or 0,
            "detailed_feedback": detailed_feedback,
            "overall_feedback": overall_feedback,
            "areas_to_review": areas_to_review,
            "recommended_actions": recommended_actions,
            "evaluated_at": datetime.utcnow().isoformat()
        }
    
    def _evaluate_answer(self, user_answer: Any, correct_answer: Any, question_type: str) -> bool:
        """Evaluate a single answer based on question type"""
        
        if question_type == 'multiple_choice':
            return str(user_answer).lower() == str(correct_answer).lower()
        elif question_type == 'true_false':
            return bool(user_answer) == bool(correct_answer)
        elif question_type == 'text':
            # Simple text comparison (could be enhanced with fuzzy matching)
            return str(user_answer).lower().strip() == str(correct_answer).lower().strip()
        elif question_type == 'numeric':
            try:
                return abs(float(user_answer) - float(correct_answer)) < 0.01
            except (ValueError, TypeError):
                return False
        else:
            return str(user_answer) == str(correct_answer)
    
    def _generate_overall_feedback(self, score_percentage: float, areas_to_review: List[str]) -> str:
        """Generate overall feedback based on performance"""
        
        if score_percentage >= 90:
            return f"Excellent work! You scored {score_percentage}% and demonstrate strong understanding of the material."
        elif score_percentage >= 80:
            return f"Great job! You scored {score_percentage}%. You have a good grasp of most concepts."
        elif score_percentage >= 70:
            return f"Good effort! You scored {score_percentage}%. There are a few areas to review for better understanding."
        elif score_percentage >= 60:
            return f"You scored {score_percentage}%. Consider reviewing the material and practicing more on the topics you missed."
        else:
            return f"You scored {score_percentage}%. Don't worry - learning is a process! Focus on reviewing the fundamentals."
    
    def _generate_recommendations(self, score_percentage: float, areas_to_review: List[str]) -> List[str]:
        """Generate action recommendations based on performance"""
        
        recommendations = []
        
        if score_percentage < 70:
            recommendations.append("Review the lesson materials thoroughly")
            recommendations.append("Practice with additional exercises")
        
        if areas_to_review:
            for area in areas_to_review[:3]:  # Limit to top 3 areas
                recommendations.append(f"Focus extra attention on {area}")
        
        if score_percentage >= 80:
            recommendations.append("You're ready to move on to the next lesson")
        elif score_percentage >= 60:
            recommendations.append("Consider retaking the quiz after review")
        else:
            recommendations.append("Review the fundamentals before retaking")
            recommendations.append("Consider reaching out for additional help")
        
        return recommendations
    
    def _generate_mock_evaluation(self, user_id: UUID, quiz_id: int, answers: Dict[int, Any], time_taken_minutes: Optional[int]) -> Dict[str, Any]:
        """Generate mock evaluation for development/testing"""
        
        # Simulate evaluation results
        total_questions = len(answers)
        correct_answers = max(1, int(total_questions * 0.75))  # Assume 75% correct
        score_percentage = (correct_answers / total_questions * 100) if total_questions > 0 else 0
        
        detailed_feedback = []
        for question_id, answer in answers.items():
            is_correct = hash(f"{question_id}{answer}") % 4 != 0  # Mock 75% success rate
            detailed_feedback.append({
                "question_id": question_id,
                "question": f"Mock question {question_id}",
                "user_answer": answer,
                "correct_answer": "Mock correct answer",
                "is_correct": is_correct,
                "explanation": "This is a mock explanation for development.",
                "topic": "Art Fundamentals"
            })
        
        return {
            "quiz_id": quiz_id,
            "user_id": str(user_id),
            "total_questions": total_questions,
            "correct_answers": correct_answers,
            "score_percentage": round(score_percentage, 1),
            "time_taken_minutes": time_taken_minutes or 15,
            "detailed_feedback": detailed_feedback,
            "overall_feedback": f"Mock evaluation complete. You scored {score_percentage}%.",
            "areas_to_review": ["Color Theory", "Composition"] if score_percentage < 80 else [],
            "recommended_actions": ["Practice more", "Review fundamentals"],
            "evaluated_at": datetime.utcnow().isoformat()
        }
