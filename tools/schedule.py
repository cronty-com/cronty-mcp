import re
from datetime import UTC, datetime
from typing import Annotated
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from fastmcp.exceptions import ToolError
from pydantic import Field

from services.qstash import (
    create_schedule,
    list_schedules,
    schedule_message,
)
from services.qstash import (
    delete_schedule as qstash_delete,
)
from services.qstash import (
    pause_schedule as qstash_pause,
)
from services.qstash import (
    resume_schedule as qstash_resume,
)

DELAY_PATTERN = r"^(\d+d)?(\d+h)?(\d+m)?(\d+s)?$"
TIMEZONE_EXAMPLES = (
    "Europe/Warsaw, Europe/London, America/New_York, America/Los_Angeles, "
    "Asia/Tokyo, Asia/Shanghai, Australia/Sydney, UTC"
)
TOPIC_PATTERN = r"^[a-z0-9]+(-[a-z0-9]+)*$"
TOPIC_DESCRIPTION = (
    "The notification topic to send to. "
    "Format: lowercase alphanumeric with dashes "
    "(e.g., 'my-alerts', 'user-123-notifications')"
)


def schedule_notification(
    message: Annotated[str, Field(description="The notification text to send")],
    notification_topic: Annotated[
        str,
        Field(description=TOPIC_DESCRIPTION, pattern=TOPIC_PATTERN),
    ],
    datetime_iso: Annotated[
        str | None,
        Field(
            description="ISO 8601 datetime with timezone",
            alias="datetime",
        ),
    ] = None,
    date: Annotated[
        str | None,
        Field(description="Date in YYYY-MM-DD format", pattern=r"^\d{4}-\d{2}-\d{2}$"),
    ] = None,
    time: Annotated[
        str | None,
        Field(description="Time in HH:MM format", pattern=r"^\d{2}:\d{2}$"),
    ] = None,
    timezone: Annotated[
        str | None,
        Field(
            description=(
                "IANA timezone (required with date+time). "
                "Check the user's system timezone first. "
                "If unavailable, ask the user for their timezone. "
                f"Examples: {TIMEZONE_EXAMPLES}"
            )
        ),
    ] = None,
    delay: Annotated[
        str | None,
        Field(description='QStash delay format (e.g., "1d", "2h30m", "1d10h30m")'),
    ] = None,
) -> dict:
    """Schedule a one-off notification for a future time.

    Supports three input modes (use only one):
    1. datetime: ISO 8601 format (e.g., 2025-01-15T09:00:00+01:00)
    2. date + time + timezone: Separate parameters
    3. delay: QStash delay format (e.g., 1d, 2h30m, 1d10h30m50s)
    """
    mode = _determine_scheduling_mode(datetime_iso, date, time, timezone, delay)

    if mode == "datetime":
        not_before = _parse_iso_datetime(datetime_iso)
        scheduled_time = datetime_iso
        return _schedule_with_not_before(
            message, notification_topic, not_before, scheduled_time
        )

    elif mode == "separate":
        not_before, scheduled_time = _parse_separate_params(date, time, timezone)
        return _schedule_with_not_before(
            message, notification_topic, not_before, scheduled_time
        )

    else:
        return _schedule_with_delay(message, notification_topic, delay)


def _determine_scheduling_mode(
    datetime_iso: str | None,
    date: str | None,
    time: str | None,
    timezone: str | None,
    delay: str | None,
) -> str:
    has_datetime = datetime_iso is not None
    has_separate = date is not None or time is not None or timezone is not None
    has_delay = delay is not None

    modes_used = sum([has_datetime, has_separate, has_delay])

    if modes_used == 0:
        raise ToolError(
            "No scheduling parameters provided. Use one of: "
            "datetime (ISO 8601), date+time+timezone, or delay"
        )

    if modes_used > 1:
        raise ToolError(
            "Multiple scheduling modes provided. Use only one of: "
            "datetime (ISO 8601), date+time+timezone, or delay"
        )

    if has_datetime:
        return "datetime"
    elif has_delay:
        return "delay"
    else:
        if date is None or time is None or timezone is None:
            missing = []
            if date is None:
                missing.append("date")
            if time is None:
                missing.append("time")
            if timezone is None:
                missing.append("timezone")
            raise ToolError(
                f"Missing required parameters: {', '.join(missing)}. "
                "date, time, and timezone are all required."
            )
        return "separate"


