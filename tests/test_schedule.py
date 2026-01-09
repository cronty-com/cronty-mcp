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
        mock_client.message.publish.return_value = mock_response
        mock_class.return_value = mock_client
        yield mock_client


@pytest.fixture
def env_vars(monkeypatch):
    monkeypatch.setenv("QSTASH_TOKEN", "test-token")


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
            {
                "message": "Call mom",
                "notification_topic": "test-topic",
                "datetime": future_dt,
            },
        )
        result_str = str(result)
        assert "test-message-id-123" in result_str
        assert "scheduled" in result_str.lower()

    async def test_reject_past_datetime(self, client, mock_qstash, env_vars):
        past_dt = past_datetime_iso()
        with pytest.raises(ToolError) as exc_info:
            await client.call_tool(
                "schedule_notification",
                {
                    "message": "Too late",
                    "notification_topic": "test-topic",
                    "datetime": past_dt,
                },
            )
        assert "future" in str(exc_info.value).lower()

    async def test_invalid_datetime_format(self, client, mock_qstash, env_vars):
        with pytest.raises(ToolError) as exc_info:
            await client.call_tool(
                "schedule_notification",
                {
                    "message": "Test",
                    "notification_topic": "test-topic",
                    "datetime": "not-a-datetime",
                },
            )
        assert "invalid" in str(exc_info.value).lower()

    async def test_datetime_without_timezone(self, client, mock_qstash, env_vars):
        with pytest.raises(ToolError) as exc_info:
            await client.call_tool(
                "schedule_notification",
                {
                    "message": "Test",
                    "notification_topic": "test-topic",
                    "datetime": "2025-12-31T09:00:00",
                },
            )
        assert "timezone" in str(exc_info.value).lower()


