"""Redis health checks and queue depth probes."""

from __future__ import annotations

from typing import Any

import redis as redis_lib

KNOWN_QUEUES = ["default", "scrapers", "evidence", "dead_letter"]


def check_redis_health(redis_client: redis_lib.Redis) -> dict[str, Any]:
    """Check Redis connectivity and return basic server info."""
    try:
        redis_client.ping()
        info = redis_client.info("memory")
        server_info = redis_client.info("server")
        return {
            "status": "healthy",
            "memory_used": info.get("used_memory_human", "unknown"),
            "memory_peak": info.get("used_memory_peak_human", "unknown"),
            "uptime_seconds": server_info.get("uptime_in_seconds", 0),
        }
    except redis_lib.ConnectionError:
        return {"status": "unhealthy", "error": "connection_failed"}
    except redis_lib.RedisError as exc:
        return {"status": "unhealthy", "error": str(exc)}


def check_queue_depths(redis_client: redis_lib.Redis) -> dict[str, int]:
    """Return the depth (LLEN) of each known Celery queue in Redis."""
    depths: dict[str, int] = {}
    for queue in KNOWN_QUEUES:
        try:
            depths[queue] = redis_client.llen(queue)
        except redis_lib.RedisError:
            depths[queue] = -1
    return depths
