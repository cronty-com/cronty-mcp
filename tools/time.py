from datetime import UTC, datetime


def get_current_time() -> dict:
    """Get the current date and time in UTC.

    Returns the current UTC timestamp in ISO 8601 format,
    useful for scheduling notifications or including timestamps in messages.
    """
    now = datetime.now(UTC)
    return {
        "utc": now.isoformat(),
        "date": now.strftime("%Y-%m-%d"),
        "time": now.strftime("%H:%M"),
        "timezone": "UTC",
    }
