import json

import httpx


async def send_notification(
    message: str,
    topic: str,
    title: str | None = None,
    priority: int | None = None,
    tags: list[str] | None = None,
    markdown: bool | None = None,
    click: str | None = None,
    icon: str | None = None,
    attach: str | None = None,
    filename: str | None = None,
    actions: list[dict] | None = None,
) -> dict:
    payload: dict = {"topic": topic, "message": message}

    if title is not None:
        payload["title"] = title
    if priority is not None:
        payload["priority"] = priority
    if tags is not None:
        payload["tags"] = tags
    if markdown is not None:
        payload["markdown"] = markdown
    if click is not None:
        payload["click"] = click
    if icon is not None:
        payload["icon"] = icon
    if attach is not None:
        payload["attach"] = attach
    if filename is not None:
        payload["filename"] = filename
    if actions is not None:
        payload["actions"] = actions

    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://ntfy.sh/",
            content=json.dumps(payload),
            headers={"Content-Type": "application/json"},
        )
        response.raise_for_status()
        return response.json()
