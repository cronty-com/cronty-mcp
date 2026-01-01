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
    monkeypatch.setenv("NTFY_TOPIC", "test-topic")

    result = await client.call_tool("health", {})
    assert "I am healthy" in str(result)


async def test_health_fails_when_var_missing(client, monkeypatch):
    monkeypatch.delenv("QSTASH_TOKEN", raising=False)
    monkeypatch.setenv("NTFY_TOPIC", "test-topic")

    with pytest.raises(ToolError) as exc_info:
        await client.call_tool("health", {})
    assert "QSTASH_TOKEN" in str(exc_info.value)


async def test_health_fails_when_var_empty(client, monkeypatch):
    monkeypatch.setenv("QSTASH_TOKEN", "test-token")
    monkeypatch.setenv("NTFY_TOPIC", "")

    with pytest.raises(ToolError) as exc_info:
        await client.call_tool("health", {})
    assert "NTFY_TOPIC" in str(exc_info.value)


async def test_health_reports_multiple_missing_vars(client, monkeypatch):
    monkeypatch.delenv("QSTASH_TOKEN", raising=False)
    monkeypatch.delenv("NTFY_TOPIC", raising=False)

    with pytest.raises(ToolError) as exc_info:
        await client.call_tool("health", {})
    assert "QSTASH_TOKEN" in str(exc_info.value)
    assert "NTFY_TOPIC" in str(exc_info.value)
