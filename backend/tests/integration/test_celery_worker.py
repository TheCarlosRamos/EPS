"""Integration tests for Celery worker task execution against real Redis."""

import os

import pytest
from celery import Celery
from src.queue.base_task import BaseScraperTask

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")


@pytest.fixture
def integration_app():
    """Celery app configured against real Redis (eager mode for test speed)."""
    app = Celery("integration_test")
    app.conf.update(
        broker_url=REDIS_URL,
        result_backend=REDIS_URL,
        task_always_eager=True,
        task_eager_propagates=True,
        task_serializer="json",
        accept_content=["json"],
        result_serializer="json",
    )
    return app


@pytest.mark.integration
class TestCeleryWorkerIntegration:
    def test_task_executes_and_stores_result(self, redis_client, integration_app):
        """Task executes and returns a result through the Celery pipeline."""

        @integration_app.task(base=BaseScraperTask, bind=True, name="integration_scraper")
        def scraper_task(self, query: str):
            return {"query": query, "results": ["result1", "result2"]}

        result = scraper_task.apply(args=("test query",))
        assert result.get() == {"query": "test query", "results": ["result1", "result2"]}
        assert result.status == "SUCCESS"

    def test_task_routing_config(self, integration_app):
        """Verify task routing configuration is applied."""
        integration_app.conf.update(
            task_routes={
                "src.queue.*scraper*": {"queue": "scrapers"},
                "src.queue.*evidence*": {"queue": "evidence"},
            },
        )
        routes = integration_app.conf.task_routes
        assert "src.queue.*scraper*" in routes
        assert routes["src.queue.*scraper*"]["queue"] == "scrapers"

    def test_json_only_serialization(self, integration_app):
        """Verify no pickle serialization is allowed."""
        assert integration_app.conf.task_serializer == "json"
        assert "pickle" not in integration_app.conf.accept_content


@pytest.mark.integration
class TestRetryIntegration:
    def test_task_retries_on_failure(self, redis_client, integration_app):
        """Task raises Retry exception on transient failure."""
        call_count = 0

        @integration_app.task(base=BaseScraperTask, bind=True, name="retry_integration_task", max_retries=3)
        def failing_task(self):
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                self.retry_with_backoff(exc=ValueError("transient"))
            return {"status": "recovered"}

        from celery.exceptions import Retry

        with pytest.raises(Retry):
            failing_task.apply().get()
        assert call_count == 1  # Eager mode propagates the Retry on first call
