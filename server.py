from dotenv import load_dotenv
from fastmcp import FastMCP

from config import get_jwt_secret, is_auth_disabled
from resources import get_cron_examples, get_valid_timezones
from tools import (
    delete_schedule,
    get_current_time,
    list_scheduled_notifications,
    pause_schedule,
    resume_schedule,
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

mcp.tool(delete_schedule)
mcp.tool(get_current_time)
mcp.tool(list_scheduled_notifications)
mcp.tool(pause_schedule)
mcp.tool(resume_schedule)
mcp.tool(schedule_cron_notification)
mcp.tool(schedule_notification)
mcp.tool(send_push_notification)

mcp.resource("cron://examples")(get_cron_examples)
mcp.resource("timezones://valid")(get_valid_timezones)

if __name__ == "__main__":
    mcp.run()
