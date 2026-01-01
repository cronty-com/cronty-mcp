# FastMCP Python Implementation Guide

## Quick Reference

### Key Imports
```python
from fastmcp import FastMCP, Context
from fastmcp.exceptions import ToolError
from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import Annotated, Optional, List, Dict, Any
from enum import Enum
import httpx
```

### Server Initialization
```python
mcp = FastMCP("service_mcp")
```

### Tool Registration Pattern
```python
@mcp.tool(name="service_action", annotations={...})
async def tool_function(params: InputModel) -> str:
    pass
```

---

## Server Naming Convention

**Format**: `{service}_mcp` (lowercase with underscores)

Examples: `github_mcp`, `slack_mcp`, `stripe_mcp`

---

## Tool Implementation

### Tool Structure with FastMCP

```python
from typing import Annotated
from pydantic import BaseModel, Field, ConfigDict
from fastmcp import FastMCP
from fastmcp.exceptions import ToolError

mcp = FastMCP("service_mcp")

class ServiceToolInput(BaseModel):
    """Input model for service tool operation."""
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra='forbid'
    )

    param1: str = Field(
        ...,
        description="First parameter (e.g., 'user123')",
        min_length=1,
        max_length=100
    )
    param2: Optional[int] = Field(
        default=None,
        description="Optional integer parameter",
        ge=0,
        le=1000
    )

@mcp.tool(
    name="service_tool_name",
    annotations={
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True
    }
)
async def service_tool_name(params: ServiceToolInput) -> str:
    """Tool description becomes the MCP description field.

    Detailed explanation of what this tool does.
    """
    # Implementation
    pass
```

### Alternative: Simple Parameters with Annotated

For simpler tools, use `Annotated` directly:

```python
@mcp.tool
def get_user(
    user_id: Annotated[str, Field(description="User ID to retrieve")],
    include_metadata: Annotated[bool, Field(description="Include metadata")] = False,
) -> dict:
    """Retrieve user information by ID."""
    return {"id": user_id, "metadata": {} if include_metadata else None}
```

---

## Pydantic v2 Patterns

### Model Configuration

```python
from pydantic import BaseModel, Field, field_validator, ConfigDict

class UserInput(BaseModel):
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra='forbid'
    )

    name: str = Field(..., description="User name", min_length=1, max_length=100)
    email: str = Field(..., description="Email address")
    age: int = Field(..., description="User age", ge=0, le=150)

    @field_validator('email')
    @classmethod
    def validate_email(cls, v: str) -> str:
        if '@' not in v:
            raise ValueError("Invalid email format")
        return v.lower()
```

### Key Pydantic v2 Changes

- Use `model_config` instead of nested `Config` class
- Use `@field_validator` instead of deprecated `@validator`
- Use `model_dump()` instead of deprecated `.dict()`
- Validators require `@classmethod` decorator

---

## Response Format Support

```python
from enum import Enum

class ResponseFormat(str, Enum):
    MARKDOWN = "markdown"
    JSON = "json"

class SearchInput(BaseModel):
    query: str = Field(..., description="Search query")
    response_format: ResponseFormat = Field(
        default=ResponseFormat.MARKDOWN,
        description="Output format: 'markdown' or 'json'"
    )

@mcp.tool
async def search_items(params: SearchInput) -> str:
    items = await fetch_items(params.query)

    if params.response_format == ResponseFormat.MARKDOWN:
        lines = [f"# Search Results: '{params.query}'", ""]
        for item in items:
            lines.append(f"- **{item['name']}** (ID: {item['id']})")
        return "\n".join(lines)
    else:
        import json
        return json.dumps({"query": params.query, "items": items}, indent=2)
```

---

## Context Parameter Injection

FastMCP can inject a `Context` parameter for advanced capabilities:

```python
from fastmcp import FastMCP, Context

mcp = FastMCP("service_mcp")

@mcp.tool
async def long_running_task(query: str, ctx: Context) -> str:
    """Task with progress reporting and logging."""

    # Log for debugging
    await ctx.info(f"Starting task with query: {query}")

    # Report progress
    await ctx.report_progress(progress=25, total=100)

    results = await fetch_data(query)
    await ctx.report_progress(progress=75, total=100)

    formatted = format_results(results)
    await ctx.report_progress(progress=100, total=100)

    return formatted
```

**Context capabilities:**
- `ctx.info()`, `ctx.warning()`, `ctx.error()`, `ctx.debug()` - Logging
- `ctx.report_progress(progress, total)` - Progress reporting
- `ctx.read_resource(uri)` - Read MCP resources
- `ctx.request_id` - Current request ID

---

## Pagination Implementation

```python
class ListInput(BaseModel):
    limit: int = Field(default=20, description="Max results", ge=1, le=100)
    offset: int = Field(default=0, description="Results to skip", ge=0)

@mcp.tool
async def list_items(params: ListInput) -> str:
    data = await api_request(limit=params.limit, offset=params.offset)

    response = {
        "total": data["total"],
        "count": len(data["items"]),
        "offset": params.offset,
        "items": data["items"],
        "has_more": data["total"] > params.offset + len(data["items"]),
        "next_offset": params.offset + len(data["items"])
            if data["total"] > params.offset + len(data["items"])
            else None
    }

    import json
    return json.dumps(response, indent=2)
```

---

## Error Handling

