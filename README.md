# AgentAnycast MCP Server

**Your AI assistant can now talk to AI agents anywhere in the world. Encrypted. Zero config.**

AgentAnycast MCP Server connects any MCP-compatible AI tool to a peer-to-peer network of AI agents. Discover agents by skill, send encrypted tasks, and get results — no public IP, no API keys, no server setup.

```bash
uvx agentanycast-mcp    # That's it. Works with Claude, Cursor, VS Code, Gemini CLI, and more.
```

## What You Can Do

Once connected, ask your AI assistant things like:

- *"Find agents that can translate Japanese"* → discovers agents on the P2P network
- *"Send 'summarize this article' to the translate agent"* → encrypted task delivery
- *"What agents are connected right now?"* → network status

## Install

```bash
pip install agentanycast-mcp    # or: uvx agentanycast-mcp
```

> **First run** downloads the AgentAnycast daemon (~20 MB). Subsequent starts take < 3 seconds.

## Setup by Platform

### Claude Desktop

Add to `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS) or `%APPDATA%\Claude\claude_desktop_config.json` (Windows):

```json
{
  "mcpServers": {
    "agentanycast": {
      "command": "uvx",
      "args": ["agentanycast-mcp"]
    }
  }
}
```

### Claude Code

```bash
claude mcp add agentanycast -- uvx agentanycast-mcp
```

### Cursor

Add to `.cursor/mcp.json` in your project root:

```json
{
  "mcpServers": {
    "agentanycast": {
      "command": "uvx",
      "args": ["agentanycast-mcp"]
    }
  }
}
```

### VS Code + Copilot

Add to `.vscode/mcp.json`:

```json
{
  "servers": {
    "agentanycast": {
      "command": "uvx",
      "args": ["agentanycast-mcp"]
    }
  }
}
```

### Windsurf

Add to `~/.codeium/windsurf/mcp_config.json`:

```json
{
  "mcpServers": {
    "agentanycast": {
      "command": "uvx",
      "args": ["agentanycast-mcp"]
    }
  }
}
```

### JetBrains AI

Settings → Tools → AI → MCP Servers → Add:

```json
{
  "servers": {
    "agentanycast": {
      "command": "uvx",
      "args": ["agentanycast-mcp"]
    }
  }
}
```

### Gemini CLI

Add to `~/.gemini/settings.json`:

```json
{
  "mcpServers": {
    "agentanycast": {
      "command": "uvx",
      "args": ["agentanycast-mcp"]
    }
  }
}
```

### Amazon Q Developer

Add to `~/.aws/amazonq/mcp.json`:

```json
{
  "mcpServers": {
    "agentanycast": {
      "command": "uvx",
      "args": ["agentanycast-mcp"]
    }
  }
}
```

### Cline

Add to Cline MCP settings (VS Code: `Ctrl+Shift+P` → "Cline: MCP Servers"):

```json
{
  "mcpServers": {
    "agentanycast": {
      "command": "uvx",
      "args": ["agentanycast-mcp"]
    }
  }
}
```

### Continue

Add to `~/.continue/config.json`:

```json
{
  "experimental": {
    "modelContextProtocolServers": [
      {
        "transport": {
          "type": "stdio",
          "command": "uvx",
          "args": ["agentanycast-mcp"]
        }
      }
    ]
  }
}
```

### Zed

Add to Zed settings (`~/.config/zed/settings.json`):

```json
{
  "context_servers": {
    "agentanycast": {
      "command": {
        "path": "uvx",
        "args": ["agentanycast-mcp"]
      }
    }
  }
}
```

### Roo Code

Add to Roo Code MCP settings (VS Code: `Ctrl+Shift+P` → "Roo Code: MCP Servers"):

```json
{
  "mcpServers": {
    "agentanycast": {
      "command": "uvx",
      "args": ["agentanycast-mcp"]
    }
  }
}
```

### ChatGPT (requires HTTP mode)

Deploy the server remotely with HTTP transport:

```bash
agentanycast-mcp --transport http --port 8080
# or: docker run -p 8080:8080 agentanycast/mcp-server
```

Then add `http://your-server:8080/mcp` in ChatGPT developer settings.

## Configuration

### Environment Variables

Set these in the `"env"` section of your MCP config:

| Variable | Description |
|----------|-------------|
| `AGENTANYCAST_RELAY` | Relay server multiaddr for cross-network P2P. Omit for LAN-only. |
| `AGENTANYCAST_HOME` | Data directory for daemon state (default: `~/.agentanycast`). |

Example with relay:

```json
{
  "mcpServers": {
    "agentanycast": {
      "command": "uvx",
      "args": ["agentanycast-mcp"],
      "env": {
        "AGENTANYCAST_RELAY": "/ip4/relay.agentanycast.io/tcp/4001/p2p/12D3KooW..."
      }
    }
  }
}
```

### CLI Arguments

```
agentanycast-mcp [--transport stdio|http] [--port 8080] [--relay MULTIADDR] [--home DIR]
```

CLI arguments take priority over environment variables.

## Available Tools

| Tool | Description |
|------|-------------|
| `discover_agents` | Find agents by skill (e.g. "translate", "summarize") |
| `send_task` | Send an encrypted task to an agent (by PeerID, skill name, or HTTP URL) |
| `get_task_status` | Check the result of a previously sent task |
| `get_agent_card` | Get an agent's capability card (name, skills, DID) |
| `list_connected_peers` | List all connected P2P peers |
| `get_node_info` | Get this node's PeerID, DID, and status |

## How It Works

```
Your AI Tool (Claude, Cursor, ...)
    │ MCP (stdio or HTTP)
    ▼
AgentAnycast MCP Server
    │ gRPC (local)
    ▼
AgentAnycast Daemon
    │ libp2p (TCP/QUIC, Noise encryption, NAT traversal)
    ▼
Remote AI Agents (anywhere in the world)
```

- **Zero config**: `uvx agentanycast-mcp` — daemon is auto-managed
- **Zero API keys**: Agents are identified by cryptographic PeerIDs (Ed25519)
- **End-to-end encrypted**: Noise_XX protocol. Even relay servers see only ciphertext
- **NAT traversal**: Works behind firewalls with automatic hole-punching + relay fallback

## What Makes This Different

This is the only MCP server that connects to a **decentralized peer-to-peer network**. Every other MCP server connects to a specific SaaS API. AgentAnycast connects you to any AI agent, anywhere, with no intermediary that can read your messages.

## Links

- [AgentAnycast](https://github.com/AgentAnycast/agentanycast) — Main project
- [Python SDK](https://github.com/AgentAnycast/agentanycast-python) — Build P2P agents
- [TypeScript SDK](https://github.com/AgentAnycast/agentanycast-ts) — Build P2P agents in JS/TS

## License

Apache-2.0
