"""
Tests for app/services/quiz_service.py

Focuses on pure business logic methods that need no DB.
"""

import uuid
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime

from app.services.quiz_service import QuizService


@pytest.fixture
def service(mock_db):
    svc = QuizService(mock_db)
    svc.quiz_repository = MagicMock()
    return svc


# ─── _evaluate_answer ─────────────────────────────────────────────────────────

class TestEvaluateAnswer:

    def test_multiple_choice_exact_match(self, service):
        assert service._evaluate_answer("A", "A", "multiple_choice") is True

    def test_multiple_choice_case_insensitive(self, service):
        assert service._evaluate_answer("a", "A", "multiple_choice") is True

    def test_multiple_choice_wrong_answer(self, service):
        assert service._evaluate_answer("B", "A", "multiple_choice") is False

    def test_true_false_correct_true(self, service):
        assert service._evaluate_answer(True, True, "true_false") is True

    def test_true_false_correct_false(self, service):
        assert service._evaluate_answer(False, False, "true_false") is True

    def test_true_false_mismatch(self, service):
        assert service._evaluate_answer(True, False, "true_false") is False

    def test_text_case_insensitive_match(self, service):
        assert service._evaluate_answer("  Red  ", "red", "text") is True

    def test_text_wrong_answer(self, service):
        assert service._evaluate_answer("Blue", "Red", "text") is False

    def test_numeric_within_tolerance(self, service):
        assert service._evaluate_answer(3.14159, 3.14159, "numeric") is True

    def test_numeric_out_of_tolerance(self, service):
        assert service._evaluate_answer(3.0, 3.14159, "numeric") is False

    def test_numeric_invalid_input_returns_false(self, service):
        assert service._evaluate_answer("not-a-number", 42, "numeric") is False

    def test_unknown_type_falls_back_to_string_equality(self, service):
        assert service._evaluate_answer("x", "x", "custom") is True
        assert service._evaluate_answer("x", "y", "custom") is False


# ─── _generate_overall_feedback ───────────────────────────────────────────────

class TestGenerateOverallFeedback:

    def test_score_90_plus_gives_excellent(self, service):
        feedback = service._generate_overall_feedback(95.0, [])
        assert "Excellent" in feedback

    def test_score_80_to_89_gives_great(self, service):
        feedback = service._generate_overall_feedback(85.0, [])
        assert "Great" in feedback

    def test_score_70_to_79_gives_good(self, service):
        feedback = service._generate_overall_feedback(75.0, [])
        assert "Good" in feedback

    def test_score_below_60_includes_encouragement(self, service):
        feedback = service._generate_overall_feedback(40.0, ["Color Theory"])
        assert "40.0" in feedback

    def test_feedback_includes_score(self, service):
        feedback = service._generate_overall_feedback(72.5, [])
        assert "72.5" in feedback


# ─── _generate_recommendations ────────────────────────────────────────────────

class TestGenerateRecommendations:

    def test_high_score_suggests_next_lesson(self, service):
        recs = service._generate_recommendations(90.0, [])
        assert any("next lesson" in r.lower() for r in recs)

    def test_low_score_suggests_review(self, service):
        recs = service._generate_recommendations(50.0, [])
        assert any("review" in r.lower() for r in recs)

    def test_areas_to_review_are_included(self, service):
        recs = service._generate_recommendations(60.0, ["Color Theory", "Composition"])
        assert any("Color Theory" in r for r in recs)

    def test_max_3_area_recommendations(self, service):
        areas = ["Area A", "Area B", "Area C", "Area D", "Area E"]
        recs = service._generate_recommendations(55.0, areas)
        area_recs = [r for r in recs if "Focus" in r]
        assert len(area_recs) <= 3


# ─── _generate_mock_evaluation ────────────────────────────────────────────────

class TestGenerateMockEvaluation:

    def test_returns_dict_with_expected_keys(self, service):
        uid = uuid.uuid4()
        answers = {1: "A", 2: "B", 3: "C", 4: "D"}
        result = service._generate_mock_evaluation(uid, 42, answers, 10)

        required_keys = {
            "quiz_id", "user_id", "total_questions", "correct_answers",
            "score_percentage", "time_taken_minutes", "detailed_feedback",
            "overall_feedback", "areas_to_review", "recommended_actions", "evaluated_at"
        }
        assert required_keys.issubset(result.keys())

    def test_total_questions_matches_answers(self, service):
        uid = uuid.uuid4()
        answers = {1: "A", 2: "B", 3: "C"}
        result = service._generate_mock_evaluation(uid, 1, answers, 0)
        assert result["total_questions"] == 3

    def test_score_percentage_between_0_and_100(self, service):
        uid = uuid.uuid4()
        answers = {i: "A" for i in range(10)}
        result = service._generate_mock_evaluation(uid, 1, answers, 5)
        assert 0 <= result["score_percentage"] <= 100

    def test_empty_answers_returns_zero_score(self, service):
        uid = uuid.uuid4()
        result = service._generate_mock_evaluation(uid, 1, {}, None)
        assert result["score_percentage"] == 0
        assert result["total_questions"] == 0
