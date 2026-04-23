"""Tests for Redis health check and queue depth probes."""

import pytest
from fakeredis import FakeRedis
from src.queue.health import KNOWN_QUEUES, check_queue_depths, check_redis_health


@pytest.mark.unit
class TestCheckRedisHealth:
    def test_healthy_redis(self):
        """Test health check with a mock that supports info() calls."""
        from unittest.mock import MagicMock

        mock_client = MagicMock()
        mock_client.ping.return_value = True
        mock_client.info.side_effect = lambda section: {
            "memory": {"used_memory_human": "1.5M", "used_memory_peak_human": "2.0M"},
            "server": {"uptime_in_seconds": 3600},
        }[section]

        result = check_redis_health(mock_client)
        assert result["status"] == "healthy"
        assert result["memory_used"] == "1.5M"
        assert result["uptime_seconds"] == 3600

    def test_unhealthy_redis(self):
        """Simulate a connection failure with an unreachable client."""
        from unittest.mock import MagicMock

        import redis as redis_lib

        mock_client = MagicMock()
        mock_client.ping.side_effect = redis_lib.ConnectionError("refused")
        result = check_redis_health(mock_client)
        assert result["status"] == "unhealthy"
        assert result["error"] == "connection_failed"


@pytest.mark.unit
class TestCheckQueueDepths:
    def test_empty_queues(self, fake_redis: FakeRedis):
        depths = check_queue_depths(fake_redis)
        for queue in KNOWN_QUEUES:
            assert depths[queue] == 0

    def test_queue_with_items(self, fake_redis: FakeRedis):
        fake_redis.lpush("scrapers", "task1", "task2", "task3")
        fake_redis.lpush("dead_letter", "failed1")
        depths = check_queue_depths(fake_redis)
        assert depths["scrapers"] == 3
        assert depths["dead_letter"] == 1
        assert depths["default"] == 0

    def test_known_queues_include_all(self):
        assert "default" in KNOWN_QUEUES
        assert "scrapers" in KNOWN_QUEUES
        assert "evidence" in KNOWN_QUEUES
        assert "dead_letter" in KNOWN_QUEUES
