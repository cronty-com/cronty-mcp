from datetime import UTC, datetime, timedelta
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
def mock_qstash():
    with patch("services.qstash.QStash") as mock_class:
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.message_id = "test-message-id-123"
        mock_client.message.publish_json.return_value = mock_response
        mock_class.return_value = mock_client
        yield mock_client


@pytest.fixture
def env_vars(monkeypatch):
    monkeypatch.setenv("QSTASH_TOKEN", "test-token")
    monkeypatch.setenv("QSTASH_CURRENT_SIGNING_KEY", "current-key")
    monkeypatch.setenv("QSTASH_NEXT_SIGNING_KEY", "next-key")
    monkeypatch.setenv("NTFY_TOPIC", "test-topic")


def future_datetime_iso() -> str:
    future = datetime.now(UTC) + timedelta(hours=1)
    return future.isoformat()


def future_date() -> str:
    future = datetime.now(UTC) + timedelta(days=1)
    return future.strftime("%Y-%m-%d")


def past_datetime_iso() -> str:
    past = datetime.now(UTC) - timedelta(hours=1)
    return past.isoformat()


class TestScheduleWithDatetime:
    async def test_success_with_iso_datetime(self, client, mock_qstash, env_vars):
        future_dt = future_datetime_iso()
        result = await client.call_tool(
            "schedule_notification",
            {"message": "Call mom", "datetime": future_dt},
        )
        result_str = str(result)
        assert "test-message-id-123" in result_str
        assert "scheduled" in result_str.lower()

    async def test_reject_past_datetime(self, client, mock_qstash, env_vars):
        past_dt = past_datetime_iso()
        with pytest.raises(ToolError) as exc_info:
            await client.call_tool(
                "schedule_notification",
                {"message": "Too late", "datetime": past_dt},
            )
        assert "future" in str(exc_info.value).lower()

    async def test_invalid_datetime_format(self, client, mock_qstash, env_vars):
        with pytest.raises(ToolError) as exc_info:
            await client.call_tool(
                "schedule_notification",
                {"message": "Test", "datetime": "not-a-datetime"},
            )
        assert "invalid" in str(exc_info.value).lower()

    async def test_datetime_without_timezone(self, client, mock_qstash, env_vars):
        with pytest.raises(ToolError) as exc_info:
            await client.call_tool(
                "schedule_notification",
                {"message": "Test", "datetime": "2025-12-31T09:00:00"},
            )
        assert "timezone" in str(exc_info.value).lower()


class TestScheduleWithSeparateParams:
    async def test_success_with_date_time_timezone(
        self, client, mock_qstash, env_vars
    ):
        future = future_date()
        result = await client.call_tool(
            "schedule_notification",
            {
                "message": "Team standup",
                "date": future,
                "time": "09:00",
                "timezone": "Europe/Warsaw",
            },
        )
        result_str = str(result)
        assert "test-message-id-123" in result_str

    async def test_missing_timezone(self, client, mock_qstash, env_vars):
        future = future_date()
        with pytest.raises(ToolError) as exc_info:
            await client.call_tool(
                "schedule_notification",
                {"message": "Test", "date": future, "time": "09:00"},
            )
        assert "timezone" in str(exc_info.value).lower()

    async def test_missing_time(self, client, mock_qstash, env_vars):
        future = future_date()
        with pytest.raises(ToolError) as exc_info:
            await client.call_tool(
                "schedule_notification",
                {"message": "Test", "date": future, "timezone": "Europe/Warsaw"},
            )
        assert "time" in str(exc_info.value).lower()

    async def test_invalid_timezone(self, client, mock_qstash, env_vars):
        future = future_date()
        with pytest.raises(ToolError) as exc_info:
            await client.call_tool(
                "schedule_notification",
                {
                    "message": "Test",
                    "date": future,
                    "time": "09:00",
                    "timezone": "Not/A/Timezone",
                },
            )
        assert "invalid timezone" in str(exc_info.value).lower()


class TestScheduleWithDelay:
    async def test_success_with_delay_days(self, client, mock_qstash, env_vars):
        result = await client.call_tool(
            "schedule_notification",
            {"message": "Follow up", "delay": "3d"},
        )
        result_str = str(result)
        assert "test-message-id-123" in result_str

    async def test_success_with_delay_combined(self, client, mock_qstash, env_vars):
        result = await client.call_tool(
            "schedule_notification",
            {"message": "Check progress", "delay": "1d10h30m"},
        )
        result_str = str(result)
        assert "test-message-id-123" in result_str

    async def test_success_with_delay_seconds(self, client, mock_qstash, env_vars):
        result = await client.call_tool(
            "schedule_notification",
            {"message": "Quick reminder", "delay": "50s"},
        )
        result_str = str(result)
        assert "test-message-id-123" in result_str


class TestValidationErrors:
    async def test_no_scheduling_params(self, client, mock_qstash, env_vars):
        with pytest.raises(ToolError) as exc_info:
            await client.call_tool(
                "schedule_notification",
                {"message": "Test"},
            )
        assert "no scheduling" in str(exc_info.value).lower()

    async def test_conflicting_datetime_and_delay(self, client, mock_qstash, env_vars):
        future_dt = future_datetime_iso()
        with pytest.raises(ToolError) as exc_info:
            await client.call_tool(
                "schedule_notification",
                {"message": "Test", "datetime": future_dt, "delay": "3d"},
            )
        assert "multiple" in str(exc_info.value).lower()

    async def test_conflicting_separate_and_delay(self, client, mock_qstash, env_vars):
        future = future_date()
        with pytest.raises(ToolError) as exc_info:
            await client.call_tool(
                "schedule_notification",
                {
                    "message": "Test",
                    "date": future,
                    "time": "09:00",
                    "timezone": "UTC",
                    "delay": "3d",
                },
            )
        assert "multiple" in str(exc_info.value).lower()
