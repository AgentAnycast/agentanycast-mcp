"""AgentAnycast MCP Server — P2P agent networking for AI tools.

Two modes of operation:

**Server mode** (default) — exposes the P2P network as MCP tools::

    uvx agentanycast-mcp          # stdio (Claude Desktop, Cursor, VS Code)
    agentanycast-mcp --transport http  # HTTP (ChatGPT, remote)

**Proxy mode** — wraps any MCP server and makes it P2P-reachable::

    agentanycast-mcp --wrap "uvx mcp-server-filesystem"
    agentanycast-mcp --wrap "python -m my_server" --relay "/ip4/.../p2p/..."

Configuration via environment variables::

    AGENTANYCAST_RELAY   — Relay server multiaddr for cross-network P2P
    AGENTANYCAST_HOME    — Data directory for daemon state
"""

from __future__ import annotations

import argparse
import asyncio


def main(argv: list[str] | None = None) -> None:
    """Entry point for ``agentanycast-mcp`` / ``uvx agentanycast-mcp``.

    Reads configuration from CLI arguments and environment variables,
    then starts the MCP server or proxy.
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
            " or http (for ChatGPT/remote). Ignored in --wrap mode."
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
    parser.add_argument(
        "--wrap",
        default=None,
        metavar="COMMAND",
        help=(
            "Proxy mode: wrap an existing MCP server and expose it on the P2P network. "
            'Example: --wrap "uvx mcp-server-filesystem"'
        ),
    )
    args = parser.parse_args(argv)

    if args.wrap:
        # Proxy mode — wrap an external MCP server.
        from agentanycast_mcp.proxy import run_proxy

        try:
            asyncio.run(run_proxy(args.wrap, relay=args.relay, home=args.home))
        except KeyboardInterrupt:
            print("\nProxy stopped.")
    else:
        # Server mode — expose P2P network as MCP tools.
        from agentanycast.mcp_server import configure, run_server

        if args.relay:
            configure(relay=args.relay, home=args.home)
        elif args.home:
            configure(home=args.home)

        run_server(transport=args.transport, port=args.port)