def _parse_iso_datetime(datetime_str: str) -> int:
    try:
        dt = datetime.fromisoformat(datetime_str)
    except ValueError as e:
        raise ToolError(f"Invalid ISO 8601 datetime format: {e}")

    if dt.tzinfo is None:
        raise ToolError(
            "ISO 8601 datetime must include timezone. "
            "Example: 2025-01-15T09:00:00+01:00 or 2025-01-15T09:00:00Z"
        )

    now = datetime.now(UTC)
    if dt <= now:
        raise ToolError(
            f"Scheduled time must be in the future. "
            f"Provided: {datetime_str}, Current time (UTC): {now.isoformat()}"
        )

    return int(dt.timestamp())


def _parse_separate_params(date: str, time: str, timezone: str) -> tuple[int, str]:
    try:
        tz_info = ZoneInfo(timezone)
    except ZoneInfoNotFoundError:
        raise ToolError(
            f"Invalid timezone: {timezone}. "
            "Use IANA timezone format (e.g., Europe/Warsaw, America/New_York)"
        )

    try:
        dt = datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M")
        dt = dt.replace(tzinfo=tz_info)
    except ValueError as e:
        raise ToolError(f"Invalid date/time format: {e}")

    now = datetime.now(UTC)
    if dt <= now:
        raise ToolError(
            f"Scheduled time must be in the future. "
            f"Provided: {date} {time} {timezone}, Current time (UTC): {now.isoformat()}"
        )

    scheduled_time = f"{date} {time} {timezone}"
    return int(dt.timestamp()), scheduled_time


def _validate_delay_format(delay: str) -> None:
    if not delay or not re.match(DELAY_PATTERN, delay):
        raise ToolError(
            f"Invalid delay format: {delay}. "
            'Valid examples: "1d", "2h30m", "1d10h30m50s". '
            "Units must be in order: d, h, m, s"
        )
    match = re.match(DELAY_PATTERN, delay)
    if match and not any(match.groups()):
        raise ToolError(
            f"Invalid delay format: {delay}. "
            "At least one time unit (d, h, m, s) is required. "
            'Valid examples: "1d", "2h30m", "1d10h30m50s"'
        )


def _schedule_with_not_before(
    message: str, topic: str, not_before: int, scheduled_time: str
) -> dict:
    message_id = schedule_message(message, topic, not_before=not_before)
    return {
        "success": True,
        "message_id": message_id,
        "scheduled_time": scheduled_time,
        "confirmation": f"Notification scheduled for {scheduled_time}",
    }


def _schedule_with_delay(message: str, topic: str, delay: str) -> dict:
    _validate_delay_format(delay)
    message_id = schedule_message(message, topic, delay=delay)
    return {
        "success": True,
        "message_id": message_id,
        "delay": delay,
        "confirmation": f"Notification scheduled with delay: {delay}",
    }


def schedule_cron_notification(
    message: Annotated[str, Field(description="The notification text to send")],
    notification_topic: Annotated[
        str,
        Field(description=TOPIC_DESCRIPTION, pattern=TOPIC_PATTERN),
    ],
    cron: Annotated[
        str,
        Field(
            description=(
                "Standard 5-field cron expression. "
                "Fields: minute hour day-of-month month day-of-week. "
                "Examples: '0 9 * * 1' (Mondays 9am), "
                "'30 8 * * 1-5' (weekdays 8:30am), '0 0 1 * *' (monthly)"
            )
        ),
    ],
    timezone: Annotated[
        str,
        Field(
            description=(
                "IANA timezone for the cron schedule. "
                "Check the user's system timezone first. "
                "If unavailable, ask the user for their timezone. "
                f"Examples: {TIMEZONE_EXAMPLES}"
            )
        ),
    ],
    label: Annotated[
        str | None,
        Field(
            description=(
                "Optional label for identifying this schedule in the Upstash "
                "dashboard logs. Only alphanumeric, hyphen, underscore, or period "
                "allowed. Examples: 'daily-standup', 'weekly_report', 'reminder.v1'"
            )
        ),
    ] = None,
) -> dict:
    """Schedule a recurring notification using cron syntax.

    Creates a persistent schedule that fires according to the cron pattern.
    The schedule continues indefinitely until deleted via the Upstash panel.

    The agent should determine the user's timezone by:
    1. Checking system/environment timezone information
    2. If unavailable, asking the user explicitly
    """
    _validate_cron(cron)
    _validate_timezone(timezone)
    if label is not None:
        _validate_label(label)

    cron_with_tz = f"CRON_TZ={timezone} {cron}"
    schedule_id = create_schedule(
        message, notification_topic, cron_with_tz, label=label
    )

    return {
        "success": True,
        "schedule_id": schedule_id,
        "cron": cron_with_tz,
        "confirmation": f"Cron schedule created: {cron_with_tz}",
    }


