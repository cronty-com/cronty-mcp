import pytest
from fastmcp.client import Client
from fastmcp.exceptions import ToolError

from server import mcp


@pytest.fixture
async def client():
    async with Client(transport=mcp) as c:
        yield c


async def test_health_returns_healthy_when_all_vars_set(client, monkeypatch):
    monkeypatch.setenv("QSTASH_TOKEN", "test-token")

    result = await client.call_tool("health", {})
    assert "I am healthy" in str(result)


async def test_health_fails_when_qstash_token_missing(client, monkeypatch):
    monkeypatch.delenv("QSTASH_TOKEN", raising=False)

    with pytest.raises(ToolError) as exc_info:
        await client.call_tool("health", {})
    assert "QSTASH_TOKEN" in str(exc_info.value)


async def test_health_fails_when_qstash_token_empty(client, monkeypatch):
    monkeypatch.setenv("QSTASH_TOKEN", "")

    with pytest.raises(ToolError) as exc_info:
        await client.call_tool("health", {})
    assert "QSTASH_TOKEN" in str(exc_info.value)
