"""
Tests for app/services/user_service.py

All repository calls are mocked — no database required.
"""

import uuid
import pytest
from unittest.mock import MagicMock, patch
from fastapi import HTTPException

from app.services.user_service import UserService
from app.entities.schemas import UserCreate, UserUpdate
from tests.conftest import make_user


@pytest.fixture
def mock_repo():
    return MagicMock()


@pytest.fixture
def service(mock_db, mock_repo):
    svc = UserService(mock_db)
    svc.repository = mock_repo
    return svc


# ─── create_user ──────────────────────────────────────────────────────────────

class TestCreateUser:

    def test_creates_user_when_email_is_new(self, service, mock_repo):
        mock_repo.get_by_email.return_value = None
        created = make_user(name="Alice", email="alice@test.com")
        mock_repo.create.return_value = created

        user_in = UserCreate(name="Alice", email="alice@test.com", password="password123")
        result = service.create_user(user_in)

        assert result.name == "Alice"
        mock_repo.create.assert_called_once()

    def test_raises_400_when_email_already_exists(self, service, mock_repo):
        existing = make_user(email="dup@test.com")
        mock_repo.get_by_email.return_value = existing

        user_in = UserCreate(name="Dup", email="dup@test.com", password="password123")
        with pytest.raises(HTTPException) as exc_info:
            service.create_user(user_in)
        assert exc_info.value.status_code == 400

    def test_password_is_hashed_before_storage(self, service, mock_repo):
        mock_repo.get_by_email.return_value = None
        mock_repo.create.return_value = make_user()

        user_in = UserCreate(name="Bob", email="bob@test.com", password="plaintext99")
        service.create_user(user_in)

        # The hashed_password argument passed to repository.create should differ from plain
        call_args = mock_repo.create.call_args
        hashed = call_args[0][1]  # second positional arg
        assert hashed != "plaintext99"
        assert len(hashed) > 10


# ─── authenticate_user ────────────────────────────────────────────────────────

class TestAuthenticateUser:

    def test_valid_credentials_return_user(self, service, mock_repo):
        from app.auth.security import get_password_hash
        user = make_user(email="a@b.com", hashed_password=get_password_hash("correct"))
        mock_repo.get_by_email.return_value = user

        result = service.authenticate_user("a@b.com", "correct")
        assert result is user

    def test_wrong_password_returns_none(self, service, mock_repo):
        from app.auth.security import get_password_hash
        user = make_user(hashed_password=get_password_hash("correct"))
        mock_repo.get_by_email.return_value = user

        result = service.authenticate_user("a@b.com", "wrong")
        assert result is None

    def test_nonexistent_email_returns_none(self, service, mock_repo):
        mock_repo.get_by_email.return_value = None
        result = service.authenticate_user("nobody@test.com", "anything")
        assert result is None

    def test_inactive_user_returns_none(self, service, mock_repo):
        from app.auth.security import get_password_hash
        user = make_user(hashed_password=get_password_hash("correct"), is_active=False)
        mock_repo.get_by_email.return_value = user

        result = service.authenticate_user("a@b.com", "correct")
        assert result is None


# ─── get_user ─────────────────────────────────────────────────────────────────

class TestGetUser:

    def test_returns_active_user(self, service, mock_repo):
        user = make_user()
        mock_repo.get_by_id.return_value = user
        result = service.get_user(user.id)
        assert result is user

    def test_returns_none_for_inactive_user(self, service, mock_repo):
        user = make_user(is_active=False)
        mock_repo.get_by_id.return_value = user
        result = service.get_user(user.id)
        assert result is None

    def test_returns_none_when_not_found(self, service, mock_repo):
        mock_repo.get_by_id.return_value = None
        result = service.get_user(uuid.uuid4())
        assert result is None


# ─── update_user ──────────────────────────────────────────────────────────────

class TestUpdateUser:

    def test_updates_existing_user(self, service, mock_repo):
        user = make_user()
        updated = make_user(name="Updated")
        mock_repo.get_by_id.return_value = user
        mock_repo.update.return_value = updated

        result = service.update_user(user.id, UserUpdate(name="Updated"))
        assert result.name == "Updated"

    def test_raises_404_when_user_not_found(self, service, mock_repo):
        mock_repo.get_by_id.return_value = None
        with pytest.raises(HTTPException) as exc_info:
            service.update_user(uuid.uuid4(), UserUpdate(name="Ghost"))
        assert exc_info.value.status_code == 404


# ─── delete_user ──────────────────────────────────────────────────────────────

class TestDeleteUser:

    def test_deletes_active_user_returns_true(self, service, mock_repo):
        user = make_user()
        mock_repo.get_by_id.return_value = user
        mock_repo.delete.return_value = True

        assert service.delete_user(user.id) is True

    def test_returns_false_when_user_not_found(self, service, mock_repo):
        mock_repo.get_by_id.return_value = None
        assert service.delete_user(uuid.uuid4()) is False
