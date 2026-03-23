"""Tests for CLI argument parsing and entry point routing."""

from __future__ import annotations

import sys
from types import ModuleType
from unittest.mock import MagicMock

import pytest


def test_main_invalid_transport():
    """Invalid transport should cause argparse to exit with error."""
    from agentanycast_mcp import main

    with pytest.raises(SystemExit) as exc_info:
        main(["--transport", "websocket"])
    assert exc_info.value.code == 2


def test_main_server_mode_calls_run_server(monkeypatch):
    """Default (no --wrap) should call run_server via agentanycast.mcp_server."""
    called = {}

    fake_mod = ModuleType("agentanycast.mcp_server")
    fake_mod.configure = lambda **kwargs: called.update({"configure": kwargs})  # type: ignore[attr-defined]
    fake_mod.run_server = lambda transport="stdio", port=8080: called.update(  # type: ignore[attr-defined]
        {"transport": transport, "port": port}
    )

    monkeypatch.setitem(sys.modules, "agentanycast.mcp_server", fake_mod)

    from agentanycast_mcp import main

    main(["--transport", "stdio"])
    assert called["transport"] == "stdio"
    assert called["port"] == 8080


def test_main_http_transport(monkeypatch):
    """--transport http should pass transport='http' and custom port."""
    called = {}

    fake_mod = ModuleType("agentanycast.mcp_server")
    fake_mod.configure = lambda **kwargs: None  # type: ignore[attr-defined]
    fake_mod.run_server = lambda transport="stdio", port=8080: called.update(  # type: ignore[attr-defined]
        {"transport": transport, "port": port}
    )

    monkeypatch.setitem(sys.modules, "agentanycast.mcp_server", fake_mod)

    from agentanycast_mcp import main

    main(["--transport", "http", "--port", "9090"])
    assert called["transport"] == "http"
    assert called["port"] == 9090


def test_main_with_relay(monkeypatch):
    """--relay should call configure() with relay address."""
    called = {}

    fake_mod = ModuleType("agentanycast.mcp_server")
    fake_mod.configure = lambda **kwargs: called.update({"configure": kwargs})  # type: ignore[attr-defined]
    fake_mod.run_server = lambda transport="stdio", port=8080: None  # type: ignore[attr-defined]

    monkeypatch.setitem(sys.modules, "agentanycast.mcp_server", fake_mod)

    from agentanycast_mcp import main

    main(["--relay", "/ip4/1.2.3.4/tcp/4001/p2p/12D3KooW"])
    assert called["configure"]["relay"] == "/ip4/1.2.3.4/tcp/4001/p2p/12D3KooW"


def test_main_wrap_mode_routes_to_proxy(monkeypatch):
    """--wrap should route to proxy mode instead of server mode."""
    called = {}

    async def fake_run_proxy(wrap_command, *, relay=None, home=None):
        called["command"] = wrap_command
        called["relay"] = relay

    monkeypatch.setattr("agentanycast_mcp.proxy.run_proxy", fake_run_proxy)

    from agentanycast_mcp import main

    main(["--wrap", "uvx mcp-server-test"])
    assert called["command"] == "uvx mcp-server-test"
    assert called["relay"] is None
