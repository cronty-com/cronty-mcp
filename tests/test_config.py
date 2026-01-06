from config import get_jwt_secret, get_missing_env_vars, is_auth_disabled


class TestIsAuthDisabled:
    def test_returns_false_by_default(self, monkeypatch):
        monkeypatch.delenv("AUTH_DISABLED", raising=False)
        assert is_auth_disabled() is False

    def test_returns_false_for_empty_string(self, monkeypatch):
        monkeypatch.setenv("AUTH_DISABLED", "")
        assert is_auth_disabled() is False

    def test_returns_true_when_true(self, monkeypatch):
        monkeypatch.setenv("AUTH_DISABLED", "true")
        assert is_auth_disabled() is True

    def test_returns_true_case_insensitive(self, monkeypatch):
        monkeypatch.setenv("AUTH_DISABLED", "TRUE")
        assert is_auth_disabled() is True

        monkeypatch.setenv("AUTH_DISABLED", "True")
        assert is_auth_disabled() is True

    def test_returns_false_for_other_values(self, monkeypatch):
        monkeypatch.setenv("AUTH_DISABLED", "false")
        assert is_auth_disabled() is False

        monkeypatch.setenv("AUTH_DISABLED", "1")
        assert is_auth_disabled() is False

        monkeypatch.setenv("AUTH_DISABLED", "yes")
        assert is_auth_disabled() is False


class TestGetJwtSecret:
    def test_returns_secret_from_env(self, monkeypatch):
        monkeypatch.setenv("JWT_SECRET", "my-secret-key")
        assert get_jwt_secret() == "my-secret-key"

    def test_returns_none_when_not_set(self, monkeypatch):
        monkeypatch.delenv("JWT_SECRET", raising=False)
        assert get_jwt_secret() is None

    def test_returns_none_for_empty_string(self, monkeypatch):
        monkeypatch.setenv("JWT_SECRET", "")
        assert get_jwt_secret() is None


class TestGetMissingEnvVars:
    def test_returns_empty_when_all_set_with_auth_disabled(self, monkeypatch):
        monkeypatch.setenv("QSTASH_TOKEN", "token")
        monkeypatch.setenv("AUTH_DISABLED", "true")
        monkeypatch.delenv("JWT_SECRET", raising=False)

        assert get_missing_env_vars() == []

    def test_returns_empty_when_all_set_with_auth_enabled(self, monkeypatch):
        monkeypatch.setenv("QSTASH_TOKEN", "token")
        monkeypatch.setenv("JWT_SECRET", "secret")
        monkeypatch.delenv("AUTH_DISABLED", raising=False)

        assert get_missing_env_vars() == []

    def test_includes_jwt_secret_when_auth_enabled(self, monkeypatch):
        monkeypatch.setenv("QSTASH_TOKEN", "token")
        monkeypatch.delenv("JWT_SECRET", raising=False)
        monkeypatch.delenv("AUTH_DISABLED", raising=False)

        missing = get_missing_env_vars()
        assert "JWT_SECRET" in missing

    def test_excludes_jwt_secret_when_auth_disabled(self, monkeypatch):
        monkeypatch.setenv("QSTASH_TOKEN", "token")
        monkeypatch.setenv("AUTH_DISABLED", "true")
        monkeypatch.delenv("JWT_SECRET", raising=False)

        missing = get_missing_env_vars()
        assert "JWT_SECRET" not in missing

    def test_includes_qstash_token_when_missing(self, monkeypatch):
        monkeypatch.delenv("QSTASH_TOKEN", raising=False)
        monkeypatch.setenv("AUTH_DISABLED", "true")

        missing = get_missing_env_vars()
        assert "QSTASH_TOKEN" in missing
