from dotenv import load_dotenv
from fastmcp import FastMCP

from tools import health, schedule_notification, send_push_notification

load_dotenv()

mcp = FastMCP("Cronty MCP")

mcp.tool(health)
mcp.tool(schedule_notification)
mcp.tool(send_push_notification)

if __name__ == "__main__":
    mcp.run()
