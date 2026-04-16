"""Dead Letter Queue (DLQ) manager for tasks that exhaust all retries.

Stores failed task metadata in a Redis list for inspection and replay.
Only exception messages are stored — tracebacks may contain PII from search queries.
"""

from __future__ import annotations

import json
import time
import uuid
from typing import Any

import redis as redis_lib
import structlog

logger = structlog.get_logger(__name__)

DLQ_KEY = "dead_letter"


class DLQManager:
    """Manage the dead letter queue backed by a Redis list."""

    def __init__(self, redis_client: redis_lib.Redis) -> None:
        self._redis = redis_client

    def send_to_dlq(
        self,
        task_name: str,
        task_id: str,
        args: tuple | list,
        kwargs: dict[str, Any],
        exception: str,
    ) -> str:
        """Write a failed task entry to the DLQ. Returns the DLQ entry ID."""
        entry_id = str(uuid.uuid4())
        entry = {
            "id": entry_id,
            "task_name": task_name,
            "task_id": task_id,
            "args": list(args),
            "kwargs": kwargs,
            "exception": exception,
            "timestamp": time.time(),
        }
        self._redis.lpush(DLQ_KEY, json.dumps(entry))
        logger.warning("task_sent_to_dlq", task_name=task_name, task_id=task_id, entry_id=entry_id)
        return entry_id

    def list_dlq(self, limit: int = 100, offset: int = 0) -> list[dict[str, Any]]:
        """Return DLQ entries with pagination."""
        raw_entries = self._redis.lrange(DLQ_KEY, offset, offset + limit - 1)
        return [json.loads(entry) for entry in raw_entries]

    def get_entry(self, entry_id: str) -> dict[str, Any] | None:
        """Find a specific DLQ entry by its ID."""
        for entry in self.list_dlq(limit=self.count()):
            if entry["id"] == entry_id:
                return entry
        return None

    def replay_task(self, entry_id: str, celery_app: Any) -> str | None:
        """Re-dispatch a task from the DLQ. Returns the new task ID or None."""
        entry = self.get_entry(entry_id)
        if entry is None:
            return None

        result = celery_app.send_task(
            entry["task_name"],
            args=entry["args"],
            kwargs=entry["kwargs"],
        )
        self._remove_entry(entry_id)
        logger.info("task_replayed_from_dlq", entry_id=entry_id, new_task_id=result.id)
        return result.id

    def purge(self) -> int:
        """Delete all entries from the DLQ. Returns the count of purged entries."""
        count = self.count()
        self._redis.delete(DLQ_KEY)
        logger.info("dlq_purged", count=count)
        return count

    def count(self) -> int:
        """Return the number of entries in the DLQ."""
        return self._redis.llen(DLQ_KEY)

    def _remove_entry(self, entry_id: str) -> None:
        """Remove a specific entry from the DLQ by rebuilding the list."""
        entries = self.list_dlq(limit=self.count())
        self._redis.delete(DLQ_KEY)
        for entry in reversed(entries):
            if entry["id"] != entry_id:
                self._redis.lpush(DLQ_KEY, json.dumps(entry))
