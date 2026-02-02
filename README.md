# Cronty MCP

A FastMCP server that enables AI agents to schedule notifications and reminders via [Upstash QStash](https://upstash.com/docs/qstash/overall/getstarted) and [NTFY](https://ntfy.sh/).

## Features

- **Instant Push Notifications** - Send immediate notifications with rich formatting, actions, and attachments
- **One-off Scheduled Notifications** - Schedule notifications for a specific future time using ISO 8601, date/time/timezone, or delay format
- **Recurring Cron Notifications** - Create persistent schedules using standard cron syntax

## Available Tools

| Tool | Description |
|------|-------------|
| `send_push_notification` | Send an immediate push notification |
| `schedule_notification` | Schedule a one-off notification for a future time |
| `schedule_cron_notification` | Schedule recurring notifications using cron syntax |
| `list_scheduled_notifications` | List all recurring cron schedules (optionally filter by topic) |
| `pause_schedule` | Temporarily pause a cron schedule |
| `resume_schedule` | Resume a paused cron schedule |
| `delete_schedule` | Permanently delete a cron schedule |

## Prerequisites

- Python 3.13+
- [uv](https://docs.astral.sh/uv/) package manager
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) 4.50+ (for Docker Sandboxes development)
- [Upstash QStash](https://console.upstash.com/qstash) account and token
- [NTFY](https://ntfy.sh/) topic for receiving notifications (passed as `notification_topic` parameter to each tool)

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

# For local development without auth:
AUTH_DISABLED=true

# Or for production with auth:
# JWT_SECRET=your_secret_here  # Generate with: openssl rand -base64 48
```

Note: The NTFY topic is now specified per-request via the `notification_topic` parameter on each tool call, enabling multi-user and multi-tenant deployments.

### 3. Run the Server

```bash
uv run fastmcp run server.py
```

For development with the MCP Inspector:

```bash
uv run fastmcp dev server.py
```

## Authentication

Cronty MCP supports bearer token authentication using JWT tokens signed with HS512.

### Generating a JWT Secret

Generate a secure secret (minimum 64 characters):

```bash
# macOS/Linux
openssl rand -base64 48

# Or using Python
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

Add the secret to your `.env`:

```bash
JWT_SECRET=your_generated_secret_here
```

### Issuing Tokens

Issue tokens for users via CLI:

```bash
uv run python -m cronty token issue --email user@example.com
```

With custom expiration:

```bash
uv run python -m cronty token issue --email user@example.com --expires-in 30d
```

Supported duration formats: `30d`, `12h`, `1y`, `365d`

### Disabling Authentication

For local development, disable auth by setting:

```bash
AUTH_DISABLED=true
```

## Agent Configuration (Local Mode)

Configure your AI agent to connect to the local MCP server.

**Note:** These configurations run the server locally with `AUTH_DISABLED=true` for development.

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

When deployed to [FastMCP Cloud](https://fastmcp.cloud), you can connect to your server using bearer token authentication.

Replace `your-hostname` with your actual FastMCP Cloud hostname (e.g., `your-app-name.fastmcp.app`).

> **Note:** Bearer token authentication is a temporary solution for clients that don't yet support OAuth 2.0 Dynamic Client Registration (DCR). OAuth with DCR support via WorkOS/Authkit is planned as the preferred authentication method.

### Environment Setup

Set your bearer token as an environment variable:

```bash
export CRONTY_TOKEN="your-token-here"
```

### Issuing Tokens for Cloud Users

Before connecting, issue a token for each user:

```bash
uv run python -m cronty token issue --email user@example.com
```

Users will need this token to authenticate with the cloud-deployed server.

### Obsidian

In the Obsidian MCP plugin settings, add a new server:

| Field | Value |
|-------|-------|
| Server name | Cronty |
| Server URL | `https://your-hostname.fastmcp.app/mcp` |
| Authentication | Bearer Token |
| Token | (paste token from CLI) |

### Claude Code

Using CLI:

```bash
claude mcp add --transport http cronty-mcp https://your-hostname.fastmcp.app/mcp \
  --header "Authorization: Bearer ${CRONTY_TOKEN}"
```

Or add to `.mcp.json`:

```json
{
  "mcpServers": {
    "cronty-mcp": {
      "type": "http",
      "url": "https://your-hostname.fastmcp.app/mcp",
      "headers": {
        "Authorization": "Bearer ${CRONTY_TOKEN}"
      }
    }
  }
}
```

### Claude Desktop

Claude Desktop requires the `mcp-remote` wrapper to add custom headers. Add to `claude_desktop_config.json`:

- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "cronty-mcp": {
      "command": "npx",
      "args": [
        "mcp-remote@latest",
        "https://your-hostname.fastmcp.app/mcp",
        "--header",
        "Authorization: Bearer YOUR_TOKEN"
      ]
    }
  }
}
```

Replace `YOUR_TOKEN` with your actual token from the CLI.

### Codex CLI

Edit `~/.codex/config.toml`:

```toml
[mcp_servers.cronty-mcp]
url = "https://your-hostname.fastmcp.app/mcp"
bearer_token_env_var = "CRONTY_TOKEN"
```

Then set the environment variable before running Codex.

### Gemini CLI

Using CLI:

```bash
gemini mcp add cronty-mcp https://your-hostname.fastmcp.app/mcp \
  --transport http \
  --header "Authorization: Bearer ${CRONTY_TOKEN}"
```

Or edit `settings.json`:

```json
{
  "mcpServers": {
    "cronty-mcp": {
      "httpUrl": "https://your-hostname.fastmcp.app/mcp",
      "headers": {
        "Authorization": "Bearer ${CRONTY_TOKEN}"
      }
    }
  }
}
```

### Cursor

Add to `.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "cronty-mcp": {
      "url": "https://your-hostname.fastmcp.app/mcp",
      "headers": {
        "Authorization": "Bearer ${env:CRONTY_TOKEN}"
      }
    }
  }
}
```

Note: Cursor uses `${env:VAR}` syntax for environment variables.

### VS Code

Add to `.vscode/mcp.json`:

```json
{
  "inputs": [
    {
      "type": "promptString",
      "id": "cronty-token",
      "description": "Cronty MCP Bearer Token",
      "password": true
    }
  ],
  "servers": {
    "cronty-mcp": {
      "type": "http",
      "url": "https://your-hostname.fastmcp.app/mcp",
      "headers": {
        "Authorization": "Bearer ${input:cronty-token}"
      }
    }
  }
}
```

VS Code will securely prompt for your token on first use.

### FastMCP Python Client

```python
import asyncio
from fastmcp import Client
from fastmcp.client.auth import BearerAuth

