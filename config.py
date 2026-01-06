import os

REQUIRED_ENV_VARS = [
    "QSTASH_TOKEN",
]


def get_jwt_secret() -> str | None:
    return os.environ.get("JWT_SECRET") or None


def is_auth_disabled() -> bool:
    return os.environ.get("AUTH_DISABLED", "").lower() == "true"


def get_missing_env_vars() -> list[str]:
    """Return the list of required env vars that are missing or empty."""
    missing = []
    for var in REQUIRED_ENV_VARS:
        value = os.environ.get(var, "")
        if not value:
            missing.append(var)

    if not is_auth_disabled() and not get_jwt_secret():
        missing.append("JWT_SECRET")

    return missing
