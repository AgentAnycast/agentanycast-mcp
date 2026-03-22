"""AgentAnycast MCP Server — P2P agent networking for AI tools.

Exposes the AgentAnycast peer-to-peer network as MCP tools so that any
MCP-compatible AI assistant (Claude Desktop, Cursor, VS Code, Gemini CLI,
ChatGPT, etc.) can discover agents, send encrypted tasks, and query the
network — zero config, zero API keys.

Quick start::

    uvx agentanycast-mcp          # stdio (Claude Desktop, Cursor, VS Code)
    agentanycast-mcp              # same, if installed via pip

Configuration via environment variables::

    AGENTANYCAST_RELAY   — Relay server multiaddr for cross-network P2P
    AGENTANYCAST_HOME    — Data directory for daemon state
"""

from __future__ import annotations

import argparse


def main(argv: list[str] | None = None) -> None:
    """Entry point for ``agentanycast-mcp`` / ``uvx agentanycast-mcp``.

    Reads configuration from CLI arguments and environment variables,
    then starts the MCP server.
    """
    parser = argparse.ArgumentParser(
        prog="agentanycast-mcp",
        description="MCP server for P2P agent networking",
    )
    parser.add_argument(
        "--transport",
        choices=["stdio", "http"],
        default="stdio",
        help=(
            "Transport mode: stdio (default, for Claude Desktop/Cursor)"
            " or http (for ChatGPT/remote)"
        ),
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8080,
        help="HTTP port (only with --transport http, default: 8080)",
    )
    parser.add_argument(
        "--relay",
        default=None,
        help="Relay server multiaddr (overrides AGENTANYCAST_RELAY env var)",
    )
    parser.add_argument(
        "--home",
        default=None,
        help="Data directory for daemon state (overrides AGENTANYCAST_HOME env var)",
    )
    args = parser.parse_args(argv)

    # Import here so startup errors are caught after arg parsing
    from agentanycast.mcp_server import configure, run_server

    # CLI args take priority over env vars (env vars are read inside
    # mcp_server._get_node via _resolve_config)
    if args.relay:
        configure(relay=args.relay, home=args.home)
    elif args.home:
        configure(home=args.home)

    run_server(transport=args.transport, port=args.port)
