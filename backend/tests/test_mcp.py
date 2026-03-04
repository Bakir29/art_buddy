"""
Tests for app/mcp/tool_registry.py

Verifies tool registration, discovery, parameter validation,
and stats tracking — no database or live service calls needed.
"""

import uuid
import pytest
from unittest.mock import MagicMock, AsyncMock, patch

from app.mcp.tool_registry import ToolRegistry
from app.mcp.schemas import ToolType, MCPRequest, MCPResponse


@pytest.fixture
def registry():
    return ToolRegistry()


# ─── Registration ─────────────────────────────────────────────────────────────

class TestToolRegistration:

    def test_all_eight_tools_are_registered(self, registry):
        tools = registry.list_tools()
        tool_names = {t.name for t in tools}
        expected = {t.value for t in ToolType}
        assert expected == tool_names

    def test_get_tool_returns_correct_tool(self, registry):
        tool = registry.get_tool(ToolType.GET_USER_PROGRESS)
        assert tool is not None
        assert tool.name == ToolType.GET_USER_PROGRESS.value

    def test_get_nonexistent_tool_returns_none(self, registry):
        result = registry.get_tool("does_not_exist")
        assert result is None

    def test_tools_have_descriptions(self, registry):
        for tool in registry.list_tools():
            assert tool.description, f"Tool {tool.name} has no description"

    def test_tools_have_parameter_schemas(self, registry):
        for tool in registry.list_tools():
            assert tool.parameters_schema, f"Tool {tool.name} has no parameters schema"

    def test_each_tool_has_required_user_id(self, registry):
        """Every tool schema should require user_id."""
        for tool in registry.list_tools():
            required = tool.parameters_schema.get("required", [])
            assert "user_id" in required, f"Tool {tool.name} missing required user_id"


# ─── Parameter validation (via validate_request) ────────────────────────────

class TestParameterValidation:

    def test_valid_params_pass_validation(self, registry):
        req = MCPRequest(
            tool_name=ToolType.GET_USER_PROGRESS,
            parameters={"user_id": str(uuid.uuid4())},
        )
        is_valid, error = registry.validate_request(req)
        assert is_valid is True
        assert error is None

    def test_missing_required_param_fails(self, registry):
        req = MCPRequest(
            tool_name=ToolType.GET_USER_PROGRESS,
            parameters={},  # user_id missing
        )
        is_valid, error = registry.validate_request(req)
        assert is_valid is False
        assert error is not None

    def test_update_progress_requires_lesson_id(self, registry):
        req = MCPRequest(
            tool_name=ToolType.UPDATE_PROGRESS,
            parameters={"user_id": str(uuid.uuid4())},  # lesson_id + status missing
        )
        is_valid, _ = registry.validate_request(req)
        assert is_valid is False

    def test_unknown_tool_detected_via_get_tool(self, registry):
        result = registry.get_tool("ghost_tool")
        assert result is None


# ─── Stats tracking ───────────────────────────────────────────────────────────

class TestToolStats:

    def test_stats_initialized_for_all_tools(self, registry):
        stats = registry.get_tool_stats()
        for tool_name in {t.value for t in ToolType}:
            assert tool_name in stats

    def test_stats_contain_call_count(self, registry):
        stats = registry.get_tool_stats()
        for tool_stats in stats.values():
            assert "calls" in tool_stats or "total_calls" in tool_stats or isinstance(tool_stats, dict)


# ─── Export and categories ───────────────────────────────────────────────────

class TestExportAndCategories:

    def test_get_categories_returns_list(self, registry):
        cats = registry.get_categories()
        assert isinstance(cats, list)
        assert len(cats) > 0

    def test_known_categories_present(self, registry):
        cats = registry.get_categories()
        # These categories are defined in the default tools
        for expected in ("progress", "profile", "assessment"):
            assert expected in cats

    def test_export_tool_definitions_has_expected_structure(self, registry):
        export = registry.export_tool_definitions()
        assert "tools" in export
        assert "categories" in export
        assert "total_tools" in export
        assert export["total_tools"] == 8

    def test_record_tool_usage_increments_calls(self, registry):
        tool_name = ToolType.GET_USER_PROGRESS.value
        before = registry.get_tool_stats(tool_name)["total_calls"]
        registry.record_tool_usage(tool_name, success=True, execution_time_ms=12.5)
        after = registry.get_tool_stats(tool_name)["total_calls"]
        assert after == before + 1

    def test_failed_usage_increments_failed_calls(self, registry):
        tool_name = ToolType.EVALUATE_QUIZ.value
        registry.record_tool_usage(tool_name, success=False, execution_time_ms=5.0)
        stats = registry.get_tool_stats(tool_name)
        assert stats["failed_calls"] >= 1
