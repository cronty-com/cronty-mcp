import os

from qstash import QStash

from services.result import Err, Ok, Result


def schedule_message(
    message: str,
    topic: str,
    not_before: int | None = None,
    delay: str | None = None,
) -> str:
    """Schedule a message to be sent to NTFY via QStash.

    Args:
        message: The notification text to send.
        topic: The NTFY topic to send to.
        not_before: Unix timestamp in seconds (UTC) for absolute scheduling.
        delay: QStash delay format string (e.g., "1d", "2h30m") for relative scheduling.

    Returns:
        The QStash message ID.

    Raises:
        ValueError: If neither not_before nor delay is provided.
        Exception: If the QStash API call fails.
    """
    if not_before is None and delay is None:
        raise ValueError("Either not_before or delay must be provided")

    client = QStash(token=os.environ["QSTASH_TOKEN"])
    url = f"https://ntfy.sh/{topic}"

    kwargs: dict = {
        "url": url,
        "body": message,
    }

    if not_before is not None:
        kwargs["not_before"] = not_before
    else:
        kwargs["delay"] = delay

    response = client.message.publish(**kwargs)

    return response.message_id


def create_schedule(
    message: str,
    topic: str,
    cron: str,
    label: str | None = None,
) -> str:
    """Create a recurring schedule to send messages to NTFY via QStash.

    Args:
        message: The notification text to send.
        topic: The NTFY topic to send to.
        cron: Cron expression with CRON_TZ prefix.
        label: Optional label for filtering logs in Upstash dashboard.

    Returns:
        The QStash schedule ID.
    """
    client = QStash(token=os.environ["QSTASH_TOKEN"])
    destination = f"https://ntfy.sh/{topic}"

    kwargs: dict = {
        "destination": destination,
        "cron": cron,
        "body": message,
    }

    if label is not None:
        kwargs["label"] = label

    schedule_id = client.schedule.create(**kwargs)

    return schedule_id


def _parse_cron(cron: str) -> tuple[str, str]:
    if cron.startswith("CRON_TZ="):
        parts = cron.split(" ", 1)
        timezone = parts[0].replace("CRON_TZ=", "")
        cron_expression = parts[1] if len(parts) > 1 else ""
        return cron_expression, timezone
    return cron, "UTC"


def _format_timestamp(ts: int | None) -> str | None:
    if ts is None:
        return None
    from datetime import UTC, datetime

    ts_seconds = ts / 1000
    return datetime.fromtimestamp(ts_seconds, tz=UTC).isoformat()


def list_schedules(topic: str | None = None) -> list[dict]:
    client = QStash(token=os.environ["QSTASH_TOKEN"])
    schedules = client.schedule.list()

    results = []
    for schedule in schedules:
        if "ntfy.sh" not in schedule.destination:
            continue

        schedule_topic = schedule.destination.split("ntfy.sh/")[-1]

        if topic is not None and schedule_topic != topic:
            continue

        cron_expression, tz = _parse_cron(schedule.cron)

        results.append(
            {
                "schedule_id": schedule.schedule_id,
                "cron_expression": cron_expression,
                "timezone": tz,
                "notification_topic": schedule_topic,
                "label": schedule.label,
                "paused": schedule.paused,
                "next_occurrence": _format_timestamp(schedule.next_schedule_time),
                "last_occurrence": _format_timestamp(schedule.last_schedule_time),
                "notification_body": schedule.body,
            }
        )

    return results


def delete_schedule(schedule_id: str) -> Result[None]:
    """Delete a schedule.

    Args:
        schedule_id: The schedule ID to delete.

    Returns:
        Ok(None) on success, or Err with code and message on failure.
        Error codes: "not_found", "api_error"
    """
    client = QStash(token=os.environ["QSTASH_TOKEN"])

    try:
        client.schedule.get(schedule_id)
    except Exception as e:
        error_msg = str(e).lower()
        if "not found" in error_msg or "404" in error_msg:
            return Err("not_found")
        return Err("api_error", str(e))

    try:
        client.schedule.delete(schedule_id)
    except Exception as e:
        return Err("api_error", str(e))

    return Ok(None)


def pause_schedule(schedule_id: str) -> Result[bool]:
    """Pause a schedule.

    Args:
        schedule_id: The schedule ID to pause.

    Returns:
        Ok(True) on success, or Err with code and message on failure.
        Error codes: "not_found", "api_error"
    """
    client = QStash(token=os.environ["QSTASH_TOKEN"])

    try:
        client.schedule.get(schedule_id)
    except Exception as e:
        error_msg = str(e).lower()
        if "not found" in error_msg or "404" in error_msg:
            return Err("not_found")
        return Err("api_error", str(e))

    try:
        client.schedule.pause(schedule_id)
    except Exception as e:
        return Err("api_error", str(e))

    return Ok(True)


def resume_schedule(schedule_id: str) -> Result[bool]:
    """Resume a schedule.

    Args:
        schedule_id: The schedule ID to resume.

    Returns:
        Ok(False) on success, or Err with code and message on failure.
        Error codes: "not_found", "api_error"
    """
    client = QStash(token=os.environ["QSTASH_TOKEN"])

    try:
        client.schedule.get(schedule_id)
    except Exception as e:
        error_msg = str(e).lower()
        if "not found" in error_msg or "404" in error_msg:
            return Err("not_found")
        return Err("api_error", str(e))

    try:
        client.schedule.resume(schedule_id)
    except Exception as e:
        return Err("api_error", str(e))

    return Ok(False)
