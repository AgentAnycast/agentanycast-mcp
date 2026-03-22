# AgentAnycast MCP Server

**Turn any AI tool into a peer-to-peer agent hub.** Discover, communicate with, and orchestrate AI agents across any network -- encrypted, decentralized, zero config.

[![PyPI](https://img.shields.io/pypi/v/agentanycast-mcp?color=8B5CF6)](https://pypi.org/project/agentanycast-mcp/)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue)](LICENSE)

```bash
uvx agentanycast-mcp
```

Works with Claude Desktop, Claude Code, Cursor, VS Code, Windsurf, JetBrains, Gemini CLI, Amazon Q, Cline, Continue, Zed, Roo Code, and ChatGPT.

## Setup

Pick your platform and add the config below. That's the entire setup -- the daemon downloads and starts automatically on first run.

<details open>
<summary><strong>Claude Desktop</strong></summary>

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
</details>

<details>
<summary><strong>Claude Code</strong></summary>

```bash
claude mcp add agentanycast -- uvx agentanycast-mcp
```
</details>

<details>
<summary><strong>Cursor</strong></summary>

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
</details>

<details>
<summary><strong>VS Code + Copilot</strong></summary>

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
</details>

<details>
<summary><strong>Windsurf</strong></summary>

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
</details>

<details>
<summary><strong>JetBrains AI</strong></summary>

Settings -> Tools -> AI -> MCP Servers -> Add:

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
</details>

<details>
<summary><strong>Gemini CLI</strong></summary>

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
</details>

<details>
<summary><strong>Amazon Q Developer</strong></summary>

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
</details>

<details>
<summary><strong>Cline</strong></summary>

Add to Cline MCP settings (VS Code: `Ctrl+Shift+P` -> "Cline: MCP Servers"):

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
</details>

<details>
<summary><strong>Continue</strong></summary>

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
</details>

<details>
<summary><strong>Zed</strong></summary>

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
</details>

<details>
<summary><strong>Roo Code</strong></summary>

Add to Roo Code MCP settings (VS Code: `Ctrl+Shift+P` -> "Roo Code: MCP Servers"):

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
</details>

<details>
<summary><strong>ChatGPT (HTTP mode)</strong></summary>

Deploy the server with HTTP transport:

```bash
agentanycast-mcp --transport http --port 8080
# or: docker run -p 8080:8080 agentanycast/mcp-server
```

Then add `http://your-server:8080/mcp` in ChatGPT developer settings.
</details>

## What You Can Do

Once connected, ask your AI assistant:

- *"Find agents that can translate Japanese"* -- discovers agents on the P2P network
- *"Send 'summarize this article' to the translate agent"* -- encrypted task delivery
- *"What agents are connected right now?"* -- lists connected peers
- *"What's my Peer ID?"* -- shows your node's identity and DID

## Available Tools

| Tool | Description | Example prompt |
|------|-------------|----------------|
| `discover_agents` | Find agents by skill | *"Find agents that can translate"* |
| `send_task` | Send an encrypted task to an agent | *"Send 'hello' to peer 12D3KooW..."* |
| `get_task_status` | Check the result of a sent task | *"What was the result of that task?"* |
| `get_agent_card` | Get an agent's capabilities | *"What can that agent do?"* |
| `list_connected_peers` | List all connected P2P peers | *"Who's online?"* |
| `get_node_info` | Get this node's Peer ID, DID, status | *"What's my agent info?"* |

## Configuration

### Environment Variables

Set these in the `"env"` section of your MCP config:

| Variable | Description | Default |
|----------|-------------|---------|
| `AGENTANYCAST_RELAY` | Relay server multiaddr for cross-network P2P | None (LAN only) |
| `AGENTANYCAST_HOME` | Data directory for daemon state | `~/.agentanycast` |

Example with relay for cross-network communication:

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

## How It Works

```
Your AI Tool (Claude, Cursor, VS Code, ...)
    |
    | MCP protocol (stdio or HTTP)
    v
AgentAnycast MCP Server
    |
    | gRPC (Unix domain socket)
    v
AgentAnycast Daemon (Go)
    |
    | libp2p (TCP/QUIC + Noise_XX encryption + NAT traversal)
    v
Remote AI Agents (anywhere in the world)
```

- **Zero config** -- `uvx agentanycast-mcp` handles everything. The daemon is auto-downloaded and managed.
- **Zero API keys** -- agents are identified by cryptographic Peer IDs (Ed25519), not accounts or tokens.
- **End-to-end encrypted** -- Noise_XX protocol. Even relay servers see only ciphertext.
- **NAT traversal** -- works behind firewalls with automatic hole-punching and relay fallback.

## What Makes This Different

This is the only MCP server that connects to a **decentralized peer-to-peer network** of AI agents. Other MCP servers connect to specific SaaS APIs. AgentAnycast connects you to any AI agent, anywhere, with no intermediary that can read your messages.

## Troubleshooting

**Daemon fails to start**
- Check that port 4001 (TCP) is not in use: `lsof -i :4001`
- Try a clean state: `rm -rf ~/.agentanycast && uvx agentanycast-mcp`

**No agents found on discover**
- Agents must be on the same LAN (mDNS) or connected to the same relay
- Set `AGENTANYCAST_RELAY` to connect across networks

**Connection timeout**
- Behind a strict firewall? Set a relay address. The relay provides fallback connectivity.
- Check daemon logs: `cat ~/.agentanycast/daemon.log`

**"uvx" not found**
- Install uv: `curl -LsSf https://astral.sh/uv/install.sh | sh`
- Or install directly: `pip install agentanycast-mcp`

**Tool calls failing**
- Restart your AI tool after adding the MCP config
- Verify config JSON syntax (no trailing commas)

## Links

- [AgentAnycast](https://github.com/AgentAnycast/agentanycast) -- Main project, documentation, examples
- [Python SDK](https://github.com/AgentAnycast/agentanycast-python) -- Build P2P agents in Python
- [TypeScript SDK](https://github.com/AgentAnycast/agentanycast-ts) -- Build P2P agents in TypeScript

## License

[Apache License, Version 2.0](LICENSE)
