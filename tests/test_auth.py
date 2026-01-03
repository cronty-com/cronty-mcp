from datetime import UTC, datetime, timedelta

import jwt
import pytest


class TestCreateAuth:
    def test_returns_none_when_auth_disabled(self, monkeypatch):
        monkeypatch.setenv("AUTH_DISABLED", "true")
        monkeypatch.delenv("JWT_SECRET", raising=False)

        from server import create_auth

        assert create_auth() is None

    def test_returns_verifier_when_auth_enabled(self, monkeypatch):
        monkeypatch.delenv("AUTH_DISABLED", raising=False)
        monkeypatch.setenv(
            "JWT_SECRET",
            "test-secret-that-is-at-least-64-characters-long-for-hs512-algorithm",
        )

        from server import create_auth

        verifier = create_auth()
        assert verifier is not None

    def test_raises_when_no_secret(self, monkeypatch):
        monkeypatch.delenv("AUTH_DISABLED", raising=False)
        monkeypatch.delenv("JWT_SECRET", raising=False)

        from server import create_auth

        with pytest.raises(ValueError, match="JWT_SECRET is required"):
            create_auth()


class TestTokenValidation:
    @pytest.fixture
    def secret(self):
        return "test-secret-that-is-at-least-64-characters-long-for-hs512-algorithm"

    @pytest.fixture
    def valid_token(self, secret):
        payload = {
            "sub": "user@example.com",
            "iss": "cronty-mcp",
            "iat": datetime.now(UTC),
            "exp": datetime.now(UTC) + timedelta(days=365),
        }
        return jwt.encode(payload, secret, algorithm="HS512")

    @pytest.fixture
    def expired_token(self, secret):
        payload = {
            "sub": "user@example.com",
            "iss": "cronty-mcp",
            "iat": datetime.now(UTC) - timedelta(days=2),
            "exp": datetime.now(UTC) - timedelta(days=1),
        }
        return jwt.encode(payload, secret, algorithm="HS512")

    @pytest.fixture
    def wrong_issuer_token(self, secret):
        payload = {
            "sub": "user@example.com",
            "iss": "wrong-issuer",
            "iat": datetime.now(UTC),
            "exp": datetime.now(UTC) + timedelta(days=365),
        }
        return jwt.encode(payload, secret, algorithm="HS512")

    def test_valid_token_decodes(self, secret, valid_token):
        decoded = jwt.decode(
            valid_token,
            secret,
            algorithms=["HS512"],
            options={"require": ["sub", "iss", "iat", "exp"]},
        )
        assert decoded["sub"] == "user@example.com"
        assert decoded["iss"] == "cronty-mcp"

    def test_wrong_secret_fails(self, valid_token):
        wrong_secret = "wrong-secret-that-is-at-least-64-characters-long-for-testing"
        with pytest.raises(jwt.InvalidSignatureError):
            jwt.decode(valid_token, wrong_secret, algorithms=["HS512"])

    def test_expired_token_fails(self, secret, expired_token):
        with pytest.raises(jwt.ExpiredSignatureError):
            jwt.decode(expired_token, secret, algorithms=["HS512"])

    def test_wrong_issuer_detected(self, secret, wrong_issuer_token):
        decoded = jwt.decode(wrong_issuer_token, secret, algorithms=["HS512"])
        assert decoded["iss"] != "cronty-mcp"

    def test_tampered_token_fails(self, secret, valid_token):
        parts = valid_token.split(".")
        tampered = parts[0] + "." + parts[1] + "tampered." + parts[2]
        with pytest.raises(jwt.DecodeError):
            jwt.decode(tampered, secret, algorithms=["HS512"])
