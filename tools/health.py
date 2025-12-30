from fastmcp.exceptions import ToolError

from config import get_missing_env_vars


def health() -> str:
    """Check server configuration and return health status."""
    missing = get_missing_env_vars()

    if missing:
        raise ToolError(f"Missing or empty environment variables: {', '.join(missing)}")

    return "I am healthy"
