# Contributing to AgentAnycast MCP Server

Thank you for your interest in contributing! Please see the
[main contributing guide](https://github.com/AgentAnycast/agentanycast/blob/main/CONTRIBUTING.md)
for the general workflow (issues, PRs, code of conduct).

## MCP Server–specific guidelines

- **Lint** — `ruff check . && ruff format --check .`
- **Test** — `pytest tests/ -v`
- **Type hints** — all public functions must have type annotations
- **Docstrings** — use Google-style docstrings for public APIs
- **Dependencies** — keep runtime dependencies minimal (`agentanycast` + `mcp`)
- **Generated code** — do not modify files under `_generated/`

## CI checks

Every PR must pass the following checks before merge:

| Check  | Command                        |
| ------ | ------------------------------ |
| Lint   | `ruff check . && ruff format --check .` |
| Test   | `pytest tests/ -v`             |
| Build  | `python -m build`              |
