"""
Shared fixtures for Art Buddy unit tests.
All database calls are mocked — no live DB connection required.
"""

import uuid
from datetime import datetime
from unittest.mock import MagicMock, patch
import pytest

from app.entities.models import User, Lesson, Progress, QuizQuestion


# ─── Model factories ──────────────────────────────────────────────────────────

def make_user(**kwargs) -> User:
    user = User()
    user.id = kwargs.get("id", uuid.uuid4())
    user.name = kwargs.get("name", "Test User")
    user.email = kwargs.get("email", "test@example.com")
    user.hashed_password = kwargs.get("hashed_password", "hashed_pw")
    user.skill_level = kwargs.get("skill_level", "beginner")
    user.is_active = kwargs.get("is_active", True)
    user.created_at = kwargs.get("created_at", datetime.utcnow())
    user.updated_at = None
    return user


def make_lesson(**kwargs) -> Lesson:
    lesson = Lesson()
    lesson.id = kwargs.get("id", uuid.uuid4())
    lesson.title = kwargs.get("title", "Test Lesson")
    lesson.content = kwargs.get("content", "Lesson content here.")
    lesson.difficulty = kwargs.get("difficulty", "beginner")
    lesson.category = kwargs.get("category", "drawing")
    lesson.order_in_category = kwargs.get("order_in_category", 1)
    lesson.lesson_type = kwargs.get("lesson_type", "tutorial")
    lesson.duration_minutes = kwargs.get("duration_minutes", 30)
    lesson.prerequisites = kwargs.get("prerequisites", [])
    lesson.is_active = kwargs.get("is_active", True)
    lesson.created_at = kwargs.get("created_at", datetime.utcnow())
    return lesson


def make_progress(**kwargs) -> Progress:
    progress = Progress()
    progress.id = kwargs.get("id", uuid.uuid4())
    progress.user_id = kwargs.get("user_id", uuid.uuid4())
    progress.lesson_id = kwargs.get("lesson_id", uuid.uuid4())
    progress.completion_status = kwargs.get("completion_status", "not_started")
    progress.score = kwargs.get("score", None)
    progress.time_spent_minutes = kwargs.get("time_spent_minutes", 0)
    progress.attempts = kwargs.get("attempts", 0)
    progress.started_at = kwargs.get("started_at", None)
    progress.completed_at = kwargs.get("completed_at", None)
    return progress


# ─── Fixtures ─────────────────────────────────────────────────────────────────

@pytest.fixture
def mock_db():
    """Return a MagicMock that stands in for a SQLAlchemy Session."""
    return MagicMock()


@pytest.fixture
def sample_user():
    return make_user()


@pytest.fixture
def sample_lesson():
    return make_lesson()


@pytest.fixture
def sample_progress(sample_user, sample_lesson):
    return make_progress(user_id=sample_user.id, lesson_id=sample_lesson.id)