client = Client(
    "https://your-hostname.fastmcp.app/mcp",
    auth=BearerAuth("your-token-here")
)

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
import os
from openai import OpenAI

client = OpenAI()

resp = client.responses.create(
    model="gpt-4.1",
    tools=[
        {
            "type": "mcp",
            "server_label": "cronty-mcp",
            "server_url": "https://your-hostname.fastmcp.app/mcp",
            "headers": {
                "Authorization": f"Bearer {os.environ['CRONTY_TOKEN']}"
            },
            "require_approval": "never",
        },
    ],
    input="Send me a test notification",
)
```

### OAuth Authentication (Coming Soon)

OAuth 2.0 with Dynamic Client Registration (DCR) support via WorkOS/Authkit is planned. This will enable:

- Automatic token refresh
- Secure authorization flows
- No manual token management

Clients with native OAuth DCR support (Claude Code, VS Code, Cursor) will be able to authenticate without bearer tokens once implemented.

## Evaluations

Run evaluations against your MCP server using Claude to verify tool effectiveness.

### Setup

Add your Anthropic API key to `.env`:

```bash
# In .env
ANTHROPIC_EVAL_API_KEY=your_api_key_here
```

> **Note:** Requires an Anthropic API key from [console.anthropic.com](https://console.anthropic.com). Claude Max subscription does not include API access. The evaluation harness uses `ANTHROPIC_EVAL_API_KEY` (not `ANTHROPIC_API_KEY`) to avoid accidental charges when using Claude Code with a different billing setup.

### Create an Evaluation File

Create an XML file with question-answer pairs (see `evaluation.xml` for examples):

```xml
<evaluation>
   <qa_pair>
      <question>Use the send_push_notification tool with message "test" and notification_topic "demo". Did it succeed? Answer: Yes or No.</question>
      <answer>Yes</answer>
   </qa_pair>
</evaluation>
```

### Run Evaluations

#### From Project Root

```bash
uv run python plugins/fastmcp-builder/skills/fastmcp-builder/scripts/evaluation.py \
    -c "uv run fastmcp run server.py" \
    evaluation.xml
```

Against HTTP server:

```bash
uv run python plugins/fastmcp-builder/skills/fastmcp-builder/scripts/evaluation.py \
    -t http \
    -u https://your-hostname.fastmcp.app/mcp \
    evaluation.xml
```

With custom model and output:

```bash
uv run python plugins/fastmcp-builder/skills/fastmcp-builder/scripts/evaluation.py \
    -c "uv run fastmcp run server.py" \
    -m claude-sonnet-4-20250514 \
    -o report.md \
    evaluation.xml
```

#### From Scripts Directory (Alternative)

If you don't want evaluation dependencies in your project:

```bash
cd plugins/fastmcp-builder/skills/fastmcp-builder/scripts
uv sync
uv run python evaluation.py \
    -c "uv run fastmcp run server.py" \
    --cwd ../../../../.. \
    ../../../../../evaluation.xml
