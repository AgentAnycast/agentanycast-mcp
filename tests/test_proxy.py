"""Tests for the MCP Remote Proxy module."""

from __future__ import annotations

from agentanycast_mcp.proxy import _extract_server_name, _parse_arguments


def test_extract_server_name_uvx():
    assert _extract_server_name("uvx mcp-server-filesystem") == "Filesystem"


def test_extract_server_name_npx():
    assert _extract_server_name("npx mcp-server-github") == "Github"


def test_extract_server_name_python_module():
    assert _extract_server_name("python -m my_mcp_server") == "My Mcp Server"


def test_extract_server_name_plain():
    assert _extract_server_name("my-custom-server") == "My Custom Server"


def test_extract_server_name_mcp_prefix():
    assert _extract_server_name("mcp-weather") == "Weather"


def test_parse_arguments_json_dict():
    result = _parse_arguments('{"city": "Tokyo", "units": "metric"}')
    assert result == {"city": "Tokyo", "units": "metric"}


def test_parse_arguments_json_with_tool():
    result = _parse_arguments('{"tool": "get_weather", "arguments": {"city": "NYC"}}')
    assert result == {"city": "NYC"}


def test_parse_arguments_plain_text():
    result = _parse_arguments("Hello, world!")
    assert result == {"input": "Hello, world!"}


def test_parse_arguments_empty():
    result = _parse_arguments("")
    assert result == {}


def test_parse_arguments_whitespace():
    result = _parse_arguments("   ")
    assert result == {}
