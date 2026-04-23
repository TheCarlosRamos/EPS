"""Tests for core configuration settings."""

import pytest

from src.core.config import CelerySettings, PostgresSettings, RedisSettings, get_beat_database_url


# Test fixtures
@pytest.fixture
def redis_test_password():
    """Test password for Redis settings."""
    return "s3cret"


@pytest.fixture
def redis_short_password():
    """Short test password."""
    return "pw"


@pytest.fixture
def redis_env_password():
    """Environment-based password."""
    return "env-pw"


@pytest.mark.unit
class TestRedisSettings:
    def test_default_url_no_password(self):
        settings = RedisSettings(host="localhost", port=6379, db=0, password="")
        assert settings.url == "redis://localhost:6379/0"

    def test_url_with_password(self, redis_test_password):
        settings = RedisSettings(host="redis.internal", port=6380, db=2, password=redis_test_password)
        assert settings.url == f"redis://:{redis_test_password}@redis.internal:6380/2"

    def test_default_values(self):
        settings = RedisSettings()
        assert settings.host == "localhost"
        assert settings.port == 6379
        assert settings.db == 0
        assert settings.password == ""
        assert settings.max_memory == "512mb"

    def test_custom_values(self, redis_short_password):
        settings = RedisSettings(host="10.0.0.1", port=6380, db=3, password=redis_short_password, max_memory="1gb")
        assert settings.host == "10.0.0.1"
        assert settings.port == 6380
        assert settings.db == 3
        assert settings.max_memory == "1gb"

    def test_from_env(self, monkeypatch, redis_env_password):
        monkeypatch.setenv("REDIS_HOST", "env-host")
        monkeypatch.setenv("REDIS_PORT", "7777")
        monkeypatch.setenv("REDIS_DB", "5")
        monkeypatch.setenv("REDIS_PASSWORD", redis_env_password)
        settings = RedisSettings()
        assert settings.url == f"redis://:{redis_env_password}@env-host:7777/5"


@pytest.mark.unit
class TestCelerySettings:
    def test_defaults(self):
        settings = CelerySettings()
        assert settings.task_serializer == "json"
        assert settings.result_serializer == "json"
        assert settings.accept_content == ["json"]
        assert settings.task_track_started is True
        assert settings.worker_hijack_root_logger is False
        assert settings.task_default_queue == "default"

    def test_json_only_serialization(self):
        """Ensure pickle is never accepted (security requirement)."""
        settings = CelerySettings()
        assert "pickle" not in settings.accept_content
        assert settings.task_serializer != "pickle"
        assert settings.result_serializer != "pickle"

    def test_from_env(self, monkeypatch):
        monkeypatch.setenv("CELERY_BROKER_URL", "redis://custom:6379/1")
        monkeypatch.setenv("CELERY_RESULT_BACKEND", "redis://custom:6379/2")
        settings = CelerySettings()
        assert settings.broker_url == "redis://custom:6379/1"
        assert settings.result_backend == "redis://custom:6379/2"


@pytest.mark.unit
class TestBeatDatabaseUrl:
    def test_explicit_beat_dburi(self, monkeypatch):
        monkeypatch.setenv("CELERY_BEAT_DBURI", "postgresql+psycopg://u:p@db:5432/beatdb")
        assert get_beat_database_url() == "postgresql+psycopg://u:p@db:5432/beatdb"

    def test_derived_from_postgres_env(self, monkeypatch):
        monkeypatch.delenv("CELERY_BEAT_DBURI", raising=False)
        monkeypatch.setenv("POSTGRES_USER", "osint")
        monkeypatch.setenv("POSTGRES_PASSWORD", "secret@x")
        monkeypatch.setenv("POSTGRES_HOST", "postgres.internal")
        monkeypatch.setenv("POSTGRES_PORT", "5433")
        monkeypatch.setenv("POSTGRES_DB", "osint_dev")
        url = get_beat_database_url()
        assert url.startswith("postgresql+psycopg://")
        assert "postgres.internal:5433" in url
        assert "secret%40x" in url

    def test_postgres_defaults(self):
        pg = PostgresSettings()
        assert pg.host == "localhost"
        assert pg.port == 5432
