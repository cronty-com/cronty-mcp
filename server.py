from dotenv import load_dotenv
from fastmcp import FastMCP

from config import get_jwt_secret, is_auth_disabled
from tools import (
    health,
    list_scheduled_notifications,
    schedule_cron_notification,
    schedule_notification,
    send_push_notification,
)

load_dotenv()


def create_auth():
    if is_auth_disabled():
        return None

    from fastmcp.server.auth.providers.jwt import JWTVerifier

    secret = get_jwt_secret()
    if not secret:
        raise ValueError("JWT_SECRET is required when authentication is enabled")

    return JWTVerifier(
        public_key=secret,
        issuer="cronty-mcp",
        algorithm="HS512",
    )


mcp = FastMCP("Cronty MCP", auth=create_auth())

mcp.tool(health)
mcp.tool(list_scheduled_notifications)
mcp.tool(schedule_cron_notification)
mcp.tool(schedule_notification)
mcp.tool(send_push_notification)

if __name__ == "__main__":
    mcp.run()