```python
from fastmcp.exceptions import ToolError
import httpx

def handle_api_error(e: Exception) -> str:
    """Consistent error formatting."""
    if isinstance(e, httpx.HTTPStatusError):
        status = e.response.status_code
        if status == 404:
            return "Error: Resource not found. Check the ID is correct."
        elif status == 403:
            return "Error: Permission denied."
        elif status == 429:
            return "Error: Rate limit exceeded. Wait before retrying."
        return f"Error: API request failed with status {status}"
    elif isinstance(e, httpx.TimeoutException):
        return "Error: Request timed out. Try again."
    return f"Error: {type(e).__name__}: {str(e)}"

@mcp.tool
async def get_resource(resource_id: str) -> str:
    """Get a resource by ID."""
    if not resource_id:
        raise ToolError("Resource ID is required")

    try:
        return await fetch_resource(resource_id)
    except Exception as e:
        raise ToolError(handle_api_error(e))
```

---

## Shared Utilities Pattern

### API Client

```python
import os
import httpx

class APIClient:
    def __init__(self):
        self.base_url = os.environ["API_BASE_URL"]
        self.api_key = os.environ["API_KEY"]

    async def request(
        self,
        method: str,
        endpoint: str,
        **kwargs
    ) -> dict:
        async with httpx.AsyncClient() as client:
            response = await client.request(
                method,
                f"{self.base_url}/{endpoint}",
                headers={"Authorization": f"Bearer {self.api_key}"},
                timeout=30.0,
                **kwargs
            )
            response.raise_for_status()
            return response.json()

    async def get(self, endpoint: str, **kwargs) -> dict:
        return await self.request("GET", endpoint, **kwargs)

    async def post(self, endpoint: str, **kwargs) -> dict:
        return await self.request("POST", endpoint, **kwargs)
```

---

## Complete Example

```python
#!/usr/bin/env python3
"""MCP Server for Example Service."""

import os
import json
from typing import Optional
from enum import Enum

import httpx
from pydantic import BaseModel, Field, ConfigDict
from fastmcp import FastMCP
from fastmcp.exceptions import ToolError

# Initialize server
mcp = FastMCP("example_mcp")

# Constants
API_BASE_URL = os.environ.get("EXAMPLE_API_URL", "https://api.example.com/v1")
API_KEY = os.environ.get("EXAMPLE_API_KEY")

# Enums
class ResponseFormat(str, Enum):
    MARKDOWN = "markdown"
    JSON = "json"

# Input Models
class SearchUsersInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    query: str = Field(..., description="Search query", min_length=2, max_length=200)
    limit: int = Field(default=20, description="Max results", ge=1, le=100)
    offset: int = Field(default=0, description="Pagination offset", ge=0)
    response_format: ResponseFormat = Field(default=ResponseFormat.MARKDOWN)

# Utilities
async def api_request(endpoint: str, **params) -> dict:
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{API_BASE_URL}/{endpoint}",
            headers={"Authorization": f"Bearer {API_KEY}"},
            params=params,
            timeout=30.0
        )
        response.raise_for_status()
        return response.json()

def handle_error(e: Exception) -> str:
    if isinstance(e, httpx.HTTPStatusError):
        if e.response.status_code == 404:
            return "Error: Resource not found"
        elif e.response.status_code == 429:
            return "Error: Rate limit exceeded"
        return f"Error: API error {e.response.status_code}"
    return f"Error: {str(e)}"

# Tools
@mcp.tool(
    name="example_search_users",
    annotations={
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True
    }
)
async def example_search_users(params: SearchUsersInput) -> str:
    """Search for users in the Example system.

    Returns matching users with pagination support.
    """
    try:
        data = await api_request(
            "users/search",
            q=params.query,
            limit=params.limit,
            offset=params.offset
        )

        users = data.get("users", [])
        total = data.get("total", 0)

        if not users:
            return f"No users found matching '{params.query}'"

        if params.response_format == ResponseFormat.MARKDOWN:
            lines = [
                f"# User Search: '{params.query}'",
                f"Found {total} users (showing {len(users)})",
                ""
            ]
            for user in users:
                lines.append(f"- **{user['name']}** ({user['id']})")
                lines.append(f"  Email: {user['email']}")
            return "\n".join(lines)
        else:
            return json.dumps({
                "total": total,
                "count": len(users),
                "offset": params.offset,
                "has_more": total > params.offset + len(users),
                "users": users
            }, indent=2)

    except Exception as e:
        raise ToolError(handle_error(e))

if __name__ == "__main__":
    if not API_KEY:
        raise ValueError("EXAMPLE_API_KEY environment variable required")
    mcp.run()
```

---

## Quality Checklist

### Strategic Design
- [ ] Tools enable complete workflows, not just API endpoint wrappers
- [ ] Tool names include service prefix (`service_action`)
- [ ] Response formats optimize for agent context efficiency
- [ ] Error messages guide agents toward correct usage

### Implementation Quality
- [ ] Server name follows format: `{service}_mcp`
- [ ] All tools have descriptive docstrings
- [ ] All network operations use async/await
- [ ] Common functionality extracted into reusable functions
- [ ] Error handling is consistent across tools

### Tool Configuration
- [ ] All tools implement `name` and `annotations` in decorator
- [ ] Annotations correctly set (readOnlyHint, destructiveHint, etc.)
- [ ] All tools use Pydantic models or Annotated for validation
- [ ] All Fields have descriptions and constraints
- [ ] Pagination implemented where applicable

### Code Quality
- [ ] Type hints used throughout
- [ ] HTTP client uses async patterns with context managers
- [ ] Constants defined at module level
- [ ] No hardcoded secrets

### Testing
- [ ] Server runs: `uv run python server.py`
- [ ] All imports resolve
- [ ] Sample tool calls work
- [ ] Error scenarios handled
