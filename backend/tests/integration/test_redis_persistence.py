"""Integration tests for Redis AOF persistence configuration.

Verifies that Redis is running with production-grade persistence settings
so Celery tasks survive Redis restarts (Issue #25 acceptance criterion).

These tests require the custom redis.conf (via docker compose). In CI,
GitHub Actions service containers use vanilla Redis defaults, so tests
that depend on custom config are skipped automatically.
"""

from __future__ import annotations

import time

import pytest


def _has_custom_config(redis_client) -> bool:
    """Check if Redis is running with our custom redis.conf (AOF enabled)."""
    info = redis_client.info("persistence")
    return info.get("aof_enabled", 0) == 1


@pytest.mark.integration
class TestRedisAOFPersistence:
    """Verify Redis persistence configuration via INFO and CONFIG commands."""

    def test_aof_is_enabled(self, redis_client):
        if not _has_custom_config(redis_client):
            pytest.skip("Redis running without custom redis.conf (CI service container)")
        info = redis_client.info("persistence")
        assert info["aof_enabled"] == 1

    def test_appendfsync_policy(self, redis_client):
        if not _has_custom_config(redis_client):
            pytest.skip("Redis running without custom redis.conf (CI service container)")
        config = redis_client.config_get("appendfsync")
        assert config["appendfsync"] == "everysec"

    def test_rdb_snapshots_configured(self, redis_client):
        config = redis_client.config_get("save")
        assert config["save"] != ""

    def test_maxmemory_policy(self, redis_client):
        if not _has_custom_config(redis_client):
            pytest.skip("Redis running without custom redis.conf (CI service container)")
        config = redis_client.config_get("maxmemory-policy")
        assert config["maxmemory-policy"] == "allkeys-lru"

    def test_data_survives_aof_rewrite(self, redis_client):
        if not _has_custom_config(redis_client):
            pytest.skip("Redis running without custom redis.conf (CI service container)")
        key = "test_persistence_queue"
        redis_client.delete(key)

        redis_client.lpush(key, '{"task": "test", "id": "persist-1"}')
        redis_client.lpush(key, '{"task": "test", "id": "persist-2"}')

        redis_client.bgrewriteaof()
        time.sleep(1)

        assert redis_client.llen(key) == 2
        entries = redis_client.lrange(key, 0, -1)
        assert len(entries) == 2

        redis_client.delete(key)
