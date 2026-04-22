"""Integration tests for health checks against real Redis."""

import pytest
from src.queue.health import check_queue_depths, check_redis_health


@pytest.mark.integration
class TestHealthRedisIntegration:
    def test_redis_health_check(self, redis_client):
        result = check_redis_health(redis_client)
        assert result["status"] == "healthy"
        assert "memory_used" in result
        assert result["uptime_seconds"] > 0

    def test_queue_depths_real_redis(self, redis_client):
        redis_client.lpush("scrapers", "task1", "task2")
        depths = check_queue_depths(redis_client)
        assert depths["scrapers"] == 2
        assert depths["default"] == 0