def _validate_cron(cron: str) -> None:
    fields = cron.strip().split()
    if len(fields) != 5:
        raise ToolError(
            f"Invalid cron expression: '{cron}'. "
            "Cron requires exactly 5 fields: minute hour day-of-month month "
            "day-of-week. Examples: '0 9 * * 1', '30 8 * * 1-5', '0 0 1 * *'"
        )


def _validate_timezone(timezone: str) -> None:
    try:
        ZoneInfo(timezone)
    except ZoneInfoNotFoundError:
        raise ToolError(
            f"Invalid timezone: '{timezone}'. "
            f"Use IANA timezone format. Examples: {TIMEZONE_EXAMPLES}"
        )


def _validate_label(label: str) -> None:
    if not re.match(r"^[a-zA-Z0-9._-]+$", label):
        raise ToolError(
            f"Invalid label: '{label}'. "
            "Only alphanumeric characters, hyphens, underscores, and periods "
            "are allowed. Examples: 'daily-standup', 'weekly_report', 'reminder.v1'"
        )


def list_scheduled_notifications(
    notification_topic: Annotated[
        str | None,
        Field(
            default=None,
            description=(
                "Optional: filter to show only schedules for this notification topic. "
                "If not provided, returns all scheduled notifications. "
                "Format: lowercase alphanumeric with dashes (e.g., 'my-alerts')"
            ),
            pattern=TOPIC_PATTERN,
        ),
    ] = None,
) -> dict:
    """List scheduled recurring notifications.

    Returns all recurring cron notification schedules.
    Optionally filter by a specific notification topic.

    Note: One-off scheduled notifications (created with schedule_notification)
    are not included as they are pending messages, not recurring schedules.
    """
    schedules = list_schedules(topic=notification_topic)
    return {
        "schedules": schedules,
        "count": len(schedules),
    }


def delete_schedule(
    schedule_id: Annotated[
        str,
        Field(
            description=(
                "The schedule ID to delete. "
                "This ID is returned when creating a cron schedule."
            )
        ),
    ],
) -> dict:
    """Delete a scheduled notification by its ID.

    Permanently removes a cron schedule. The schedule will stop firing
    and cannot be recovered. Use the schedule_id returned from
    schedule_cron_notification.
    """
    result = qstash_delete(schedule_id)

    if result.is_ok:
        return {
            "success": True,
            "schedule_id": schedule_id,
            "confirmation": f"Schedule {schedule_id} deleted successfully",
        }

    if result.code == "not_found":
        return {
            "success": False,
            "schedule_id": schedule_id,
            "error": (
                f"Schedule not found: {schedule_id}. "
                "It may have already been deleted or the ID is incorrect."
            ),
        }

    return {
        "success": False,
        "schedule_id": schedule_id,
        "error": f"Failed to delete schedule: {result.message}",
    }


def pause_schedule(
    schedule_id: Annotated[
        str,
        Field(
            description=(
                "The schedule ID to pause. "
                "This ID is returned when creating a cron schedule."
            )
        ),
    ],
) -> dict:
    """Pause a scheduled notification.

    Temporarily stops a cron schedule from firing. The schedule configuration
    is preserved and can be resumed later. Use the schedule_id returned from
    schedule_cron_notification.
    """
    result = qstash_pause(schedule_id)

    if result.is_ok:
        return {
            "success": True,
            "schedule_id": schedule_id,
            "paused": True,
            "confirmation": f"Schedule {schedule_id} paused successfully",
        }

    if result.code == "not_found":
        return {
            "success": False,
            "schedule_id": schedule_id,
            "error": (
                f"Schedule not found: {schedule_id}. "
                "It may have been deleted or the ID is incorrect."
            ),
        }

    return {
        "success": False,
        "schedule_id": schedule_id,
        "error": f"Failed to pause schedule: {result.message}",
    }


def resume_schedule(
    schedule_id: Annotated[
        str,
        Field(
            description=(
                "The schedule ID to resume. "
                "This ID is returned when creating a cron schedule."
            )
        ),
    ],
) -> dict:
    """Resume a paused scheduled notification.

    Reactivates a paused cron schedule. The schedule will resume firing
    at its next scheduled time. Use the schedule_id returned from
    schedule_cron_notification.
    """
    result = qstash_resume(schedule_id)

    if result.is_ok:
        return {
            "success": True,
            "schedule_id": schedule_id,
            "paused": False,
            "confirmation": f"Schedule {schedule_id} resumed successfully",
        }

    if result.code == "not_found":
        return {
            "success": False,
            "schedule_id": schedule_id,
            "error": (
                f"Schedule not found: {schedule_id}. "
                "It may have been deleted or the ID is incorrect."
            ),
        }

    return {
        "success": False,
        "schedule_id": schedule_id,
        "error": f"Failed to resume schedule: {result.message}",
    }
