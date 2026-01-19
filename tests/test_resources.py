import re

from resources.resources import get_cron_examples, get_valid_timezones


class TestCronExamples:
    def test_has_required_fields(self):
        result = get_cron_examples()
        assert "examples" in result
        assert "format_help" in result

    def test_each_example_has_expression_and_description(self):
        result = get_cron_examples()
        for example in result["examples"]:
            assert "expression" in example
            assert "description" in example

    def test_has_at_least_five_examples(self):
        result = get_cron_examples()
        assert len(result["examples"]) >= 5

    def test_all_expressions_are_valid_five_field_cron(self):
        result = get_cron_examples()
        cron_pattern = re.compile(
            r"^(\*|[0-9,\-\/\*]+)\s+"
            r"(\*|[0-9,\-\/\*]+)\s+"
            r"(\*|[0-9,\-\/\*]+)\s+"
            r"(\*|[0-9,\-\/\*]+)\s+"
            r"(\*|[0-9,\-\/\*]+)$"
        )
        for example in result["examples"]:
            expr = example["expression"]
            assert cron_pattern.match(expr), f"Invalid cron expression: {expr}"

    def test_format_help_explains_five_fields(self):
        result = get_cron_examples()
        format_help = result["format_help"].lower()
        assert "minute" in format_help
        assert "hour" in format_help
        assert "day" in format_help
        assert "month" in format_help


class TestValidTimezones:
    def test_has_required_fields(self):
        result = get_valid_timezones()
        assert "timezones" in result
        assert "count" in result

    def test_each_timezone_has_zone_and_region(self):
        result = get_valid_timezones()
        for tz in result["timezones"]:
            assert "zone" in tz
            assert "region" in tz

    def test_count_matches_list_length(self):
        result = get_valid_timezones()
        assert result["count"] == len(result["timezones"])

    def test_covers_major_regions(self):
        result = get_valid_timezones()
        regions = {tz["region"] for tz in result["timezones"]}
        assert "Americas" in regions
        assert "Europe" in regions
        assert "Asia" in regions
        assert "Oceania" in regions

    def test_includes_utc(self):
        result = get_valid_timezones()
        zones = [tz["zone"] for tz in result["timezones"]]
        assert "UTC" in zones

    def test_has_at_least_three_different_regions(self):
        result = get_valid_timezones()
        regions = {tz["region"] for tz in result["timezones"]}
        assert len(regions) >= 3
