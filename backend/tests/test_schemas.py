"""
Tests for app/entities/schemas.py and app/mcp/schemas.py

Covers:
- Field validation (min/max length, patterns, ranges)
- Required vs optional fields
- MCP request/response validation
"""

import uuid
import pytest
from pydantic import ValidationError

from app.entities.schemas import (
    UserCreate,
    UserUpdate,
    LessonCreate,
    LessonUpdate,
    ProgressCreate,
)
from app.mcp.schemas import MCPRequest, MCPResponse, ToolType


# ─── UserCreate ───────────────────────────────────────────────────────────────

class TestUserCreateSchema:

    def test_valid_user(self):
        user = UserCreate(name="Alice", email="alice@test.com", password="secret99", skill_level="beginner")
        assert user.name == "Alice"
        assert user.email == "alice@test.com"

    def test_invalid_email_raises(self):
        with pytest.raises(ValidationError):
            UserCreate(name="Bob", email="not-an-email", password="secret99")

    def test_password_too_short_raises(self):
        with pytest.raises(ValidationError):
            UserCreate(name="Bob", email="bob@test.com", password="short")

    def test_empty_name_raises(self):
        with pytest.raises(ValidationError):
            UserCreate(name="", email="bob@test.com", password="longpassword")

    def test_invalid_skill_level_raises(self):
        with pytest.raises(ValidationError):
            UserCreate(name="Bob", email="bob@test.com", password="longpassword", skill_level="expert")

    def test_all_valid_skill_levels(self):
        for level in ("beginner", "intermediate", "advanced"):
            user = UserCreate(name="Bob", email="bob@test.com", password="longpassword", skill_level=level)
            assert user.skill_level == level

    def test_default_skill_level_is_beginner(self):
        user = UserCreate(name="Alice", email="alice@test.com", password="secret99")
        assert user.skill_level == "beginner"


# ─── UserUpdate ───────────────────────────────────────────────────────────────

class TestUserUpdateSchema:

    def test_all_fields_optional(self):
        update = UserUpdate()
        assert update.name is None
        assert update.skill_level is None

    def test_partial_update_valid(self):
        update = UserUpdate(name="Updated Name")
        assert update.name == "Updated Name"

    def test_invalid_skill_level_in_update(self):
        with pytest.raises(ValidationError):
            UserUpdate(skill_level="guru")


# ─── LessonCreate ─────────────────────────────────────────────────────────────

class TestLessonCreateSchema:

    def test_valid_lesson(self):
        lesson = LessonCreate(
            title="Introduction to Drawing",
            content="In this lesson...",
            difficulty="beginner",
            lesson_type="tutorial",
            duration_minutes=45,
        )
        assert lesson.title == "Introduction to Drawing"
        assert lesson.duration_minutes == 45

    def test_empty_title_raises(self):
        with pytest.raises(ValidationError):
            LessonCreate(title="", content="...", difficulty="beginner")

    def test_invalid_difficulty_raises(self):
        with pytest.raises(ValidationError):
            LessonCreate(title="Lesson", content="...", difficulty="master")

    def test_invalid_lesson_type_raises(self):
        with pytest.raises(ValidationError):
            LessonCreate(title="Lesson", content="...", difficulty="beginner", lesson_type="video")

    def test_zero_duration_raises(self):
        with pytest.raises(ValidationError):
            LessonCreate(title="Lesson", content="...", difficulty="beginner", duration_minutes=0)

    def test_prerequisites_defaults_to_empty_list(self):
        lesson = LessonCreate(title="Lesson", content="...", difficulty="beginner")
        assert lesson.prerequisites == []

    def test_prerequisites_accepts_uuid_list(self):
        ids = [uuid.uuid4(), uuid.uuid4()]
        lesson = LessonCreate(title="L", content="c", difficulty="advanced", prerequisites=ids)
        assert len(lesson.prerequisites) == 2


# ─── ProgressCreate ───────────────────────────────────────────────────────────

class TestProgressCreateSchema:

    def test_valid_progress(self):
        uid = uuid.uuid4()
        lid = uuid.uuid4()
        from app.entities.schemas import ProgressCreate
        progress = ProgressCreate(user_id=uid, lesson_id=lid, completion_status="in_progress")
        assert progress.user_id == uid


# ─── MCP Schemas ──────────────────────────────────────────────────────────────

class TestMCPSchemas:

    def test_valid_mcp_request(self):
        req = MCPRequest(
            tool_name=ToolType.GET_USER_PROGRESS,
            parameters={"user_id": str(uuid.uuid4())},
        )
        assert req.tool_name == ToolType.GET_USER_PROGRESS.value

    def test_mcp_request_unknown_tool_raises(self):
        with pytest.raises(ValidationError):
            MCPRequest(tool_name="nonexistent_tool", parameters={})

    def test_mcp_response_success(self):
        resp = MCPResponse(
            success=True,
            result={"data": "ok"},
            tool_name="get_user_progress",
        )
        assert resp.success is True
        assert resp.error is None

    def test_mcp_response_error(self):
        resp = MCPResponse(
            success=False,
            error="Something went wrong",
            tool_name="get_user_progress",
        )
        assert resp.success is False
        assert resp.error == "Something went wrong"
        assert resp.result is None

    def test_all_tool_types_are_valid_enum_values(self):
        expected = {
            "get_user_progress", "update_progress", "generate_lesson",
            "evaluate_quiz", "schedule_reminder", "fetch_recommendations",
            "get_user_profile", "update_user_profile",
        }
        actual = {t.value for t in ToolType}
        assert actual == expected
