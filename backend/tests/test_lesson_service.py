"""
Tests for app/services/lesson_service.py

All repository calls are mocked — no database required.
"""

import uuid
import pytest
from unittest.mock import MagicMock
from fastapi import HTTPException

from app.services.lesson_service import LessonService
from app.entities.schemas import LessonCreate, LessonUpdate
from tests.conftest import make_lesson


@pytest.fixture
def mock_repo():
    return MagicMock()


@pytest.fixture
def service(mock_db, mock_repo):
    svc = LessonService(mock_db)
    svc.repository = mock_repo
    return svc


# ─── get_lesson ───────────────────────────────────────────────────────────────

class TestGetLesson:

    def test_returns_lesson_when_found(self, service, mock_repo):
        lesson = make_lesson()
        mock_repo.get_by_id.return_value = lesson
        result = service.get_lesson(lesson.id)
        assert result is lesson

    def test_raises_404_when_not_found(self, service, mock_repo):
        mock_repo.get_by_id.return_value = None
        with pytest.raises(HTTPException) as exc_info:
            service.get_lesson(uuid.uuid4())
        assert exc_info.value.status_code == 404


# ─── get_lessons filtering ────────────────────────────────────────────────────

class TestGetLessons:

    def test_get_all_when_no_filter(self, service, mock_repo):
        lessons = [make_lesson(), make_lesson()]
        mock_repo.get_all.return_value = lessons
        result = service.get_lessons()
        mock_repo.get_all.assert_called_once()
        assert len(result) == 2

    def test_filters_by_difficulty(self, service, mock_repo):
        lessons = [make_lesson(difficulty="advanced")]
        mock_repo.get_by_difficulty.return_value = lessons
        result = service.get_lessons(difficulty="advanced")
        mock_repo.get_by_difficulty.assert_called_once_with("advanced", skip=0, limit=100)
        assert result[0].difficulty == "advanced"

    def test_filters_by_lesson_type(self, service, mock_repo):
        lessons = [make_lesson(lesson_type="exercise")]
        mock_repo.get_by_type.return_value = lessons
        result = service.get_lessons(lesson_type="exercise")
        mock_repo.get_by_type.assert_called_once_with("exercise", skip=0, limit=100)

    def test_searches_by_text(self, service, mock_repo):
        lessons = [make_lesson(title="Color Theory Basics")]
        mock_repo.search_lessons.return_value = lessons
        result = service.get_lessons(search="color")
        mock_repo.search_lessons.assert_called_once_with("color", skip=0, limit=100)


# ─── create_lesson ────────────────────────────────────────────────────────────

class TestCreateLesson:

    def test_creates_and_returns_lesson(self, service, mock_repo):
        new_lesson = make_lesson(title="Watercolor Basics")
        mock_repo.create.return_value = new_lesson

        lesson_in = LessonCreate(
            title="Watercolor Basics",
            content="Content here",
            difficulty="beginner",
        )
        result = service.create_lesson(lesson_in)
        assert result.title == "Watercolor Basics"
        mock_repo.create.assert_called_once_with(lesson_in)


# ─── update_lesson ────────────────────────────────────────────────────────────

class TestUpdateLesson:

    def test_updates_and_returns_lesson(self, service, mock_repo):
        updated = make_lesson(title="New Title")
        mock_repo.update.return_value = updated

        result = service.update_lesson(uuid.uuid4(), LessonUpdate(title="New Title"))
        assert result.title == "New Title"

    def test_raises_404_when_not_found(self, service, mock_repo):
        mock_repo.update.return_value = None
        with pytest.raises(HTTPException) as exc_info:
            service.update_lesson(uuid.uuid4(), LessonUpdate(title="Ghost"))
        assert exc_info.value.status_code == 404


# ─── delete_lesson ────────────────────────────────────────────────────────────

class TestDeleteLesson:

    def test_deletes_existing_lesson(self, service, mock_repo):
        mock_repo.delete.return_value = True
        result = service.delete_lesson(uuid.uuid4())
        assert result is True

    def test_raises_404_when_lesson_not_found(self, service, mock_repo):
        mock_repo.delete.return_value = False
        with pytest.raises(HTTPException) as exc_info:
            service.delete_lesson(uuid.uuid4())
        assert exc_info.value.status_code == 404


# ─── validate_prerequisites ───────────────────────────────────────────────────

class TestValidatePrerequisites:

    def test_no_prerequisites_returns_true(self, service, mock_repo):
        lesson = make_lesson(prerequisites=[])
        mock_repo.get_by_id.return_value = lesson
        assert service.validate_prerequisites(lesson.id) is True

    def test_missing_prerequisite_returns_false(self, service, mock_repo):
        prereq_id = uuid.uuid4()
        lesson = make_lesson(prerequisites=[prereq_id])

        def side_effect(lid):
            if lid == lesson.id:
                return lesson
            return None  # prereq not found

        mock_repo.get_by_id.side_effect = side_effect
        assert service.validate_prerequisites(lesson.id) is False

    def test_all_prerequisites_exist_returns_true(self, service, mock_repo):
        prereq = make_lesson()
        lesson = make_lesson(prerequisites=[prereq.id])

        def side_effect(lid):
            if lid == lesson.id:
                return lesson
            return prereq

        mock_repo.get_by_id.side_effect = side_effect
        assert service.validate_prerequisites(lesson.id) is True

    def test_nonexistent_lesson_returns_true(self, service, mock_repo):
        mock_repo.get_by_id.return_value = None
        assert service.validate_prerequisites(uuid.uuid4()) is True
