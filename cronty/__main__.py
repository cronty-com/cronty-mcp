import argparse
import sys

from dotenv import load_dotenv

load_dotenv()

from cronty.cli import token  # noqa: E402


def main():
    parser = argparse.ArgumentParser(
        prog="cronty",
        description="Cronty MCP CLI tools",
    )
    subparsers = parser.add_subparsers(dest="command")

    token.register(subparsers)

    args = parser.parse_args()

    if args.command == "token":
        token.handle(args)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
