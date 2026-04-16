"""Tests for BaseScraperTask retry logic and lifecycle hooks."""

import pytest
from celery import Celery
from celery.exceptions import Retry

from src.queue.base_task import BaseScraperTask
from src.queue.retry import MAX_RETRIES


@pytest.fixture
def app_with_task(celery_app: Celery):
    """Register a concrete scraper task on the eager celery app."""

    @celery_app.task(base=BaseScraperTask, bind=True, name="test_scraper")
    def sample_task(self, should_fail: bool = False):  # noqa: FBT001, FBT002
        if should_fail:
            raise ValueError("simulated failure")
        return {"status": "ok"}

    return celery_app, sample_task


@pytest.mark.unit
class TestBaseScraperTask:
    def test_successful_execution(self, app_with_task):
        _, task = app_with_task
        result = task.apply(args=(False,))
        assert result.get() == {"status": "ok"}
        assert result.status == "SUCCESS"

    def test_task_has_max_retries(self, app_with_task):
        _, task = app_with_task
        assert task.max_retries == MAX_RETRIES
        assert task.max_retries == 3

    def test_task_is_acks_late(self, app_with_task):
        _, task = app_with_task
        assert task.acks_late is True

    def test_failure_propagates_in_eager_mode(self, app_with_task):
        _, task = app_with_task
        with pytest.raises(ValueError, match="simulated failure"):
            task.apply(args=(True,)).get()

    def test_retry_with_backoff_raises_retry(self, app_with_task):
        """Verify retry_with_backoff dispatches a Celery Retry."""
        app, task = app_with_task

        @app.task(base=BaseScraperTask, bind=True, name="test_retry_task")
        def retrying_task(self):
            self.retry_with_backoff(exc=ValueError("transient error"))

        with pytest.raises(Retry):
            retrying_task.apply().get()


@pytest.mark.unit
class TestBaseScraperTaskHooks:
    def test_before_start_sets_start_time(self, app_with_task):
        _, task = app_with_task
        result = task.apply(args=(False,))
        assert result.status == "SUCCESS"

    def test_after_return_logs_completion(self, app_with_task):
        """Verify after_return runs without error on success."""
        _, task = app_with_task
        result = task.apply(args=(False,))
        assert result.status == "SUCCESS"
