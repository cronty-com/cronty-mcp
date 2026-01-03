# Cronty MCP

A FastMCP server that enables AI agents to schedule notifications and reminders via [Upstash QStash](https://upstash.com/docs/qstash/overall/getstarted) and [NTFY](https://ntfy.sh/).

## Features

- **Instant Push Notifications** - Send immediate notifications with rich formatting, actions, and attachments
- **One-off Scheduled Notifications** - Schedule notifications for a specific future time using ISO 8601, date/time/timezone, or delay format
- **Recurring Cron Notifications** - Create persistent schedules using standard cron syntax

## Available Tools

| Tool | Description |
|------|-------------|
| `health` | Check server configuration and environment status |
| `send_push_notification` | Send an immediate push notification |
| `schedule_notification` | Schedule a one-off notification for a future time |
| `schedule_cron_notification` | Schedule recurring notifications using cron syntax |

## Prerequisites

- Python 3.13+
- [uv](https://docs.astral.sh/uv/) package manager
- [Upstash QStash](https://console.upstash.com/qstash) account and token
- [NTFY](https://ntfy.sh/) topic for receiving notifications

## Quickstart

### 1. Clone and Setup

```bash
git clone https://github.com/your-org/cronty-mcp.git
cd cronty-mcp
uv sync
```

### 2. Configure Environment

```bash
cp .env.example .env
```

Edit `.env` with your credentials:

```bash
QSTASH_TOKEN=your_qstash_token_here
NTFY_TOPIC=your_ntfy_topic_here
```

### 3. Run the Server

```bash
uv run fastmcp run server.py
```

For development with the MCP Inspector:

```bash
uv run fastmcp dev server.py
```

## Agent Configuration (Local Mode)

Configure your AI agent to connect to the local MCP server.

### Claude Code

Add to your project's `.mcp.json`:

```json
{
  "mcpServers": {
    "cronty-mcp": {
      "command": "uv",
      "args": ["run", "fastmcp", "run", "server.py"]
    }
  }
}
```

Or use the CLI:

```bash
claude mcp add cronty-mcp -- uv run fastmcp run server.py
```

### Claude Desktop

Add to your Claude Desktop configuration file:

- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "cronty-mcp": {
      "command": "uv",
      "args": ["run", "fastmcp", "run", "server.py"],
      "cwd": "/path/to/cronty-mcp"
    }
  }
}
```

### Cursor

Add to your Cursor MCP configuration (`.cursor/mcp.json` in your project or global settings):

```json
{
  "mcpServers": {
    "cronty-mcp": {
      "command": "uv",
      "args": ["run", "fastmcp", "run", "server.py"],
      "cwd": "/path/to/cronty-mcp"
    }
  }
}
```

### VS Code

Add to your VS Code settings (`.vscode/mcp.json` or user settings):

```json
{
  "mcpServers": {
    "cronty-mcp": {
      "command": "uv",
      "args": ["run", "fastmcp", "run", "server.py"],
      "cwd": "/path/to/cronty-mcp"
    }
  }
}
```

### Windsurf

Add to your Windsurf MCP configuration (`~/.windsurf/mcp.json` or project-level):

```json
{
  "mcpServers": {
    "cronty-mcp": {
      "command": "uv",
      "args": ["run", "fastmcp", "run", "server.py"],
      "cwd": "/path/to/cronty-mcp"
    }
  }
}
```

### Codex CLI

```bash
codex mcp add cronty-mcp -- uv run fastmcp run server.py
```

### Gemini CLI

```bash
gemini mcp add cronty-mcp -- uv run fastmcp run server.py
```

## FastMCP Cloud Deployment

When deployed to [FastMCP Cloud](https://fastmcp.cloud), you can connect to your server using these configurations.

Replace `your-hostname` with your actual FastMCP Cloud hostname (e.g., `your-app-name.fastmcp.app`).

### Claude Code

```bash
claude mcp add --scope local --transport http cronty-mcp https://your-hostname.fastmcp.app/mcp
```

### Claude Desktop

Use the DXT manifest URL:

```
https://your-hostname.fastmcp.app/manifest.dxt
```

### Codex CLI

```bash
codex mcp add --url https://your-hostname.fastmcp.app/mcp cronty-mcp
```

### Gemini CLI

```bash
gemini mcp add cronty-mcp https://your-hostname.fastmcp.app/mcp --transport http
```

### Cursor

Use this deeplink (replace the hostname in the base64-encoded config):

```
cursor://anysphere.cursor-deeplink/mcp/install?name=cronty-mcp&config=<base64-encoded-config>
```

Or add manually to `.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "cronty-mcp": {
      "url": "https://your-hostname.fastmcp.app/mcp"
    }
  }
}
```

### VS Code

```bash
code --add-mcp '{"name":"cronty-mcp","type":"http","url":"https://your-hostname.fastmcp.app/mcp"}'
```

### FastMCP Python Client

```python
import asyncio
from fastmcp import Client

client = Client("https://your-hostname.fastmcp.app/mcp")

async def main():
    async with client:
        await client.ping()

        tools = await client.list_tools()

        result = await client.call_tool(
            "send_push_notification",
            {"message": "Hello from Cronty!"}
        )
        print(result)

asyncio.run(main())
```

### OpenAI SDK

```python
from openai import OpenAI

client = OpenAI()

resp = client.responses.create(
    model="gpt-4.1",
    tools=[
        {
            "type": "mcp",
            "server_label": "cronty-mcp",
            "server_url": "https://your-hostname.fastmcp.app/mcp",
            "require_approval": "never",
        },
    ],
    input="Send me a test notification",
)
```

## Development

### Install Dependencies

```bash
uv sync
```

### Run Tests

```bash
uv run pytest
```

### Linting

```bash
uv run ruff check .
uv run ruff check . --fix
uv run ruff format .
```

## License

MIT
