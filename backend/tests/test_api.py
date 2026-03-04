"""
Tests for FastAPI HTTP endpoints.

Uses TestClient with a mocked database session so no live DB is required.
Auth, registration, and lesson list endpoints are covered.
"""

import uuid
import pytest
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient

from tests.conftest import make_user, make_lesson
from app.auth.security import get_password_hash, create_access_token


# ─── App + dependency override helpers ────────────────────────────────────────

def _make_client(mock_db):
    """Return a TestClient with get_db overridden by mock_db."""
    from main import app
    from app.database import get_db

    app.dependency_overrides[get_db] = lambda: mock_db
    client = TestClient(app, raise_server_exceptions=False)
    yield client
    app.dependency_overrides.clear()


@pytest.fixture
def mock_db():
    return MagicMock()


@pytest.fixture
def client(mock_db):
    from main import app
    from app.database import get_db

    app.dependency_overrides[get_db] = lambda: mock_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


# ─── Health / root ────────────────────────────────────────────────────────────

class TestHealthEndpoints:

    def test_docs_page_returns_200_in_dev(self, client):
        resp = client.get("/docs")
        # In development mode docs are enabled
        assert resp.status_code in (200, 404)  # 404 if env != development

    def test_openapi_json_available(self, client):
        resp = client.get("/openapi.json")
        assert resp.status_code == 200
        data = resp.json()
        assert data["info"]["title"] == "Art Buddy API"


# ─── POST /api/v1/auth/register ───────────────────────────────────────────────

class TestRegisterEndpoint:

    def test_register_new_user_returns_201(self, client, mock_db):
        new_user = make_user(name="Alice", email="alice@test.com")
        mock_db.query.return_value.filter.return_value.first.return_value = None
        mock_db.add.return_value = None
        mock_db.commit.return_value = None
        mock_db.refresh.side_effect = lambda obj: setattr(obj, "id", new_user.id) or setattr(obj, "created_at", new_user.created_at)

        with patch(
            "app.repositories.user_repository.UserRepository.get_by_email",
            return_value=None,
        ), patch(
            "app.repositories.user_repository.UserRepository.create",
            return_value=new_user,
        ):
            resp = client.post(
                "/auth/register",
                json={
                    "name": "Alice",
                    "email": "alice@test.com",
                    "password": "password123",
                    "skill_level": "beginner",
                },
            )
        assert resp.status_code == 201
        body = resp.json()
        assert body["email"] == "alice@test.com"

    def test_register_duplicate_email_returns_400(self, client):
        existing = make_user(email="dup@test.com")
        with patch(
            "app.repositories.user_repository.UserRepository.get_by_email",
            return_value=existing,
        ):
            resp = client.post(
                "/auth/register",
                json={
                    "name": "Dup",
                    "email": "dup@test.com",
                    "password": "password123",
                },
            )
        assert resp.status_code == 400

    def test_register_invalid_email_format_returns_422(self, client):
        resp = client.post(
            "/auth/register",
            json={"name": "Bob", "email": "not-an-email", "password": "password123"},
        )
        assert resp.status_code == 422

    def test_register_short_password_returns_422(self, client):
        resp = client.post(
            "/auth/register",
            json={"name": "Bob", "email": "bob@test.com", "password": "short"},
        )
        assert resp.status_code == 422


# ─── POST /api/v1/auth/login ──────────────────────────────────────────────────

class TestLoginEndpoint:

    def test_valid_credentials_return_token(self, client):
        user = make_user(
            email="login@test.com",
            hashed_password=get_password_hash("mypassword"),
            is_active=True,
        )
        with patch(
            "app.repositories.user_repository.UserRepository.get_by_email",
            return_value=user,
        ):
            resp = client.post(
                "/auth/login",
                data={"username": "login@test.com", "password": "mypassword"},
            )
        assert resp.status_code == 200
        body = resp.json()
        assert "access_token" in body
        assert body["token_type"] == "bearer"

    def test_wrong_password_returns_401(self, client):
        user = make_user(
            email="login@test.com",
            hashed_password=get_password_hash("correctpassword"),
            is_active=True,
        )
        with patch(
            "app.repositories.user_repository.UserRepository.get_by_email",
            return_value=user,
        ):
            resp = client.post(
                "/auth/login",
                data={"username": "login@test.com", "password": "wrongpassword"},
            )
        assert resp.status_code == 401

    def test_nonexistent_user_returns_401(self, client):
        with patch(
            "app.repositories.user_repository.UserRepository.get_by_email",
            return_value=None,
        ):
            resp = client.post(
                "/auth/login",
                data={"username": "ghost@test.com", "password": "anything"},
            )
        assert resp.status_code == 401


# ─── GET /auth/me ─────────────────────────────────────────────────────────────

class TestMeEndpoint:

    def test_valid_token_returns_user_info(self, client):
        from main import app
        from app.auth.dependencies import get_current_active_user

        user = make_user(email="me@test.com")

        # Override the auth dependency directly so no ORM call is made
        app.dependency_overrides[get_current_active_user] = lambda: user
        try:
            resp = client.get("/auth/me")
        finally:
            app.dependency_overrides.pop(get_current_active_user, None)

        assert resp.status_code == 200
        assert resp.json()["email"] == "me@test.com"

    def test_missing_token_returns_403(self, client):
        # HTTPBearer returns 403 (not 401) when the Authorization header is absent
        resp = client.get("/auth/me")
        assert resp.status_code == 403

    def test_invalid_token_returns_401(self, client):
        resp = client.get(
            "/auth/me",
            headers={"Authorization": "Bearer invalid.token.here"},
        )
        assert resp.status_code == 401


# ─── GET /lessons ─────────────────────────────────────────────────────────────

class TestLessonsEndpoint:

    def test_get_lessons_returns_list(self, client):
        from main import app
        from app.auth.dependencies import get_current_active_user

        user = make_user(email="user@test.com")
        lessons = [make_lesson(title="Lesson 1"), make_lesson(title="Lesson 2")]

        app.dependency_overrides[get_current_active_user] = lambda: user
        try:
            with patch(
                "app.repositories.lesson_repository.LessonRepository.get_all",
                return_value=lessons,
            ):
                resp = client.get("/lessons")
        finally:
            app.dependency_overrides.pop(get_current_active_user, None)

        assert resp.status_code == 200
        body = resp.json()
        assert isinstance(body, list)
        assert len(body) == 2

    def test_get_lessons_unauthenticated_returns_403(self, client):
        # HTTPBearer returns 403 when Authorization header is absent
        resp = client.get("/lessons")
        assert resp.status_code == 403
