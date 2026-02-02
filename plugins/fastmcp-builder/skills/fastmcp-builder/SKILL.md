---
name: fastmcp-builder
description: Guide for creating FastMCP servers in Python. Use for building MCP servers to integrate external APIs, deploy over HTTP, or add MCP to existing FastAPI applications.
---

# FastMCP Server Development Guide

Build high-quality MCP servers using FastMCP that enable LLMs to interact with external services through well-designed tools.

## When to Use This Skill

Use this skill when:
- Building a new MCP server to integrate with an external API
- Adding tools, resources, or prompts to an existing FastMCP server
- Deploying MCP over HTTP (standalone or with existing web app)
- Integrating MCP into a FastAPI application
- Converting existing FastAPI endpoints to MCP tools
- Evaluating whether an MCP server effectively serves its purpose

## Development Process

Follow these four phases in order:

### Phase 1: Research & Planning

**1.1 Study the Target API**
- Read API documentation thoroughly
- Identify authentication requirements
- Map out available endpoints and their purposes
- Note rate limits and pagination patterns

**1.2 Plan Tool Design**

Balance between two approaches:
- **API Coverage**: Mirror API endpoints as tools (more flexibility, steeper learning curve)
- **Workflow Tools**: Create task-oriented tools (easier to use, less flexible)

For most servers, prefer API coverage with clear tool naming.

**1.3 Assess Project Structure**

Before creating files, inspect the existing repository structure:

1. **Check for existing patterns**:
   - Monorepo with `packages/` or `apps/` directories
   - Existing FastAPI application to extend
   - Python package structure with `src/` layout

2. **Adapt to existing structure**:
   - Monorepo: Create under `packages/mcp-server/` or similar
   - Existing FastAPI: Add MCP alongside existing code
   - Existing Python package: Follow established patterns

3. **Default to flat structure** only when:
   - Starting a fresh standalone MCP server
   - Deploying to FastMCP Cloud (requires flat structure)

**Flat Structure** (required for FastMCP Cloud, default for new projects):

```
my-mcp-server/
├── server.py          # FastMCP server entry point
├── config.py          # Environment variable handling
├── tools/             # Tool implementations
│   ├── __init__.py
│   └── my_tools.py
├── services/          # Business logic, API clients
│   ├── __init__.py
│   └── api_client.py
├── tests/             # pytest tests
│   └── test_tools.py
├── pyproject.toml     # Dependencies
└── .env.example       # Environment template
```

**Monorepo Structure** (when adding MCP to existing monorepo):

```
my-monorepo/
├── packages/
│   ├── api/           # Existing API package
│   └── mcp-server/    # New MCP server package
│       ├── server.py
│       ├── tools/
│       ├── services/
│       └── pyproject.toml
└── ...
```

**Adding to Existing FastAPI App** (see section 2.10 for integration patterns):

```
my-fastapi-app/
├── main.py            # Existing FastAPI app
├── mcp_server.py      # New MCP server module
├── tools/             # MCP tools
└── ...
```

### Phase 2: Implementation

**2.1 Project Setup**

Choose your preferred package manager:

**Option A: uv (recommended for new projects)**
```bash
uv init my-mcp-server
cd my-mcp-server
uv add fastmcp
uv add --dev pytest pytest-asyncio ruff
```

**Option B: pip**
```bash
mkdir my-mcp-server && cd my-mcp-server
python -m venv .venv && source .venv/bin/activate
pip install fastmcp pytest pytest-asyncio ruff
```

**Option C: poetry**
```bash
poetry new my-mcp-server
cd my-mcp-server
poetry add fastmcp
poetry add --group dev pytest pytest-asyncio ruff
```

**pyproject.toml**:
```toml
[project]
name = "my-mcp-server"
version = "0.1.0"
requires-python = ">=3.13"
dependencies = ["fastmcp<3"]

[tool.pytest.ini_options]
asyncio_mode = "auto"

[tool.ruff]
line-length = 88

[tool.ruff.lint]
select = ["E", "F", "I", "UP"]
```

**2.2 Server Entry Point**

```python
# server.py
from dotenv import load_dotenv
from fastmcp import FastMCP

from tools import my_tool

load_dotenv()

mcp = FastMCP("My Server Name")

mcp.tool(my_tool)

if __name__ == "__main__":
    mcp.run()
```

