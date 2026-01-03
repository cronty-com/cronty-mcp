import re
import sys
from datetime import UTC, datetime, timedelta

import jwt

from config import get_jwt_secret

ISSUER = "cronty-mcp"
ALGORITHM = "HS512"
DEFAULT_EXPIRES_IN = "365d"


def register(subparsers):
    token_parser = subparsers.add_parser("token", help="Token management")
    token_sub = token_parser.add_subparsers(dest="token_command")

    issue_parser = token_sub.add_parser("issue", help="Issue a new token")
    issue_parser.add_argument("--email", required=True, help="User email address")
    issue_parser.add_argument(
        "--expires-in",
        default=DEFAULT_EXPIRES_IN,
        help=f"Token validity duration (default: {DEFAULT_EXPIRES_IN})",
    )


def handle(args):
    if args.token_command == "issue":
        issue_token(args.email, args.expires_in)
    else:
        print("Usage: cronty token issue --email <email>", file=sys.stderr)
        sys.exit(1)


def issue_token(email: str, expires_in: str) -> None:
    secret = get_jwt_secret()
    if not secret:
        print("Error: JWT_SECRET environment variable is required", file=sys.stderr)
        sys.exit(1)

    try:
        expiry_delta = parse_duration(expires_in)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    now = datetime.now(UTC)
    payload = {
        "sub": email,
        "iss": ISSUER,
        "iat": now,
        "exp": now + expiry_delta,
    }

    token = jwt.encode(payload, secret, algorithm=ALGORITHM)
    print(token)


def parse_duration(duration: str) -> timedelta:
    pattern = r"^(\d+)(d|h|m|s|y)$"
    match = re.match(pattern, duration)

    if not match:
        raise ValueError(
            f"Invalid duration format: {duration}. "
            "Valid examples: 30d, 12h, 1y, 365d"
        )

    value = int(match.group(1))
    unit = match.group(2)

    if unit == "d":
        return timedelta(days=value)
    elif unit == "h":
        return timedelta(hours=value)
    elif unit == "m":
        return timedelta(minutes=value)
    elif unit == "s":
        return timedelta(seconds=value)
    elif unit == "y":
        return timedelta(days=value * 365)
    else:
        raise ValueError(f"Unknown time unit: {unit}")
