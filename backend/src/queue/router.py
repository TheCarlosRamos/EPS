"""FastAPI admin endpoints for Dead Letter Queue management.

Endpoints:
    GET    /api/admin/dlq              — List DLQ entries (paginated)
    POST   /api/admin/dlq/{id}/replay  — Replay a failed task
    DELETE /api/admin/dlq              — Purge all DLQ entries
"""

from __future__ import annotations

from typing import Any

import redis as redis_lib
from fastapi import APIRouter, HTTPException, Query

from src.queue.dlq import DLQManager

router = APIRouter(prefix="/api/admin/dlq", tags=["admin", "dlq"])


def _get_dlq_manager() -> DLQManager:
    """Create a DLQManager with a Redis connection.

    In production, this would use dependency injection via FastAPI Depends().
    """
    client = redis_lib.from_url("redis://localhost:6379/0", decode_responses=True)
    return DLQManager(client)


@router.get("")
def list_dlq(
    limit: int = Query(default=100, ge=1, le=1000),
    offset: int = Query(default=0, ge=0),
) -> dict[str, Any]:
    """List dead letter queue entries."""
    manager = _get_dlq_manager()
    entries = manager.list_dlq(limit=limit, offset=offset)
    return {
        "count": manager.count(),
        "entries": entries,
    }


@router.post("/{entry_id}/replay")
def replay_dlq_entry(entry_id: str) -> dict[str, str]:
    """Replay a specific task from the DLQ."""
    from src.core.celery_app import app

    manager = _get_dlq_manager()
    new_task_id = manager.replay_task(entry_id, celery_app=app)
    if new_task_id is None:
        raise HTTPException(status_code=404, detail=f"DLQ entry {entry_id} not found")
    return {"status": "replayed", "new_task_id": new_task_id}


@router.delete("")
def purge_dlq() -> dict[str, Any]:
    """Purge all entries from the dead letter queue."""
    manager = _get_dlq_manager()
    count = manager.purge()
    return {"status": "purged", "count": count}
