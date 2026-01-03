from datetime import timedelta

import jwt
import pytest

from cronty.cli.token import ALGORITHM, ISSUER, issue_token, parse_duration


class TestParseDuration:
    def test_parse_days(self):
        assert parse_duration("30d") == timedelta(days=30)

    def test_parse_hours(self):
        assert parse_duration("12h") == timedelta(hours=12)

    def test_parse_minutes(self):
        assert parse_duration("45m") == timedelta(minutes=45)

    def test_parse_seconds(self):
        assert parse_duration("90s") == timedelta(seconds=90)

    def test_parse_years(self):
        assert parse_duration("1y") == timedelta(days=365)
        assert parse_duration("2y") == timedelta(days=730)

    def test_invalid_format_raises(self):
        with pytest.raises(ValueError, match="Invalid duration format"):
            parse_duration("invalid")

    def test_missing_unit_raises(self):
        with pytest.raises(ValueError, match="Invalid duration format"):
            parse_duration("30")

    def test_empty_string_raises(self):
        with pytest.raises(ValueError, match="Invalid duration format"):
            parse_duration("")


class TestIssueToken:
    def test_issues_valid_jwt(self, monkeypatch, capsys):
        secret = "test-secret-that-is-at-least-64-characters-long-for-hs512-algorithm"
        monkeypatch.setenv("JWT_SECRET", secret)

        issue_token("user@example.com", "365d")

        captured = capsys.readouterr()
        token = captured.out.strip()

        decoded = jwt.decode(token, secret, algorithms=[ALGORITHM])
        assert decoded["sub"] == "user@example.com"
        assert decoded["iss"] == ISSUER
        assert "iat" in decoded
        assert "exp" in decoded

    def test_token_signed_with_hs512(self, monkeypatch, capsys):
        secret = "test-secret-that-is-at-least-64-characters-long-for-hs512-algorithm"
        monkeypatch.setenv("JWT_SECRET", secret)

        issue_token("user@example.com", "1d")

        captured = capsys.readouterr()
        token = captured.out.strip()

        header = jwt.get_unverified_header(token)
        assert header["alg"] == "HS512"

    def test_custom_expiration(self, monkeypatch, capsys):
        secret = "test-secret-that-is-at-least-64-characters-long-for-hs512-algorithm"
        monkeypatch.setenv("JWT_SECRET", secret)

        issue_token("user@example.com", "30d")

        captured = capsys.readouterr()
        token = captured.out.strip()

        decoded = jwt.decode(token, secret, algorithms=[ALGORITHM])
        exp_delta = decoded["exp"] - decoded["iat"]
        assert exp_delta == 30 * 24 * 60 * 60  # 30 days in seconds

    def test_missing_secret_exits(self, monkeypatch, capsys):
        monkeypatch.delenv("JWT_SECRET", raising=False)

        with pytest.raises(SystemExit) as exc_info:
            issue_token("user@example.com", "365d")

        assert exc_info.value.code == 1

        captured = capsys.readouterr()
        assert "JWT_SECRET" in captured.err

    def test_invalid_duration_exits(self, monkeypatch, capsys):
        secret = "test-secret-that-is-at-least-64-characters-long-for-hs512-algorithm"
        monkeypatch.setenv("JWT_SECRET", secret)

        with pytest.raises(SystemExit) as exc_info:
            issue_token("user@example.com", "invalid")

        assert exc_info.value.code == 1

        captured = capsys.readouterr()
        assert "Invalid duration format" in captured.err
