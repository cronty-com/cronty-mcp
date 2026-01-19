from resources.data import CRON_EXAMPLES, TIMEZONES


def get_cron_examples() -> dict:
    """Common cron expression examples with descriptions."""
    return {
        "examples": CRON_EXAMPLES,
        "format_help": "Fields: minute hour day-of-month month day-of-week",
    }


def get_valid_timezones() -> dict:
    """Common IANA timezones grouped by region."""
    return {
        "timezones": TIMEZONES,
        "count": len(TIMEZONES),
    }
