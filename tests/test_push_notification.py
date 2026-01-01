import json
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest
from fastmcp.client import Client
from fastmcp.exceptions import ToolError

from server import mcp


def get_payload_from_mock(mock_client) -> dict:
    call_args = mock_client.post.call_args
    content = call_args[1]["content"]
    return json.loads(content)


@pytest.fixture
async def client():
    async with Client(transport=mcp) as c:
        yield c


@pytest.fixture
def mock_ntfy():
    with patch("services.ntfy.httpx.AsyncClient") as mock_class:
        mock_client = AsyncMock()
        mock_response = MagicMock()
        mock_response.json.return_value = {"id": "test-notification-id"}
        mock_response.raise_for_status = MagicMock()
        mock_client.post.return_value = mock_response
        mock_client.__aenter__.return_value = mock_client
        mock_client.__aexit__.return_value = None
        mock_class.return_value = mock_client
        yield mock_client


@pytest.fixture
def env_vars(monkeypatch):
    monkeypatch.setenv("QSTASH_TOKEN", "test-token")
    monkeypatch.setenv("QSTASH_CURRENT_SIGNING_KEY", "current-key")
    monkeypatch.setenv("QSTASH_NEXT_SIGNING_KEY", "next-key")
    monkeypatch.setenv("NTFY_TOPIC", "test-topic")


class TestSendPushNotificationSuccess:
    async def test_simple_message_only(self, client, mock_ntfy, env_vars):
        result = await client.call_tool(
            "send_push_notification",
            {"message": "Build completed"},
        )
        result_str = str(result)
        assert "success" in result_str.lower()
        assert "test-notification-id" in result_str

    async def test_message_with_title(self, client, mock_ntfy, env_vars):
        result = await client.call_tool(
            "send_push_notification",
            {"message": "All tests passed", "title": "CI Pipeline"},
        )
        result_str = str(result)
        assert "success" in result_str.lower()

        payload = get_payload_from_mock(mock_ntfy)
        assert payload["title"] == "CI Pipeline"
        assert payload["message"] == "All tests passed"

    async def test_urgent_notification_with_priority(self, client, mock_ntfy, env_vars):
        result = await client.call_tool(
            "send_push_notification",
            {
                "message": "Server is unresponsive",
                "title": "Alert",
                "priority": 5,
                "tags": ["warning", "skull"],
            },
        )
        result_str = str(result)
        assert "success" in result_str.lower()

        payload = get_payload_from_mock(mock_ntfy)
        assert payload["priority"] == 5
        assert payload["tags"] == ["warning", "skull"]

    async def test_notification_with_click_action(self, client, mock_ntfy, env_vars):
        result = await client.call_tool(
            "send_push_notification",
            {
                "message": "New deployment ready",
                "click": "https://dashboard.example.com",
            },
        )
        result_str = str(result)
        assert "success" in result_str.lower()

        payload = get_payload_from_mock(mock_ntfy)
        assert payload["click"] == "https://dashboard.example.com"

    async def test_notification_with_action_buttons(self, client, mock_ntfy, env_vars):
        actions = [
            {
                "action": "view",
                "label": "Open PR",
                "url": "https://github.com/org/repo/pull/123",
            }
        ]
        result = await client.call_tool(
            "send_push_notification",
            {"message": "PR #123 needs review", "actions": actions},
        )
        result_str = str(result)
        assert "success" in result_str.lower()

        payload = get_payload_from_mock(mock_ntfy)
        assert payload["actions"] == actions

    async def test_notification_with_markdown(self, client, mock_ntfy, env_vars):
        result = await client.call_tool(
            "send_push_notification",
            {
                "message": "**Build failed** for `main` branch",
                "markdown": True,
            },
        )
        result_str = str(result)
        assert "success" in result_str.lower()

        payload = get_payload_from_mock(mock_ntfy)
        assert payload["markdown"] is True

    async def test_notification_with_attachment(self, client, mock_ntfy, env_vars):
        result = await client.call_tool(
            "send_push_notification",
            {
                "message": "Screenshot of the error",
                "attach": "https://example.com/screenshot.png",
                "filename": "error.png",
            },
        )
        result_str = str(result)
        assert "success" in result_str.lower()

        payload = get_payload_from_mock(mock_ntfy)
        assert payload["attach"] == "https://example.com/screenshot.png"
        assert payload["filename"] == "error.png"

    async def test_notification_with_custom_icon(self, client, mock_ntfy, env_vars):
        result = await client.call_tool(
            "send_push_notification",
            {
                "message": "Deployment successful",
                "icon": "https://example.com/deploy-icon.png",
            },
        )
        result_str = str(result)
        assert "success" in result_str.lower()

        payload = get_payload_from_mock(mock_ntfy)
        assert payload["icon"] == "https://example.com/deploy-icon.png"

    async def test_notification_with_all_params(self, client, mock_ntfy, env_vars):
        actions = [{"action": "view", "label": "View", "url": "https://example.com"}]
        result = await client.call_tool(
            "send_push_notification",
            {
                "message": "**Full featured** notification test",
                "title": "Complete Test",
                "priority": 4,
                "tags": ["white_check_mark", "test"],
                "markdown": True,
                "click": "https://example.com",
                "icon": "https://example.com/icon.png",
                "actions": actions,
            },
        )
        result_str = str(result)
        assert "success" in result_str.lower()

        payload = get_payload_from_mock(mock_ntfy)
        assert payload["topic"] == "test-topic"
        assert payload["message"] == "**Full featured** notification test"
        assert payload["title"] == "Complete Test"
        assert payload["priority"] == 4
        assert payload["tags"] == ["white_check_mark", "test"]
        assert payload["markdown"] is True
        assert payload["click"] == "https://example.com"
        assert payload["icon"] == "https://example.com/icon.png"
        assert payload["actions"] == actions


class TestSendPushNotificationErrors:
    async def test_ntfy_connection_error(self, client, env_vars):
        with patch("services.ntfy.httpx.AsyncClient") as mock_class:
            mock_client = AsyncMock()
            mock_client.post.side_effect = httpx.ConnectError("Connection refused")
            mock_client.__aenter__.return_value = mock_client
            mock_client.__aexit__.return_value = None
            mock_class.return_value = mock_client

            with pytest.raises(ToolError) as exc_info:
                await client.call_tool(
                    "send_push_notification",
                    {"message": "Test"},
                )
            assert "connect" in str(exc_info.value).lower()

    async def test_ntfy_http_error(self, client, env_vars):
        with patch("services.ntfy.httpx.AsyncClient") as mock_class:
            mock_client = AsyncMock()
            mock_response = MagicMock()
            mock_response.status_code = 500
            mock_response.text = "Internal Server Error"
            mock_client.post.return_value = mock_response
            mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
                "Server Error",
                request=MagicMock(),
                response=mock_response,
            )
            mock_client.__aenter__.return_value = mock_client
            mock_client.__aexit__.return_value = None
            mock_class.return_value = mock_client

            with pytest.raises(ToolError) as exc_info:
                await client.call_tool(
                    "send_push_notification",
                    {"message": "Test"},
                )
            assert "500" in str(exc_info.value)
