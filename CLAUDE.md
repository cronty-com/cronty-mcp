# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Cronty MCP is a FastMCP server that enables AI agents to schedule notifications via Upstash QStash and NTFY.

**Stack:** Python 3.13+, FastMCP, Upstash QStash, NTFY, pytest

## Commands

### Setup

```bash
uv sync                    # Install dependencies
cp .env.example .env       # Create local env file
```

### Dependencies

```bash
uv add <package>           # Add dependency (never edit pyproject.toml directly)
uv add --dev <package>     # Add dev dependency
```

### Development

```bash
uv run fastmcp dev server.py       # Run server in dev mode with MCP Inspector
uv run python server.py            # Run server directly
```

### Testing

```bash
uv run pytest                      # Run all tests
uv run pytest tests/test_health.py # Run single test file
uv run pytest -k "health"          # Run tests matching pattern
uv run pytest -x                   # Stop on first failure
```

### Linting

```bash
uv run ruff check .                # Check for issues
uv run ruff check . --fix          # Auto-fix issues
uv run ruff format .               # Format code
```

## Architecture

### Project Structure (Flat - required for FastMCP Cloud)

```
cronty-mcp/
├── server.py          # FastMCP server entry point
├── config.py          # Environment variable loading and validation
├── tools/             # MCP tool implementations
│   ├── __init__.py
│   └── health.py
├── services/          # Business logic (QStash, NTFY integrations)
│   ├── __init__.py
│   ├── qstash.py
│   └── ntfy.py
├── tests/             # pytest tests
├── pyproject.toml     # Dependencies and project config
└── .env.example       # Environment variable template
```

### Layer Pattern

```
MCP Tool → Service → External API (QStash/NTFY)
```

- **Tools**: Thin handlers that validate input and delegate to services
- **Services**: Business logic and external API interactions
- **Config**: Environment validation, loaded at startup

## Code Conventions

- No comments unless explicitly requested
- No emojis in code
- Use type hints for function signatures
- Prefer explicit over implicit
- Environment variables validated at startup, accessed via config module

## Git Conventions

Use conventional commits: `feat:`, `fix:`, `test:`, `refactor:`, `docs:`, `chore:`

Use `/commit` command for AI-attributed commits.

## Environment Variables

Required variables (validated at startup):
- `QSTASH_TOKEN` - QStash API token
- `NTFY_TOPIC` - Notification delivery topic
