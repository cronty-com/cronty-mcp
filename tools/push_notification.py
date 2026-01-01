from typing import Annotated

import httpx
from fastmcp.exceptions import ToolError
from pydantic import Field

from services.ntfy import send_notification


async def send_push_notification(
    message: Annotated[str, Field(description="The notification body text")],
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
    attach: Annotated[
        str | None, Field(description="URL of file to attach")
    ] = None,
    filename: Annotated[
        str | None, Field(description="Filename for attachment")
    ] = None,
    actions: Annotated[
        list[dict] | None, Field(description="Action buttons (max 3)")
    ] = None,
) -> dict:
    """Send an immediate push notification.

    Sends a push notification for instant delivery (currently via NTFY.sh).
    Only a message is required; all other parameters are optional.
    """
    try:
        response = await send_notification(
            message=message,
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
        raise ToolError(f"Failed to connect to NTFY: {e}")
    except httpx.HTTPStatusError as e:
        raise ToolError(f"NTFY API error: {e.response.status_code} - {e.response.text}")
