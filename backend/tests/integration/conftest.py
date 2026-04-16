"""Integration test fixtures — requires a running Redis instance."""

import os

import pytest
import redis

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")


@pytest.fixture
def redis_client() -> redis.Redis:
    """Real Redis connection for integration tests.

    Flushes the test database on teardown.
    """
    client = redis.from_url(REDIS_URL, decode_responses=True)
    try:
        client.ping()
    except redis.ConnectionError:
        pytest.skip("Redis not available — start with: docker compose up redis -d")
    yield client
    client.flushdb()
    client.close()
