import re
from datetime import UTC, datetime
from typing import Annotated
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from fastmcp.exceptions import ToolError
from pydantic import Field

from services.qstash import schedule_message

DELAY_PATTERN = r"^(\d+d)?(\d+h)?(\d+m)?(\d+s)?$"


def schedule_notification(
    message: Annotated[str, Field(description="The notification text to send")],
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
        Field(description="IANA timezone (e.g., Europe/Warsaw)"),
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
        return _schedule_with_not_before(message, not_before, scheduled_time)

    elif mode == "separate":
        not_before, scheduled_time = _parse_separate_params(date, time, timezone)
        return _schedule_with_not_before(message, not_before, scheduled_time)

    else:
        return _schedule_with_delay(message, delay)


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


def _parse_separate_params(
    date: str, time: str, timezone: str
) -> tuple[int, str]:
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
    message: str, not_before: int, scheduled_time: str
) -> dict:
    message_id = schedule_message(message, not_before=not_before)
    return {
        "success": True,
        "message_id": message_id,
        "scheduled_time": scheduled_time,
        "confirmation": f"Notification scheduled for {scheduled_time}",
    }


def _schedule_with_delay(message: str, delay: str) -> dict:
    _validate_delay_format(delay)
    message_id = schedule_message(message, delay=delay)
    return {
        "success": True,
        "message_id": message_id,
        "delay": delay,
        "confirmation": f"Notification scheduled with delay: {delay}",
    }