**2.3 Configuration**

```python
# config.py
import os

REQUIRED_ENV_VARS = [
    "API_KEY",
    "API_BASE_URL",
]

def get_missing_env_vars() -> list[str]:
    missing = []
    for var in REQUIRED_ENV_VARS:
        if not os.environ.get(var):
            missing.append(var)
    return missing
```

**2.4 Tools**

Basic tool:
```python
from fastmcp import FastMCP

mcp = FastMCP("Demo")

@mcp.tool
def get_user(user_id: str) -> dict:
    """Retrieve user information by ID."""
    return {"id": user_id, "name": "Example User"}
```

Tool with validation using Pydantic Field:
```python
from typing import Annotated
from pydantic import Field
from fastmcp.exceptions import ToolError

@mcp.tool
def create_item(
    name: Annotated[str, Field(description="Item name", min_length=1, max_length=100)],
    quantity: Annotated[int, Field(description="Quantity", ge=1, le=1000)] = 1,
    category: Annotated[str | None, Field(description="Optional category")] = None,
) -> dict:
    """Create a new item in the inventory."""
    if not name.strip():
        raise ToolError("Name cannot be empty")
    return {"name": name, "quantity": quantity, "category": category}
```

Tool with regex pattern validation:
```python
from typing import Annotated
from pydantic import Field

TOPIC_PATTERN = r"^[a-z0-9]+(-[a-z0-9]+)*$"

@mcp.tool
def send_notification(
    message: Annotated[str, Field(description="Message text")],
    topic: Annotated[str, Field(
        description="Topic name (lowercase alphanumeric with dashes)",
        pattern=TOPIC_PATTERN,
    )],
) -> dict:
    """Send a notification to a topic."""
    return {"status": "sent", "topic": topic}
```
Use `pattern` for regex validation instead of custom validators. Pydantic will automatically reject invalid values and include "pattern" in the error message.

Tool with context access:
```python
from fastmcp import FastMCP, Context

@mcp.tool
async def process_data(data_uri: str, ctx: Context) -> dict:
    """Process data from a resource."""
    await ctx.info(f"Processing {data_uri}")
    await ctx.report_progress(progress=50, total=100)
    # ... processing logic
    await ctx.report_progress(progress=100, total=100)
    return {"status": "complete"}
```

**2.5 Resources**

Static resource:
```python
@mcp.resource("config://app")
def get_config() -> dict:
    """Application configuration."""
    return {"version": "1.0", "environment": "production"}
```

Dynamic resource with URI template:
```python
@mcp.resource("users://{user_id}/profile")
def get_user_profile(user_id: str) -> dict:
    """Get user profile by ID."""
    return {"id": user_id, "name": f"User {user_id}"}
```

**2.6 Prompts**

```python
@mcp.prompt
def analyze_data(data_type: str) -> str:
    """Generate analysis prompt for specific data type."""
    return f"Analyze the following {data_type} data and provide insights..."
```

**2.7 Error Handling**

Always use ToolError for user-facing errors:
```python
from fastmcp.exceptions import ToolError

@mcp.tool
def divide(a: float, b: float) -> float:
    """Divide a by b."""
    if b == 0:
        raise ToolError("Cannot divide by zero")
    return a / b
```

**2.8 Service Layer**

Keep tools thin, delegate to services:
```python
# services/api_client.py
import os
import httpx

class APIClient:
    def __init__(self):
        self.base_url = os.environ["API_BASE_URL"]
        self.api_key = os.environ["API_KEY"]

    def get_item(self, item_id: str) -> dict:
        with httpx.Client() as client:
            response = client.get(
                f"{self.base_url}/items/{item_id}",
                headers={"Authorization": f"Bearer {self.api_key}"}
            )
            response.raise_for_status()
            return response.json()
```

**2.9 HTTP Deployment**

Choose based on your needs:

**Option A: Direct HTTP Server** (simplest)
```python
# server.py
from fastmcp import FastMCP

mcp = FastMCP("My Server")

@mcp.tool
def my_tool(input: str) -> str:
    """Process input."""
    return f"Processed: {input}"

if __name__ == "__main__":
    mcp.run(transport="http", host="0.0.0.0", port=8000)
```
Endpoint: `http://localhost:8000/mcp`

