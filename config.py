import os

REQUIRED_ENV_VARS = [
    "QSTASH_TOKEN",
    "NTFY_TOPIC",
]


def get_missing_env_vars() -> list[str]:
    """Return the list of required env vars that are missing or empty."""
    missing = []
    for var in REQUIRED_ENV_VARS:
        value = os.environ.get(var, "")
        if not value:
            missing.append(var)
    return missing
