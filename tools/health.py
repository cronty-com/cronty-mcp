from datetime import UTC, datetime

from fastmcp.exceptions import ToolError

from config import get_missing_env_vars


def health() -> dict:
    """Check server configuration and return health status."""
    missing = get_missing_env_vars()

    if missing:
        raise ToolError(f"Missing or empty environment variables: {', '.join(missing)}")

    now = datetime.now(UTC)
    return {
        "status": "healthy",
        "current_time_utc": now.isoformat(),
        "current_time_ms": int(now.timestamp() * 1000),
    }
