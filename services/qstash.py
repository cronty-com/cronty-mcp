import os

from qstash import QStash


def schedule_message(
    message: str,
    not_before: int | None = None,
    delay: str | None = None,
) -> str:
    """Schedule a message to be sent to NTFY via QStash.

    Args:
        message: The notification text to send.
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
    ntfy_topic = os.environ["NTFY_TOPIC"]
    url = f"https://ntfy.sh/{ntfy_topic}"

    kwargs: dict = {
        "url": url,
        "body": message,
    }

    if not_before is not None:
        kwargs["not_before"] = not_before
    else:
        kwargs["delay"] = delay

    response = client.message.publish_json(**kwargs)

    return response.message_id


def create_schedule(
    message: str,
    cron: str,
    label: str | None = None,
) -> str:
    """Create a recurring schedule to send messages to NTFY via QStash.

    Args:
        message: The notification text to send.
        cron: Cron expression with CRON_TZ prefix.
        label: Optional label for filtering logs in Upstash dashboard.

    Returns:
        The QStash schedule ID.
    """
    client = QStash(token=os.environ["QSTASH_TOKEN"])
    ntfy_topic = os.environ["NTFY_TOPIC"]
    destination = f"https://ntfy.sh/{ntfy_topic}"

    kwargs: dict = {
        "destination": destination,
        "cron": cron,
        "body": message,
    }

    if label is not None:
        kwargs["label"] = label

    schedule_id = client.schedule.create(**kwargs)

    return schedule_id
