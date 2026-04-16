"""Prometheus-compatible metrics for Celery queue monitoring."""

from prometheus_client import Counter, Gauge, Histogram

QUEUE_DEPTH = Gauge(
    "celery_queue_depth",
    "Number of tasks in queue",
    ["queue_name"],
)

TASK_TOTAL = Counter(
    "celery_task_total",
    "Total tasks processed",
    ["task_name", "status"],
)

TASK_FAILURE_TOTAL = Counter(
    "celery_task_failures_total",
    "Total task failures",
    ["task_name"],
)

TASK_DURATION = Histogram(
    "celery_task_duration_seconds",
    "Task execution time in seconds",
    ["task_name"],
    buckets=(0.1, 0.5, 1.0, 5.0, 10.0, 30.0, 60.0, 120.0, 300.0),
)


def update_queue_depths(redis_client) -> None:  # noqa: ANN001
    """Refresh Prometheus queue depth gauges from Redis LLEN."""
    from src.queue.health import KNOWN_QUEUES

    for queue in KNOWN_QUEUES:
        try:
            depth = redis_client.llen(queue)
            QUEUE_DEPTH.labels(queue_name=queue).set(depth)
        except Exception:  # noqa: BLE001
            QUEUE_DEPTH.labels(queue_name=queue).set(-1)
