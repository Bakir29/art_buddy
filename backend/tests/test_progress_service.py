"""
Tests for app/services/progress_service.py

UserService and LessonService dependencies are mocked.
"""

import uuid
import pytest
from unittest.mock import MagicMock, patch
from fastapi import HTTPException

from app.services.progress_service import ProgressService
from app.entities.schemas import ProgressCreate, ProgressUpdate
from tests.conftest import make_user, make_lesson, make_progress


@pytest.fixture
def mock_repo():
    return MagicMock()


@pytest.fixture
def mock_user_svc():
    return MagicMock()


@pytest.fixture
def mock_lesson_svc():
    return MagicMock()


@pytest.fixture
def service(mock_db, mock_repo, mock_user_svc, mock_lesson_svc):
    svc = ProgressService(mock_db)
    svc.repository = mock_repo
    svc.user_service = mock_user_svc
    svc.lesson_service = mock_lesson_svc
    return svc


# ─── create_progress ──────────────────────────────────────────────────────────

class TestCreateProgress:

    def test_creates_progress_for_valid_user_and_lesson(self, service, mock_repo, mock_user_svc, mock_lesson_svc):
        user = make_user()
        lesson = make_lesson()
        progress = make_progress(user_id=user.id, lesson_id=lesson.id)

        mock_user_svc.get_user.return_value = user
        mock_lesson_svc.get_lesson.return_value = lesson
        mock_repo.get_user_progress.return_value = None
        mock_repo.create.return_value = progress

        prog_in = ProgressCreate(user_id=user.id, lesson_id=lesson.id, completion_status="not_started")
        result = service.create_progress(prog_in)
        assert result.user_id == user.id
        mock_repo.create.assert_called_once()

    def test_raises_400_when_progress_already_exists(self, service, mock_repo, mock_user_svc, mock_lesson_svc):
        user = make_user()
        lesson = make_lesson()

        mock_user_svc.get_user.return_value = user
        mock_lesson_svc.get_lesson.return_value = lesson
        mock_repo.get_user_progress.return_value = make_progress()  # already exists

        prog_in = ProgressCreate(user_id=user.id, lesson_id=lesson.id, completion_status="not_started")
        with pytest.raises(HTTPException) as exc_info:
            service.create_progress(prog_in)
        assert exc_info.value.status_code == 400


# ─── get_progress ─────────────────────────────────────────────────────────────

class TestGetProgress:

    def test_returns_progress_when_found(self, service, mock_repo):
        progress = make_progress()
        mock_repo.get_by_id.return_value = progress
        result = service.get_progress(progress.id)
        assert result is progress

    def test_raises_404_when_not_found(self, service, mock_repo):
        mock_repo.get_by_id.return_value = None
        with pytest.raises(HTTPException) as exc_info:
            service.get_progress(uuid.uuid4())
        assert exc_info.value.status_code == 404


# ─── get_user_all_progress ────────────────────────────────────────────────────

class TestGetUserAllProgress:

    def test_returns_list_for_valid_user(self, service, mock_repo, mock_user_svc):
        user = make_user()
        records = [make_progress(user_id=user.id), make_progress(user_id=user.id)]
        mock_user_svc.get_user.return_value = user
        mock_repo.get_user_all_progress.return_value = records

        result = service.get_user_all_progress(user.id)
        assert len(result) == 2

    def test_raises_404_for_nonexistent_user(self, service, mock_user_svc):
        mock_user_svc.get_user.return_value = None
        with pytest.raises(HTTPException) as exc_info:
            service.get_user_all_progress(uuid.uuid4())
        assert exc_info.value.status_code == 404


# ─── update_progress ──────────────────────────────────────────────────────────

class TestUpdateProgress:

    def test_updates_progress_record(self, service, mock_repo):
        updated = make_progress(completion_status="completed", score=95.0)
        mock_repo.update.return_value = updated

        result = service.update_progress(uuid.uuid4(), ProgressUpdate(completion_status="completed", score=95.0))
        assert result.completion_status == "completed"
        assert result.score == 95.0

    def test_raises_404_when_record_not_found(self, service, mock_repo):
        mock_repo.update.return_value = None
        with pytest.raises(HTTPException) as exc_info:
            service.update_progress(uuid.uuid4(), ProgressUpdate(completion_status="completed"))
        assert exc_info.value.status_code == 404


# ─── start_lesson ─────────────────────────────────────────────────────────────

class TestStartLesson:

    def test_creates_new_in_progress_record_when_no_existing(self, service, mock_repo):
        new_progress = make_progress(completion_status="in_progress")
        mock_repo.get_user_progress.return_value = None
        mock_repo.create.return_value = new_progress

        uid = uuid.uuid4()
        lid = uuid.uuid4()
        result = service.start_lesson(uid, lid)
        assert result.completion_status == "in_progress"

    def test_updates_not_started_to_in_progress(self, service, mock_repo):
        existing = make_progress(completion_status="not_started")
        updated = make_progress(completion_status="in_progress")
        mock_repo.get_user_progress.return_value = existing
        mock_repo.update.return_value = updated

        result = service.start_lesson(existing.user_id, existing.lesson_id)
        assert result.completion_status == "in_progress"
