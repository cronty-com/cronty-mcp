# FastMCP Best Practices

## Quick Reference

### Server Naming
- **Format**: `{service}_mcp` (lowercase with underscores)
- **Examples**: `slack_mcp`, `github_mcp`, `stripe_mcp`

### Tool Naming
- Use snake_case with service prefix
- Format: `{service}_{action}_{resource}`
- Examples: `slack_send_message`, `github_create_issue`, `stripe_list_payments`

### Response Formats
- Support both JSON and Markdown formats
- JSON for programmatic processing
- Markdown for human readability

### Pagination
- Always respect `limit` parameter
- Return `has_more`, `next_offset`, `total_count`
- Default to 20-50 items

### Transport
- **Streamable HTTP**: Remote servers, multi-client scenarios
- **stdio**: Local integrations, command-line tools

---

## Server Naming Convention

Follow this standardized naming pattern:

**Format**: `{service}_mcp` (lowercase with underscores)

The name should be:
- General (not tied to specific features)
- Descriptive of the service/API being integrated
- Easy to infer from the task description
- Without version numbers or dates

---

## Tool Naming and Design

### Tool Naming

1. **Use snake_case**: `search_users`, `create_project`, `get_channel_info`

2. **Include service prefix**: Anticipate your MCP server being used alongside others
   - Use `slack_send_message` instead of just `send_message`
   - Use `github_create_issue` instead of just `create_issue`

3. **Be action-oriented**: Start with verbs (get, list, search, create, update, delete)

4. **Be specific**: `search_products` not `search`

### Tool Design

- Tool descriptions must narrowly and unambiguously describe functionality
- Descriptions must precisely match actual functionality
- Provide tool annotations (see below)
- Keep tool operations focused and atomic

---

## Response Formats

Support multiple formats for flexibility:

### JSON Format (`response_format="json"`)
- Machine-readable structured data
- Include all available fields and metadata
- Consistent field names and types
- Use for programmatic processing

### Markdown Format (`response_format="markdown"`)
- Human-readable formatted text
- Use headers, lists, and formatting for clarity
- Convert timestamps to human-readable format
- Show display names with IDs in parentheses
- Omit verbose metadata

```python
from enum import Enum

class ResponseFormat(str, Enum):
    MARKDOWN = "markdown"
    JSON = "json"
```

---

## Pagination

For tools that list resources:

- **Always respect the `limit` parameter**
- **Implement pagination**: Use `offset` or cursor-based pagination
- **Return pagination metadata**: Include `has_more`, `next_offset`/`next_cursor`, `total_count`
- **Never load all results into memory**
- **Default to reasonable limits**: 20-50 items is typical

Example pagination response:
```python
{
    "total": 150,
    "count": 20,
    "offset": 0,
    "items": [...],
    "has_more": True,
    "next_offset": 20
}
```

---

## Transport Options

### Streamable HTTP

**Best for**: Remote servers, web services, multi-client scenarios

**Use when**:
- Serving multiple clients simultaneously
- Deploying as a cloud service
- Integration with web applications

```python
mcp.run(transport="http", host="0.0.0.0", port=8000)
# Or ASGI: app = mcp.http_app()
```

### stdio

**Best for**: Local integrations, command-line tools

**Use when**:
- Building tools for local development
- Integrating with desktop applications
- Single-user, single-session scenarios

```python
mcp.run()  # Default is stdio
```

**Note**: stdio servers should NOT log to stdout (use stderr for logging)

### Transport Selection

| Criterion | stdio | Streamable HTTP |
|-----------|-------|-----------------|
| Deployment | Local | Remote |
| Clients | Single | Multiple |
| Complexity | Low | Medium |
| Real-time | No | Yes |

---

## Tool Annotations

Provide annotations to help clients understand tool behavior:

```python
@mcp.tool(
    name="github_list_repos",
    annotations={
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True
    }
)
```

| Annotation | Type | Default | Description |
|-----------|------|---------|-------------|
| `readOnlyHint` | bool | False | Tool does not modify its environment |
| `destructiveHint` | bool | True | Tool may perform destructive updates |
| `idempotentHint` | bool | False | Repeated calls with same args have no additional effect |
| `openWorldHint` | bool | True | Tool interacts with external entities |

**Important**: Annotations are hints, not security guarantees.

---

## Security Best Practices

### API Keys and Secrets

- Store API keys in environment variables, never in code
- Validate keys on server startup
- Provide clear error messages when authentication fails

```python
import os

API_KEY = os.environ.get("SERVICE_API_KEY")
if not API_KEY:
    raise ValueError("SERVICE_API_KEY environment variable required")
```

### Input Validation

- Use Pydantic models with constraints for all inputs
- Sanitize file paths to prevent directory traversal
- Validate URLs and external identifiers
- Check parameter sizes and ranges

```python
from pydantic import Field

class SearchInput(BaseModel):
    query: str = Field(..., min_length=1, max_length=500)
    limit: int = Field(default=20, ge=1, le=100)
```

### Error Handling

- Don't expose internal errors to clients
- Use `ToolError` for user-facing errors
- Mask internal details with `mask_error_details=True`

```python
mcp = FastMCP("Server", mask_error_details=True)
```

---

## Error Handling

Provide clear, actionable error messages:

```python
from fastmcp.exceptions import ToolError

@mcp.tool
def get_user(user_id: str) -> dict:
    if not user_id:
        raise ToolError("User ID is required. Example: 'U123456789'")

    try:
        return fetch_user(user_id)
    except NotFoundError:
        raise ToolError(
            f"User '{user_id}' not found. "
            "Use list_users to find valid user IDs."
        )
    except RateLimitError:
        raise ToolError(
            "Rate limit exceeded. Please wait before making more requests."
        )
```

**Error message guidelines:**
- Be specific about what went wrong
- Include valid examples where helpful
- Suggest next steps or alternative tools
- Don't expose internal implementation details

---

## Documentation Requirements

Every tool should have:

1. **Clear description** in docstring (becomes tool description)
2. **Parameter documentation** via Field descriptions
3. **Return type documentation** including schema structure
4. **Examples** of when to use (and when not to)
5. **Error scenarios** and how they're handled

---

## Testing Requirements

Comprehensive testing should cover:

- **Functional testing**: Verify correct execution with valid/invalid inputs
- **Integration testing**: Test interaction with external systems
- **Error handling**: Ensure proper error reporting and cleanup
- **Pagination**: Test boundary conditions

```python
@pytest.fixture
async def client():
    async with Client(transport=mcp) as c:
        yield c

async def test_tool_success(client, env_vars):
    result = await client.call_tool("tool_name", {"param": "value"})
    assert "expected" in str(result)

async def test_tool_validation_error(client, env_vars):
    with pytest.raises(ToolError):
        await client.call_tool("tool_name", {"param": ""})
```
