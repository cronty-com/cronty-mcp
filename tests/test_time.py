from datetime import UTC, datetime
from unittest.mock import patch

import pytest
from fastmcp.client import Client

from server import mcp


@pytest.fixture
async def client():
    async with Client(mcp) as c:
        yield c


@pytest.fixture
def env_vars(monkeypatch):
    monkeypatch.setenv("QSTASH_TOKEN", "test-token")


class TestGetCurrentTime:
    async def test_returns_utc_timestamp(self, client, env_vars):
        result = await client.call_tool("get_current_time", {})
        assert "utc" in result.data
        assert "UTC" in result.data["utc"] or "+00:00" in result.data["utc"]

    async def test_returns_date_in_correct_format(self, client, env_vars):
        result = await client.call_tool("get_current_time", {})
        date = result.data["date"]
        datetime.strptime(date, "%Y-%m-%d")

    async def test_returns_time_in_correct_format(self, client, env_vars):
        result = await client.call_tool("get_current_time", {})
        time = result.data["time"]
        datetime.strptime(time, "%H:%M")

    async def test_returns_timezone_utc(self, client, env_vars):
        result = await client.call_tool("get_current_time", {})
        assert result.data["timezone"] == "UTC"

    async def test_returns_all_expected_fields(self, client, env_vars):
        result = await client.call_tool("get_current_time", {})
        assert set(result.data.keys()) == {"utc", "date", "time", "timezone"}

    async def test_time_is_current(self, client, env_vars):
        before = datetime.now(UTC)
        result = await client.call_tool("get_current_time", {})
        after = datetime.now(UTC)

        returned_time = datetime.fromisoformat(result.data["utc"])
        assert before <= returned_time <= after


class TestGetCurrentTimeUnit:
    def test_returns_correct_format(self):
        from tools.time import get_current_time

        result = get_current_time()
        assert isinstance(result, dict)
        assert "utc" in result
        assert "date" in result
        assert "time" in result
        assert "timezone" in result

    def test_with_mocked_datetime(self):
        from tools.time import get_current_time

        fixed_time = datetime(2026, 6, 15, 14, 30, 45, tzinfo=UTC)

        with patch("tools.time.datetime") as mock_dt:
            mock_dt.now.return_value = fixed_time
            mock_dt.side_effect = lambda *args, **kw: datetime(*args, **kw)

            result = get_current_time()

            assert result["utc"] == "2026-06-15T14:30:45+00:00"
            assert result["date"] == "2026-06-15"
            assert result["time"] == "14:30"
            assert result["timezone"] == "UTC"
