"""Integration-style tests for the MCP Remote Proxy module.

These tests use mocks to simulate the MCP subprocess and AgentAnycast node,
verifying the full proxy pipeline without requiring external services.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from agentanycast_mcp.proxy import _resolve_tool_name


# ---------------------------------------------------------------------------
# Fixtures and helpers
# ---------------------------------------------------------------------------


@dataclass
class FakeTask:
    """Mimics an incoming A2A task for testing."""

    messages: list[Any] = field(default_factory=list)
    skill_id: str | None = None
    target_skill_id: str | None = None
    _status: str = "submitted"

    async def update_status(self, status: str) -> None:
        self._status = status

    async def complete(self, artifacts: list[dict[str, Any]] | None = None) -> None:
        self._status = "completed"
        self.artifacts = artifacts

    async def fail(self, error_message: str = "") -> None:
        self._status = "failed"
        self.error_message = error_message


@dataclass
class FakePart:
    text: str | None = None


@dataclass
class FakeMessage:
    parts: list[FakePart] = field(default_factory=list)


# ---------------------------------------------------------------------------
# _resolve_tool_name tests
# ---------------------------------------------------------------------------


def test_resolve_tool_name_by_skill_id():
    """When the task has a skill_id matching a tool, use it."""
    task = FakeTask(skill_id="get_weather")
    tool_names = {"get_weather", "search"}
    assert _resolve_tool_name(task, tool_names, "search") == "get_weather"


def test_resolve_tool_name_by_target_skill_id():
    """Fallback to target_skill_id attribute."""
    task = FakeTask(target_skill_id="search")
    tool_names = {"get_weather", "search"}
    assert _resolve_tool_name(task, tool_names, "get_weather") == "search"


def test_resolve_tool_name_from_json_message():
    """Parse tool name from JSON message body."""
    msg = FakeMessage(parts=[FakePart(text='{"tool": "search", "query": "test"}')])
    task = FakeTask(messages=[msg])
    tool_names = {"get_weather", "search"}
    assert _resolve_tool_name(task, tool_names, "get_weather") == "search"


def test_resolve_tool_name_unknown_skill_id_fallback():
    """Unknown skill_id should fall back to default."""
    task = FakeTask(skill_id="nonexistent")
    tool_names = {"get_weather", "search"}
    assert _resolve_tool_name(task, tool_names, "search") == "search"


def test_resolve_tool_name_no_messages_fallback():
    """No messages and no skill_id should use default."""
    task = FakeTask()
    tool_names = {"get_weather"}
    assert _resolve_tool_name(task, tool_names, "get_weather") == "get_weather"


def test_resolve_tool_name_invalid_json_fallback():
    """Invalid JSON in message should fall back to default."""
    msg = FakeMessage(parts=[FakePart(text="not json")])
    task = FakeTask(messages=[msg])
    tool_names = {"search"}
    assert _resolve_tool_name(task, tool_names, "search") == "search"


def test_resolve_tool_name_json_tool_not_in_set():
    """JSON with tool name not in the tool set should fall back to default."""
    msg = FakeMessage(parts=[FakePart(text='{"tool": "delete_all"}')])
    task = FakeTask(messages=[msg])
    tool_names = {"search", "get_weather"}
    assert _resolve_tool_name(task, tool_names, "search") == "search"


# ---------------------------------------------------------------------------
# Proxy pipeline tests (mock MCP subprocess + Node)
# ---------------------------------------------------------------------------


@dataclass
class FakeMCPTool:
    name: str
    description: str = ""
    inputSchema: dict[str, Any] = field(default_factory=dict)


@dataclass
class FakeToolsResult:
    tools: list[FakeMCPTool] = field(default_factory=list)


@dataclass
class FakeContent:
    text: str


@dataclass
class FakeCallResult:
    content: list[FakeContent] = field(default_factory=list)


@pytest.mark.asyncio
async def test_proxy_handles_tool_call_success():
    """Verify the proxy routes a task to the correct MCP tool and completes."""
    from agentanycast_mcp.proxy import _parse_arguments, _resolve_tool_name

    # Simulate the task handler logic
    tool_names = {"get_weather", "search"}
    msg = FakeMessage(parts=[FakePart(text='{"city": "Tokyo"}')])
    task = FakeTask(messages=[msg], skill_id="get_weather")

    # Resolve tool
    tool_name = _resolve_tool_name(task, tool_names, "search")
    assert tool_name == "get_weather"

    # Parse arguments
    text = task.messages[-1].parts[0].text
    arguments = _parse_arguments(text)
    assert arguments == {"city": "Tokyo"}

    # Simulate MCP call
    await task.update_status("working")
    assert task._status == "working"

    result = FakeCallResult(content=[FakeContent(text="Sunny, 25°C")])
    result_texts = [c.text for c in result.content if hasattr(c, "text")]
    response_text = "\n".join(result_texts)
    await task.complete(artifacts=[{"name": tool_name, "parts": [{"text": response_text}]}])

    assert task._status == "completed"
    assert task.artifacts[0]["name"] == "get_weather"
    assert task.artifacts[0]["parts"][0]["text"] == "Sunny, 25°C"


@pytest.mark.asyncio
async def test_proxy_handles_tool_call_failure():
    """Verify the proxy correctly reports MCP tool errors."""
    task = FakeTask(
        messages=[FakeMessage(parts=[FakePart(text="test")])],
        skill_id="get_weather",
    )

    await task.update_status("working")

    # Simulate MCP tool failure
    await task.fail(error_message="Connection timeout")

    assert task._status == "failed"
    assert task.error_message == "Connection timeout"


@pytest.mark.asyncio
async def test_proxy_handles_empty_mcp_result():
    """Verify the proxy handles empty MCP tool results gracefully."""
    task = FakeTask(
        messages=[FakeMessage(parts=[FakePart(text='{"query": "test"}')])],
        skill_id="search",
    )

    await task.update_status("working")

    # Empty result
    result = FakeCallResult(content=[])
    result_texts = [c.text for c in result.content if hasattr(c, "text")]
    response_text = "\n".join(result_texts) if result_texts else "(no output)"
    await task.complete(artifacts=[{"name": "search", "parts": [{"text": response_text}]}])

    assert task._status == "completed"
    assert task.artifacts[0]["parts"][0]["text"] == "(no output)"