**Option B: ASGI Application** (production)
```python
# server.py
from fastmcp import FastMCP

mcp = FastMCP("My Server")

@mcp.tool
def my_tool(input: str) -> str:
    """Process input."""
    return f"Processed: {input}"

app = mcp.http_app()
```
Run with: `uvicorn server:app --host 0.0.0.0 --port 8000`

**Custom path and middleware:**
```python
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware

middleware = [
    Middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"])
]
app = mcp.http_app(path="/api/mcp/", middleware=middleware)
```

**Stateless mode (for horizontal scaling):**
```python
mcp = FastMCP("Server", stateless_http=True)
app = mcp.http_app()
# Or: FASTMCP_STATELESS_HTTP=true uvicorn server:app --workers 4
```

**2.10 FastAPI Integration**

**Mount MCP into existing FastAPI app:**
```python
from fastapi import FastAPI
from fastmcp import FastMCP

# Your existing FastAPI app
api = FastAPI(title="My API")

@api.get("/items/{item_id}")
def get_item(item_id: int):
    return {"id": item_id, "name": "Example"}

# Create MCP server with tools
mcp = FastMCP("API Tools")

@mcp.tool
def analyze_item(item_id: int) -> dict:
    """Analyze an item."""
    return {"item_id": item_id, "analysis": "Good condition"}

# Mount MCP into FastAPI
mcp_app = mcp.http_app(path="/mcp")
api = FastAPI(title="My API", lifespan=mcp_app.lifespan)  # Pass lifespan!
api.mount("/mcp", mcp_app)

# Results:
# - REST API: http://localhost:8000/items/123
# - MCP: http://localhost:8000/mcp
```

**Convert FastAPI to MCP (auto-generate tools from endpoints):**
```python
from fastapi import FastAPI
from fastmcp import FastMCP

app = FastAPI()

@app.get("/users/{user_id}", operation_id="get_user")
def get_user(user_id: int):
    return {"id": user_id, "name": "John"}

@app.post("/users", operation_id="create_user")
def create_user(name: str):
    return {"id": 1, "name": name}

# Convert all endpoints to MCP tools
mcp = FastMCP.from_fastapi(app=app)

if __name__ == "__main__":
    mcp.run()
```

**Combined: REST + MCP from same endpoints:**
```python
from fastapi import FastAPI
from fastmcp import FastMCP

app = FastAPI()

@app.get("/products/{id}", operation_id="get_product")
def get_product(id: int):
    return {"id": id, "name": "Widget"}

# Convert to MCP and create combined app
mcp = FastMCP.from_fastapi(app=app, name="Products MCP")
mcp_app = mcp.http_app(path="/mcp")

combined = FastAPI(
    title="Products API + MCP",
    routes=[*mcp_app.routes, *app.routes],
    lifespan=mcp_app.lifespan,
)

# REST: http://localhost:8000/products/1
# MCP: http://localhost:8000/mcp
```

**Important:** Always pass `lifespan=mcp_app.lifespan` to FastAPI for proper session management.

### Phase 3: Review & Testing

**3.1 Code Quality Checklist**

- [ ] No code duplication
- [ ] Consistent error handling with ToolError
- [ ] All tools have descriptive docstrings
- [ ] Type hints on all function signatures
- [ ] Environment variables validated at startup
- [ ] No hardcoded secrets

**3.2 Testing Pattern**

```python
# tests/test_tools.py
from unittest.mock import MagicMock, patch
import pytest
from fastmcp.client import Client
from fastmcp.exceptions import ToolError

from server import mcp

@pytest.fixture
async def client():
    async with Client(transport=mcp) as c:
        yield c

@pytest.fixture
def env_vars(monkeypatch):
    monkeypatch.setenv("API_KEY", "test-key")
    monkeypatch.setenv("API_BASE_URL", "https://api.example.com")

async def test_get_user_success(client, env_vars):
    result = await client.call_tool("get_user", {"user_id": "123"})
    assert "123" in str(result)

async def test_create_item_validation(client, env_vars):
    with pytest.raises(ToolError):
        await client.call_tool("create_item", {"name": "", "quantity": 1})
```

