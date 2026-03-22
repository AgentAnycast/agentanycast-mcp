"""MCP Remote Proxy — expose any MCP server on the P2P agent network.

This module wraps a local MCP server (running as a subprocess via stdio)
and makes it reachable on the AgentAnycast P2P network. Remote agents
can discover and invoke the MCP server's tools via encrypted P2P tasks.

Usage::

    agentanycast-mcp --wrap "uvx mcp-server-filesystem"
    agentanycast-mcp --wrap "python -m my_mcp_server" --relay "/ip4/.../p2p/..."

How it works:

1. Spawns the target MCP server as a subprocess (stdio transport)
2. Lists the server's tools via ``tools/list``
3. Creates an AgentCard with skills derived from those tools
4. Starts an AgentAnycast P2P node and registers the skills
5. Incoming A2A tasks are mapped to MCP ``tools/call`` on the subprocess
6. Results are returned as A2A task artifacts
"""

from __future__ import annotations

import json
import logging
import shlex
from typing import Any

logger = logging.getLogger(__name__)


async def run_proxy(
    wrap_command: str,
    *,
    relay: str | None = None,
    home: str | None = None,
) -> None:
    """Run the MCP Remote Proxy.

    Spawns *wrap_command* as a subprocess MCP server, discovers its tools,
    and bridges them onto the P2P network as A2A skills.

    Args:
        wrap_command: Shell command to start the MCP server (e.g.
            ``"uvx mcp-server-filesystem"``).
        relay: Optional relay multiaddr for cross-network connectivity.
        home: Optional data directory for daemon state.
    """
    # Lazy imports so the main CLI stays fast when --wrap is not used.
    from contextlib import AsyncExitStack

    from agentanycast import Node
    from agentanycast.mcp import MCPTool, mcp_tools_to_agent_card
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client

    args = shlex.split(wrap_command)
    if not args:
        raise ValueError("--wrap command must not be empty")

    server_params = StdioServerParameters(command=args[0], args=args[1:])

    async with AsyncExitStack() as stack:
        # 1. Start MCP server subprocess.
        logger.info("starting MCP server: %s", wrap_command)
        read_stream, write_stream = await stack.enter_async_context(stdio_client(server_params))
        session: ClientSession = await stack.enter_async_context(
            ClientSession(read_stream, write_stream)
        )
        await session.initialize()

        # 2. List tools from the MCP server.
        tools_result = await session.list_tools()
        mcp_tools = [
            MCPTool(
                name=t.name,
                description=t.description or "",
                input_schema=t.inputSchema if hasattr(t, "inputSchema") else {},
            )
            for t in tools_result.tools
        ]
        logger.info("discovered %d MCP tools: %s", len(mcp_tools), [t.name for t in mcp_tools])

        if not mcp_tools:
            logger.warning("MCP server has no tools — nothing to proxy")
            return

        # 3. Build AgentCard from tools.
        server_name = _extract_server_name(wrap_command)
        card = mcp_tools_to_agent_card(
            server_name=server_name,
            tools=mcp_tools,
            description=f"MCP proxy for {server_name} — {len(mcp_tools)} tools available",
        )

        # 4. Start P2P node.
        node_kwargs: dict[str, Any] = {}
        if relay:
            node_kwargs["relay"] = relay
        if home:
            node_kwargs["home"] = home

        node = Node(card=card, **node_kwargs)
        await node.start()

        logger.info("P2P node started — PeerID: %s", node.peer_id)
        logger.info("proxying %d tools as A2A skills", len(mcp_tools))
        for tool in mcp_tools:
            logger.info("  skill: %s — %s", tool.name, tool.description)

        # Build tool name lookup.
        tool_names = {t.name for t in mcp_tools}

        # 5. Handle incoming A2A tasks → MCP tool calls.
        @node.on_task
        async def handle_task(task: Any) -> None:
            """Route an incoming A2A task to the appropriate MCP tool."""
            # Extract the text message from the task.
            text = ""
            if task.messages:
                for part in task.messages[-1].parts:
                    if part.text:
                        text = part.text
                        break

            # Determine which tool to call.
            # Strategy: if the task arrived via anycast, the skill_id maps
            # directly to a tool name. Otherwise try to parse the text as
            # JSON with a "tool" field, or fall back to the first tool.
            tool_name = _resolve_tool_name(task, tool_names, mcp_tools[0].name)

            # Parse arguments from the text (try JSON first, then plain text).
            arguments = _parse_arguments(text)

            logger.info("calling MCP tool %s with %d args", tool_name, len(arguments))
            await task.update_status("working")

            try:
                result = await session.call_tool(tool_name, arguments=arguments)

                # Convert MCP result to A2A artifact.
                result_texts = []
                for content in result.content:
                    if hasattr(content, "text"):
                        result_texts.append(content.text)

                response_text = "\n".join(result_texts) if result_texts else "(no output)"
                await task.complete(
                    artifacts=[{"name": tool_name, "parts": [{"text": response_text}]}]
                )
            except Exception as exc:
                logger.error("MCP tool call failed: %s", exc)
                await task.fail(error_message=str(exc))

        # 6. Serve forever.
        print(f"\nMCP Remote Proxy active — PeerID: {node.peer_id}")
        print(f"Proxying {len(mcp_tools)} tools from: {wrap_command}")
        print("Press Ctrl+C to stop.\n")

        await node.serve_forever()


def _extract_server_name(command: str) -> str:
    """Extract a human-readable name from the wrap command."""
    parts = shlex.split(command)
    # Skip runtime prefixes like uvx, npx, python -m
    for skip in ("uvx", "npx", "pipx", "python", "node"):
        if parts and parts[0] == skip:
            parts = parts[1:]
    if parts and parts[0] == "-m":
        parts = parts[1:]
    name = parts[0] if parts else command
    # Clean up common prefixes
    for prefix in ("mcp-server-", "mcp-"):
        if name.startswith(prefix):
            name = name[len(prefix) :]
    return name.replace("-", " ").replace("_", " ").title()


def _resolve_tool_name(task: Any, tool_names: set[str], default: str) -> str:
    """Determine which MCP tool to call from the task context."""
    # If the task has a target_skill_id that matches a tool, use it.
    skill_id = getattr(task, "skill_id", None) or getattr(task, "target_skill_id", None)
    if skill_id and skill_id in tool_names:
        return skill_id

    # Try to parse the first message as JSON with a "tool" field.
    if task.messages:
        for part in task.messages[-1].parts:
            if part.text:
                try:
                    parsed = json.loads(part.text)
                    if isinstance(parsed, dict) and "tool" in parsed:
                        name = parsed["tool"]
                        if name in tool_names:
                            return name
                except (json.JSONDecodeError, TypeError):
                    pass

    return default


def _parse_arguments(text: str) -> dict[str, Any]:
    """Parse tool arguments from message text."""
    # Try JSON first.
    try:
        parsed = json.loads(text)
        if isinstance(parsed, dict):
            # If it has "tool" + "arguments" structure, extract arguments.
            if "arguments" in parsed:
                return parsed["arguments"]
            # If it has "tool" key, remove it and use the rest.
            if "tool" in parsed:
                return {k: v for k, v in parsed.items() if k != "tool"}
            return parsed
    except (json.JSONDecodeError, TypeError):
        pass

    # Plain text — pass as single "input" argument.
    if text.strip():
        return {"input": text}
    return {}