```

### Evaluation Guidelines

- Questions must be **READ-ONLY, INDEPENDENT, NON-DESTRUCTIVE, IDEMPOTENT**
- Answers must be **single, verifiable values** (not lists or objects)
- Answers must be **STABLE** (won't change over time)
- Create **challenging questions** that require multiple tool calls

See `plugins/fastmcp-builder/skills/fastmcp-builder/reference/evaluation.md` for the complete guide.

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

### Testing with Claude Code

#### Local Mode (stdio)

For local development, use stdio transport with auth disabled. Set in `.env`:

```bash
AUTH_DISABLED=true
```

The repo includes `.mcp.json` for local testing:

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

Then run Claude Code from this directory - it will automatically detect the MCP server.

#### Cloud Mode (HTTP with bearer token)

To test against FastMCP Cloud deployment:

1. Set your token:
   ```bash
   export CRONTY_TOKEN="your-token-here"
   ```

2. Update `.mcp.json` to use HTTP transport:
   ```json
   {
     "mcpServers": {
       "cronty-mcp": {
         "type": "http",
         "url": "https://your-hostname.fastmcp.app/mcp",
         "headers": {
           "Authorization": "Bearer ${CRONTY_TOKEN}"
         }
       }
     }
   }
   ```

3. Run Claude Code with the env var set.

## Claude Code with Docker Sandboxes

Run Claude Code in an isolated Docker container with all dependencies pre-installed.

### Build the Custom Template

```bash
docker build -t cronty-dev .
```

### Set Environment Variables

The `.env` file is not mounted in the container for security. Set variables in your shell:

```bash
# Option 1: Source from .env file
set -a; source .env; set +a

# Option 2: Add to ~/.zshrc or ~/.bashrc for persistence
export QSTASH_TOKEN=your_qstash_token_here
export ANTHROPIC_EVAL_API_KEY=your_api_key_here  # Required for running evaluations
export JWT_SECRET=your_jwt_secret_here           # Required if AUTH_DISABLED is not set
```

### Run Claude Code in Sandbox

```bash
# Development mode (auth disabled)
docker sandbox run \
  -e QSTASH_TOKEN=$QSTASH_TOKEN \
  -e AUTH_DISABLED=true \
  --template cronty-dev claude

# Continue a previous conversation
docker sandbox run \
  -e QSTASH_TOKEN=$QSTASH_TOKEN \
  -e AUTH_DISABLED=true \
  --template cronty-dev claude -c

# With a direct prompt
docker sandbox run \
  -e QSTASH_TOKEN=$QSTASH_TOKEN \
  -e AUTH_DISABLED=true \
  --template cronty-dev claude "Run the tests"

# With auth enabled and evaluation support
docker sandbox run \
  -e QSTASH_TOKEN=$QSTASH_TOKEN \
  -e JWT_SECRET=$JWT_SECRET \
  -e ANTHROPIC_EVAL_API_KEY=$ANTHROPIC_EVAL_API_KEY \
  --template cronty-dev claude
```

### Claude Settings in Sandbox

Global Claude settings (`~/.claude/settings.json`) are not available inside the sandbox due to security restrictions. To use custom settings (hooks, permissions, preferences), create a local settings file in the project:

```bash
# Create local settings file
cp ~/.claude/settings.json .claude/settings.local.json
```

The `.claude/settings.local.json` file is mounted with the project and will be used by Claude Code inside the sandbox.

### Available Commands Inside Sandbox

All uv commands work inside the sandbox:

```bash
uv run pytest                    # Run tests
uv run fastmcp dev server.py     # Start dev server with MCP Inspector
uv run ruff check .              # Lint code
uv add some-package              # Add dependencies
```

### What's Included

The Docker Sandbox template includes:
- Claude Code with automatic credential handling
- Python 3.13 with uv package manager
- All project dependencies pre-installed
- Docker CLI, GitHub CLI, Git, Node.js, Go
- Non-root `agent` user with sudo privileges

## Plugin Marketplace

This repository includes the **fastmcp-builder** skill as a Claude Code plugin, providing comprehensive guidance for building production-quality MCP servers with FastMCP.

### Installation

1. Add the marketplace:
   ```
   /plugin marketplace add cronty-com/cronty-mcp
   ```

2. Install the plugin:
   ```
   /plugin install fastmcp-builder@cronty-plugins
   ```

### Usage

Invoke the skill to get guidance on building FastMCP servers:

```
/fastmcp-builder
```

The plugin includes:

- **SKILL.md** - Comprehensive 4-phase guide for building MCP servers (research, implementation, review, evaluation)
- **reference/best-practices.md** - Naming conventions, response formats, security patterns
- **reference/python-guide.md** - Pydantic v2 patterns, async operations, pagination
- **reference/evaluation.md** - Guide for creating evaluation test suites
- **scripts/evaluation.py** - Evaluation harness for testing MCP servers with Claude

For running evaluations, see the [Evaluations](#evaluations) section above.

## License

MIT