class TestScheduleWithSeparateParams:
    async def test_success_with_date_time_timezone(self, client, mock_qstash, env_vars):
        future = future_date()
        result = await client.call_tool(
            "schedule_notification",
            {
                "message": "Team standup",
                "notification_topic": "test-topic",
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
                {
                    "message": "Test",
                    "notification_topic": "test-topic",
                    "date": future,
                    "time": "09:00",
                },
            )
        assert "timezone" in str(exc_info.value).lower()

    async def test_missing_time(self, client, mock_qstash, env_vars):
        future = future_date()
        with pytest.raises(ToolError) as exc_info:
            await client.call_tool(
                "schedule_notification",
                {
                    "message": "Test",
                    "notification_topic": "test-topic",
                    "date": future,
                    "timezone": "Europe/Warsaw",
                },
            )
        assert "time" in str(exc_info.value).lower()

    async def test_invalid_timezone(self, client, mock_qstash, env_vars):
        future = future_date()
        with pytest.raises(ToolError) as exc_info:
            await client.call_tool(
                "schedule_notification",
                {
                    "message": "Test",
                    "notification_topic": "test-topic",
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
            {"message": "Follow up", "notification_topic": "test-topic", "delay": "3d"},
        )
        result_str = str(result)
        assert "test-message-id-123" in result_str

    async def test_success_with_delay_combined(self, client, mock_qstash, env_vars):
        result = await client.call_tool(
            "schedule_notification",
            {
                "message": "Check progress",
                "notification_topic": "test-topic",
                "delay": "1d10h30m",
            },
        )
        result_str = str(result)
        assert "test-message-id-123" in result_str

    async def test_success_with_delay_seconds(self, client, mock_qstash, env_vars):
        result = await client.call_tool(
            "schedule_notification",
            {
                "message": "Quick reminder",
                "notification_topic": "test-topic",
                "delay": "50s",
            },
        )
        result_str = str(result)
        assert "test-message-id-123" in result_str


class TestValidationErrors:
    async def test_no_scheduling_params(self, client, mock_qstash, env_vars):
        with pytest.raises(ToolError) as exc_info:
            await client.call_tool(
                "schedule_notification",
                {"message": "Test", "notification_topic": "test-topic"},
            )
        assert "no scheduling" in str(exc_info.value).lower()

    async def test_conflicting_datetime_and_delay(self, client, mock_qstash, env_vars):
        future_dt = future_datetime_iso()
        with pytest.raises(ToolError) as exc_info:
            await client.call_tool(
                "schedule_notification",
                {
                    "message": "Test",
                    "notification_topic": "test-topic",
                    "datetime": future_dt,
                    "delay": "3d",
                },
            )
        assert "multiple" in str(exc_info.value).lower()

    async def test_conflicting_separate_and_delay(self, client, mock_qstash, env_vars):
        future = future_date()
        with pytest.raises(ToolError) as exc_info:
            await client.call_tool(
                "schedule_notification",
                {
                    "message": "Test",
                    "notification_topic": "test-topic",
                    "date": future,
                    "time": "09:00",
                    "timezone": "UTC",
                    "delay": "3d",
                },
            )
        assert "multiple" in str(exc_info.value).lower()


class TestNotificationTopicValidation:
    async def test_schedule_notification_invalid_topic_uppercase(
        self, client, mock_qstash, env_vars
    ):
        with pytest.raises(ToolError) as exc_info:
            await client.call_tool(
                "schedule_notification",
                {"message": "Test", "notification_topic": "My-Topic", "delay": "1h"},
            )
        assert "notification_topic" in str(exc_info.value)
        assert "pattern" in str(exc_info.value).lower()

    async def test_schedule_notification_invalid_topic_special_chars(
        self, client, mock_qstash, env_vars
    ):
        with pytest.raises(ToolError) as exc_info:
            await client.call_tool(
                "schedule_notification",
                {"message": "Test", "notification_topic": "my_topic!", "delay": "1h"},
            )
        assert "notification_topic" in str(exc_info.value)
        assert "pattern" in str(exc_info.value).lower()

    async def test_schedule_cron_invalid_topic_uppercase(
        self, client, mock_qstash, env_vars
    ):
        with pytest.raises(ToolError) as exc_info:
            await client.call_tool(
                "schedule_cron_notification",
                {
                    "message": "Test",
                    "notification_topic": "My-Topic",
                    "cron": "0 9 * * 1",
                    "timezone": "UTC",
                },
            )
        assert "notification_topic" in str(exc_info.value)
        assert "pattern" in str(exc_info.value).lower()

    async def test_schedule_cron_invalid_topic_leading_dash(
        self, client, mock_qstash, env_vars
    ):
        with pytest.raises(ToolError) as exc_info:
            await client.call_tool(
                "schedule_cron_notification",
                {
                    "message": "Test",
                    "notification_topic": "-my-topic",
                    "cron": "0 9 * * 1",
                    "timezone": "UTC",
                },
            )
        assert "notification_topic" in str(exc_info.value)
        assert "pattern" in str(exc_info.value).lower()


@pytest.fixture
def mock_qstash_schedule():
    with patch("services.qstash.QStash") as mock_class:
        mock_client = MagicMock()
        mock_client.schedule.create.return_value = "test-schedule-id-456"
        mock_class.return_value = mock_client
        yield mock_client


class TestScheduleCronNotification:
    async def test_success_with_cron_and_timezone(
        self, client, mock_qstash_schedule, env_vars
    ):
        result = await client.call_tool(
            "schedule_cron_notification",
            {
                "message": "Submit your timesheet",
                "notification_topic": "test-topic",
                "cron": "0 9 * * 1",
                "timezone": "Europe/Warsaw",
            },
        )
        result_str = str(result)
        assert "test-schedule-id-456" in result_str
        assert "CRON_TZ=Europe/Warsaw 0 9 * * 1" in result_str

    async def test_success_with_weekday_cron(
        self, client, mock_qstash_schedule, env_vars
    ):
        result = await client.call_tool(
            "schedule_cron_notification",
            {
                "message": "Daily standup reminder",
                "notification_topic": "test-topic",
                "cron": "30 8 * * 1-5",
                "timezone": "America/New_York",
            },
        )
        result_str = str(result)
        assert "test-schedule-id-456" in result_str
        assert "CRON_TZ=America/New_York 30 8 * * 1-5" in result_str

    async def test_success_with_optional_label(
        self, client, mock_qstash_schedule, env_vars
    ):
        result = await client.call_tool(
            "schedule_cron_notification",
            {
                "message": "Weekly report",
                "notification_topic": "test-topic",
                "cron": "0 9 * * 1",
                "timezone": "UTC",
                "label": "weekly-report",
            },
        )
        result_str = str(result)
        assert "test-schedule-id-456" in result_str
        mock_qstash_schedule.schedule.create.assert_called_once()
        call_kwargs = mock_qstash_schedule.schedule.create.call_args.kwargs
        assert call_kwargs["label"] == "weekly-report"

    async def test_invalid_cron_too_few_fields(
        self, client, mock_qstash_schedule, env_vars
    ):
        with pytest.raises(ToolError) as exc_info:
            await client.call_tool(
                "schedule_cron_notification",
                {
                    "message": "Test",
                    "notification_topic": "test-topic",
                    "cron": "* * *",
                    "timezone": "Europe/Warsaw",
                },
            )
        assert "5 fields" in str(exc_info.value)

    async def test_invalid_cron_too_many_fields(
        self, client, mock_qstash_schedule, env_vars
    ):
        with pytest.raises(ToolError) as exc_info:
            await client.call_tool(
                "schedule_cron_notification",
                {
                    "message": "Test",
                    "notification_topic": "test-topic",
                    "cron": "0 9 * * 1 2024",
                    "timezone": "Europe/Warsaw",
                },
            )
        assert "5 fields" in str(exc_info.value)

    async def test_invalid_timezone(self, client, mock_qstash_schedule, env_vars):
        with pytest.raises(ToolError) as exc_info:
            await client.call_tool(
                "schedule_cron_notification",
                {
                    "message": "Test",
                    "notification_topic": "test-topic",
                    "cron": "0 9 * * 1",
                    "timezone": "Invalid/Zone",
                },
            )
        assert "invalid timezone" in str(exc_info.value).lower()

    async def test_invalid_label_with_spaces(
        self, client, mock_qstash_schedule, env_vars
    ):
        with pytest.raises(ToolError) as exc_info:
            await client.call_tool(
                "schedule_cron_notification",
                {
                    "message": "Test",
                    "notification_topic": "test-topic",
                    "cron": "0 9 * * 1",
                    "timezone": "Europe/Warsaw",
                    "label": "my label with spaces",
                },
            )
        assert "invalid label" in str(exc_info.value).lower()
        assert "alphanumeric" in str(exc_info.value).lower()

    async def test_invalid_label_with_special_chars(
        self, client, mock_qstash_schedule, env_vars
    ):
        with pytest.raises(ToolError) as exc_info:
            await client.call_tool(
                "schedule_cron_notification",
                {
                    "message": "Test",
                    "notification_topic": "test-topic",
                    "cron": "0 9 * * 1",
                    "timezone": "Europe/Warsaw",
                    "label": "reminder (daily)",
                },
            )
        assert "invalid label" in str(exc_info.value).lower()


@pytest.fixture
def mock_qstash_list():
    with patch("services.qstash.QStash") as mock_class:
        mock_client = MagicMock()
        mock_client.schedule.list.return_value = []
        mock_class.return_value = mock_client
        yield mock_client


def create_mock_schedule(
    schedule_id: str,
    destination: str,
    cron: str,
    body: str | None = None,
    label: str | None = None,
    next_schedule_time: int | None = None,
    last_schedule_time: int | None = None,
) -> MagicMock:
    mock = MagicMock()
    mock.schedule_id = schedule_id
    mock.destination = destination
    mock.cron = cron
    mock.body = body
    mock.label = label
    mock.next_schedule_time = next_schedule_time
    mock.last_schedule_time = last_schedule_time
    return mock


class TestListScheduledNotifications:
    async def test_returns_ntfy_schedules(self, client, mock_qstash_list, env_vars):
        mock_schedule = create_mock_schedule(
            schedule_id="sched_123",
            destination="https://ntfy.sh/my-topic",
            cron="CRON_TZ=Europe/Warsaw 0 9 * * 1",
            body="Test message",
            label="test-label",
            next_schedule_time=1736330400000,
            last_schedule_time=1735725600000,
        )
        mock_qstash_list.schedule.list.return_value = [mock_schedule]

        result = await client.call_tool("list_scheduled_notifications", {})

        assert result.data["count"] == 1
        schedule = result.data["schedules"][0]
        assert schedule["schedule_id"] == "sched_123"
        assert schedule["cron_expression"] == "0 9 * * 1"
        assert schedule["timezone"] == "Europe/Warsaw"
        assert schedule["notification_topic"] == "my-topic"
        assert schedule["notification_body"] == "Test message"
        assert schedule["label"] == "test-label"

    async def test_filters_by_topic(self, client, mock_qstash_list, env_vars):
        mock_schedule_a = create_mock_schedule(
            schedule_id="sched_1",
            destination="https://ntfy.sh/topic-a",
            cron="0 9 * * 1",
        )
        mock_schedule_b = create_mock_schedule(
            schedule_id="sched_2",
            destination="https://ntfy.sh/topic-b",
            cron="0 10 * * 1",
        )
        mock_qstash_list.schedule.list.return_value = [mock_schedule_a, mock_schedule_b]

        result = await client.call_tool(
            "list_scheduled_notifications",
            {"notification_topic": "topic-a"},
        )

        assert result.data["count"] == 1
        assert result.data["schedules"][0]["notification_topic"] == "topic-a"

    async def test_returns_empty_list_when_no_matches(
        self, client, mock_qstash_list, env_vars
    ):
        mock_qstash_list.schedule.list.return_value = []

        result = await client.call_tool("list_scheduled_notifications", {})

        assert result.data["count"] == 0
        assert result.data["schedules"] == []

    async def test_handles_null_body(self, client, mock_qstash_list, env_vars):
        mock_schedule = create_mock_schedule(
            schedule_id="sched_123",
            destination="https://ntfy.sh/my-topic",
            cron="0 9 * * 1",
            body=None,
        )
        mock_qstash_list.schedule.list.return_value = [mock_schedule]

        result = await client.call_tool("list_scheduled_notifications", {})

        assert result.data["count"] == 1
        assert result.data["schedules"][0]["notification_body"] is None


class TestListScheduledNotificationsFiltering:
    async def test_excludes_non_ntfy_destinations(
        self, client, mock_qstash_list, env_vars
    ):
        mock_ntfy = create_mock_schedule(
            schedule_id="sched_ntfy",
            destination="https://ntfy.sh/my-topic",
            cron="0 9 * * 1",
            body="NTFY message",
        )
        mock_webhook = create_mock_schedule(
            schedule_id="sched_webhook",
            destination="https://example.com/webhook",
            cron="0 10 * * 1",
        )
        mock_other = create_mock_schedule(
            schedule_id="sched_other",
            destination="https://other-service.io/notify",
            cron="0 11 * * 1",
        )
        mock_qstash_list.schedule.list.return_value = [
            mock_ntfy,
            mock_webhook,
            mock_other,
        ]

        result = await client.call_tool("list_scheduled_notifications", {})

        assert result.data["count"] == 1
        assert result.data["schedules"][0]["schedule_id"] == "sched_ntfy"

    async def test_excludes_malformed_destinations(
        self, client, mock_qstash_list, env_vars
    ):
        mock_valid = create_mock_schedule(
            schedule_id="sched_valid",
            destination="https://ntfy.sh/valid-topic",
            cron="0 9 * * 1",
            body="Valid",
        )
        mock_malformed = create_mock_schedule(
            schedule_id="sched_malformed",
            destination="not-a-valid-url",
            cron="0 10 * * 1",
        )
        mock_qstash_list.schedule.list.return_value = [mock_valid, mock_malformed]

        result = await client.call_tool("list_scheduled_notifications", {})

        assert result.data["count"] == 1
        assert result.data["schedules"][0]["schedule_id"] == "sched_valid"


class TestParseCron:
    def test_with_timezone(self):
        from services.qstash import _parse_cron

        cron_expression, timezone = _parse_cron("CRON_TZ=Europe/Warsaw 0 9 * * 1")
        assert cron_expression == "0 9 * * 1"
        assert timezone == "Europe/Warsaw"

    def test_without_timezone(self):
        from services.qstash import _parse_cron

        cron_expression, timezone = _parse_cron("0 9 * * 1")
        assert cron_expression == "0 9 * * 1"
        assert timezone == "UTC"

    def test_with_utc_timezone(self):
        from services.qstash import _parse_cron

        cron_expression, timezone = _parse_cron("CRON_TZ=UTC 30 8 * * 1-5")
        assert cron_expression == "30 8 * * 1-5"
        assert timezone == "UTC"

    def test_with_complex_expression(self):
        from services.qstash import _parse_cron

        cron_expression, timezone = _parse_cron("CRON_TZ=America/New_York 0 0 1 * *")
        assert cron_expression == "0 0 1 * *"
        assert timezone == "America/New_York"


class TestFormatTimestamp:
    def test_valid_timestamp_milliseconds(self):
        from services.qstash import _format_timestamp

        result = _format_timestamp(1736330400000)
        assert "2025-01-08" in result
        assert "+00:00" in result

    def test_none_returns_none(self):
        from services.qstash import _format_timestamp

        result = _format_timestamp(None)
        assert result is None

    def test_zero_timestamp(self):
        from services.qstash import _format_timestamp

        result = _format_timestamp(0)
        assert result == "1970-01-01T00:00:00+00:00"


@pytest.fixture
def mock_qstash_delete():
    with patch("services.qstash.QStash") as mock_class:
        mock_client = MagicMock()
        mock_client.schedule.get.return_value = MagicMock()
        mock_client.schedule.delete.return_value = None
        mock_class.return_value = mock_client
        yield mock_client


class TestDeleteSchedule:
    async def test_success_delete_schedule(self, client, mock_qstash_delete, env_vars):
        result = await client.call_tool(
            "delete_schedule",
            {"schedule_id": "scd_abc123"},
        )
        assert result.data["success"] is True
        assert result.data["schedule_id"] == "scd_abc123"
        assert "deleted" in result.data["confirmation"].lower()
        mock_qstash_delete.schedule.get.assert_called_once_with("scd_abc123")
        mock_qstash_delete.schedule.delete.assert_called_once_with("scd_abc123")

    async def test_delete_nonexistent_schedule(self, client, env_vars):
        with patch("services.qstash.QStash") as mock_class:
            mock_client = MagicMock()
            mock_client.schedule.get.side_effect = Exception("Schedule not found")
            mock_class.return_value = mock_client

            result = await client.call_tool(
                "delete_schedule",
                {"schedule_id": "scd_nonexistent"},
            )
            assert result.data["success"] is False
            assert result.data["schedule_id"] == "scd_nonexistent"
            assert "not found" in result.data["error"].lower()

    async def test_delete_with_404_error(self, client, env_vars):
        with patch("services.qstash.QStash") as mock_class:
            mock_client = MagicMock()
            mock_client.schedule.get.side_effect = Exception("404 Not Found")
            mock_class.return_value = mock_client

            result = await client.call_tool(
                "delete_schedule",
                {"schedule_id": "scd_invalid"},
            )
            assert result.data["success"] is False
            assert "not found" in result.data["error"].lower()

    async def test_delete_with_other_error(self, client, env_vars):
        with patch("services.qstash.QStash") as mock_class:
            mock_client = MagicMock()
            mock_client.schedule.get.return_value = MagicMock()
            mock_client.schedule.delete.side_effect = Exception("Connection timeout")
            mock_class.return_value = mock_client

            result = await client.call_tool(
                "delete_schedule",
                {"schedule_id": "scd_abc123"},
            )
            assert result.data["success"] is False
            assert "failed to delete" in result.data["error"].lower()