**3.3 Running & Debugging**

Adapt commands to your package manager:
- **uv**: prefix with `uv run`
- **pip**: activate venv first, then run directly
- **poetry**: prefix with `poetry run`

```bash
# Development with MCP Inspector
fastmcp dev server.py

# Run directly
python server.py

# Run tests
pytest -v

# Lint
ruff check . --fix
ruff format .
```

### Phase 4: Evaluation

Create 10 test questions that verify the server enables real tasks.

**Question Design:**
- Questions should be independent (don't chain results)
- Answers must be single, verifiable values (not lists or objects)
- Answers must be stable (won't change over time)
- Cover different tool capabilities
- Include edge cases

**REQUIRED XML Format:**

```xml
<evaluation>
  <qa_pair>
    <question>Get the current UTC time. Does the response include an ISO timestamp? Answer yes or no.</question>
    <answer>yes</answer>
  </qa_pair>
  <qa_pair>
    <question>How many fields does the get_user tool return? Answer with just the number.</question>
    <answer>3</answer>
  </qa_pair>
  <qa_pair>
    <question>Call get_item with an invalid ID "xyz". Does the error message mention "not found"? Answer yes or no.</question>
    <answer>yes</answer>
  </qa_pair>
</evaluation>
```

**Important:** Use `<qa_pair>`, `<question>`, and `<answer>` tags. The answer must be a single verifiable value that can be checked via string comparison.

## Best Practices

### Tool Naming
- Use clear, action-oriented names: `create_user`, `list_items`, `delete_record`
- Prefix with service name: `slack_send_message`, `github_create_issue`
- Be specific: `search_products` not `search`

### Descriptions
- Tool docstrings are shown to LLMs - make them clear and complete
- Include parameter constraints in Field descriptions
- Explain return value structure

### Async vs Sync
- FastMCP handles both, but prefer async for I/O operations
- Use `anyio.to_thread.run_sync()` for blocking operations

### Error Messages
- Make errors actionable: "Invalid date format. Use YYYY-MM-DD"
- Include current state when helpful: "Scheduled time must be in the future. Current time: ..."

For comprehensive best practices, see `reference/best-practices.md`.

## Reference Files

This skill includes detailed reference guides:

| File                                          | Purpose                                                     |
|-----------------------------------------------|-------------------------------------------------------------|
| [Best Practices](reference/best-practices.md) | Server naming, tool design, pagination, transport, security |
| [Python Guide](reference/python-guide.md)     | Pydantic v2 patterns, context injection, complete examples  |
| [Evaluation](reference/evaluation.md)         | Creating evaluations to test MCP server effectiveness       |

## Evaluation Scripts

The `scripts/` directory contains a complete evaluation harness:

| File                            | Purpose                                              |
|---------------------------------|------------------------------------------------------|
| [evaluation.py](scripts/evaluation.py) | FastMCP + Claude evaluation harness          |
| [example.xml](scripts/example.xml)     | Example evaluation file with sample questions |
| [pyproject.toml](scripts/pyproject.toml) | Dependencies for uv                         |
| [requirements.txt](scripts/requirements.txt) | Dependencies for pip                    |

**Quick start (from your project directory):**
```bash
# Find the plugin cache path (version-independent)
EVAL_SCRIPTS=$(find ~/.claude/plugins/cache/cronty-plugins/fastmcp-builder -name "evaluation.py" -exec dirname {} \; | head -1)

# Install dependencies (one time)
cd $EVAL_SCRIPTS && uv sync && cd -

# Set API key
export ANTHROPIC_EVAL_API_KEY=your_key

# Run evaluation
uv run python $EVAL_SCRIPTS/evaluation.py \
  -c "uv run fastmcp run server.py" \
  evaluation.xml
```

**CLI Options:**
- `-c, --command` - Command to start the server (for stdio transport)
- `-t, --transport` - `stdio` (default) or `http`
- `-u, --url` - Server URL (for http transport)
- `--cwd` - Working directory for the server command
- `-m, --model` - Claude model (default: claude-haiku-4-5)
- `-o, --output` - Output file for report

## External References

- FastMCP Documentation: https://gofastmcp.com/llms.txt
- MCP Protocol: https://modelcontextprotocol.io/llms.txt
