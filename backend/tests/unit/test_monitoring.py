"""Tests for Prometheus monitoring metrics."""

import pytest

from src.queue.monitoring import (
    QUEUE_DEPTH,
    TASK_DURATION,
    TASK_FAILURE_TOTAL,
    TASK_TOTAL,
    update_queue_depths,
)


@pytest.mark.unit
class TestPrometheusMetrics:
    def test_queue_depth_gauge_exists(self):
        assert QUEUE_DEPTH is not None
        assert QUEUE_DEPTH._name == "celery_queue_depth"

    def test_task_total_counter_exists(self):
        assert TASK_TOTAL is not None
        # prometheus_client Counter strips _total suffix from _name
        assert TASK_TOTAL._name == "celery_task"

    def test_task_failure_counter_exists(self):
        assert TASK_FAILURE_TOTAL is not None
        assert TASK_FAILURE_TOTAL._name == "celery_task_failures"

    def test_task_duration_histogram_exists(self):
        assert TASK_DURATION is not None
        assert TASK_DURATION._name == "celery_task_duration_seconds"

    def test_task_total_increment(self):
        TASK_TOTAL.labels(task_name="test_task", status="SUCCESS").inc()
        # Counter can only go up — no assertion on exact value since
        # prometheus_client is process-global, but no exception = pass

    def test_task_failure_increment(self):
        TASK_FAILURE_TOTAL.labels(task_name="test_task").inc()

    def test_task_duration_observe(self):
        TASK_DURATION.labels(task_name="test_task").observe(1.5)


@pytest.mark.unit
class TestUpdateQueueDepths:
    def test_updates_gauge_from_redis(self, fake_redis):
        fake_redis.lpush("scrapers", "t1", "t2")
        fake_redis.lpush("evidence", "t3")
        update_queue_depths(fake_redis)
        # Verify gauges were set (no exception = working)
        assert QUEUE_DEPTH.labels(queue_name="scrapers")._value.get() == 2.0
        assert QUEUE_DEPTH.labels(queue_name="evidence")._value.get() == 1.0

    def test_handles_redis_error(self):
        from unittest.mock import MagicMock

        mock_client = MagicMock()
        mock_client.llen.side_effect = Exception("connection lost")
        update_queue_depths(mock_client)
        # Should set -1 for all queues, not raise
        for queue in ["default", "scrapers", "evidence", "dead_letter"]:
            assert QUEUE_DEPTH.labels(queue_name=queue)._value.get() == -1.0
