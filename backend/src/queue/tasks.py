"""Celery tasks for periodic maintenance.

These tasks are referenced by Celery Beat schedule entries in `src.queue.beat_schedules`.
They must exist and be registered, otherwise Celery Beat will raise `NotRegistered` on every tick.
"""

from __future__ import annotations

import structlog
import redis as redis_lib
from celery import shared_task

from src.core.config import RedisSettings
from src.queue.health import check_queue_depths, check_redis_health
from src.queue.monitoring import update_queue_depths

logger = structlog.get_logger(__name__)


def _get_redis_client() -> redis_lib.Redis:
    settings = RedisSettings()
    return redis_lib.from_url(settings.url, decode_responses=True)


@shared_task(name="src.queue.tasks.health_check_scrapers")
def health_check_scrapers() -> dict[str, object]:
    """Periodic health check for Redis + queue depths.

    Kept lightweight: probes Redis and updates Prometheus gauges.
    """
    client = _get_redis_client()

    redis_health = check_redis_health(client)
    depths = check_queue_depths(client)

    # Best-effort metrics update: should never crash the Beat tick.
    try:
        update_queue_depths(client)
    except Exception as exc:  # noqa: BLE001
        logger.warning("queue_metrics_update_failed", error=str(exc))

    logger.info("periodic_health_check_completed", redis=redis_health, queue_depths=depths)
    return {"redis": redis_health, "queue_depths": depths}


@shared_task(name="src.queue.tasks.data_retention_purge")
def data_retention_purge() -> dict[str, str]:
    """Periodic retention purge.

    The actual retention policy (what to delete, how to audit, and how to avoid deleting evidence)
    should be implemented in a dedicated service/module. For now, keep the Beat schedule healthy.
    """
    logger.warning("data_retention_purge_not_implemented")
    return {"status": "skipped", "reason": "not_implemented"}

