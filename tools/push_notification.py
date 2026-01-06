from typing import Annotated

import httpx
from fastmcp.exceptions import ToolError
from pydantic import Field

from services.ntfy import send_notification

TOPIC_PATTERN = r"^[a-z0-9]+(-[a-z0-9]+)*$"
TOPIC_DESCRIPTION = (
    "The notification topic to send to. "
    "Format: lowercase alphanumeric with dashes "
    "(e.g., 'my-alerts', 'user-123-notifications')"
)


async def send_push_notification(
    message: Annotated[str, Field(description="The notification body text")],
    notification_topic: Annotated[
        str,
        Field(description=TOPIC_DESCRIPTION, pattern=TOPIC_PATTERN),
    ],
    title: Annotated[str | None, Field(description="Notification title")] = None,
    priority: Annotated[
        int | None,
        Field(description="Priority 1-5 (1=min, 3=default, 5=urgent)", ge=1, le=5),
    ] = None,
    tags: Annotated[
        list[str] | None, Field(description="List of tags/emoji shortcodes")
    ] = None,
    markdown: Annotated[
        bool | None, Field(description="Enable markdown formatting")
    ] = None,
    click: Annotated[
        str | None, Field(description="URL to open when notification is tapped")
    ] = None,
    icon: Annotated[
        str | None, Field(description="URL of custom notification icon")
    ] = None,
    attach: Annotated[str | None, Field(description="URL of file to attach")] = None,
    filename: Annotated[
        str | None, Field(description="Filename for attachment")
    ] = None,
    actions: Annotated[
        list[dict] | None, Field(description="Action buttons (max 3)")
    ] = None,
) -> dict:
    """Send an immediate push notification.

    Sends a push notification for instant delivery.
    Only a message is required; all other parameters are optional.
    """
    try:
        response = await send_notification(
            message=message,
            topic=notification_topic,
            title=title,
            priority=priority,
            tags=tags,
            markdown=markdown,
            click=click,
            icon=icon,
            attach=attach,
            filename=filename,
            actions=actions,
        )
        return {
            "success": True,
            "id": response.get("id"),
            "confirmation": "Push notification sent successfully",
        }
    except httpx.ConnectError as e:
        raise ToolError(f"Failed to connect to notification service: {e}")
    except httpx.HTTPStatusError as e:
        raise ToolError(
            f"Notification service error: {e.response.status_code} - {e.response.text}"
        )
