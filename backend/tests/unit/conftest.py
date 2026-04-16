"""Unit test fixtures — no external services required."""

import pytest
from celery import Celery
from fakeredis import FakeRedis


@pytest.fixture
def fake_redis() -> FakeRedis:
    """In-memory Redis mock for unit tests."""
    client = FakeRedis(decode_responses=True)
    yield client
    client.flushall()


@pytest.fixture
def celery_app() -> Celery:
    """Celery app in eager mode for synchronous unit testing."""
    app = Celery("test")
    app.conf.update(
        task_always_eager=True,
        task_eager_propagates=True,
        task_serializer="json",
        accept_content=["json"],
        result_serializer="json",
        broker_url="memory://",
        result_backend="cache+memory://",
    )
    return app
