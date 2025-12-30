from dotenv import load_dotenv
from fastmcp import FastMCP

from tools import health

load_dotenv()

mcp = FastMCP("Cronty MCP")

mcp.tool(health)

if __name__ == "__main__":
    mcp.run()
