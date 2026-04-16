"""Base scraper task with retry logic, audit logging, and DLQ integration."""

from __future__ import annotations

import time
from typing import Any

import structlog
from celery import Task

from src.queue.retry import MAX_RETRIES, get_retry_delay

logger = structlog.get_logger(__name__)


class BaseScraperTask(Task):
    """Abstract base task for all scraper operations.

    Features:
    - Exponential backoff retry: 60s / 300s / 900s (max 3 retries)
    - Structured audit logging on start and completion
    - Dead letter queue integration on final failure
    """

    abstract = True
    max_retries = MAX_RETRIES
    acks_late = True

    _start_time: float | None = None

    def before_start(self, task_id: str, args: tuple, kwargs: dict) -> None:
        """Log task start for audit trail."""
        self._start_time = time.monotonic()
        logger.info(
            "task_started",
            task_name=self.name,
            task_id=task_id,
            args=args,
            kwargs=kwargs,
        )

    def after_return(self, status: str, retval: Any, task_id: str, args: tuple, kwargs: dict, einfo: Any) -> None:
        """Log task completion for audit trail."""
        elapsed = time.monotonic() - self._start_time if self._start_time else 0.0
        logger.info(
            "task_completed",
            task_name=self.name,
            task_id=task_id,
            status=status,
            elapsed_seconds=round(elapsed, 3),
        )

    def on_retry(self, exc: Exception, task_id: str, args: tuple, kwargs: dict, einfo: Any) -> None:
        """Log retry attempt."""
        logger.warning(
            "task_retry",
            task_name=self.name,
            task_id=task_id,
            retry_count=self.request.retries,
            exception=str(exc),
        )

    def on_failure(self, exc: Exception, task_id: str, args: tuple, kwargs: dict, einfo: Any) -> None:
        """Log failure and send to DLQ if retries exhausted."""
        logger.error(
            "task_failed",
            task_name=self.name,
            task_id=task_id,
            exception=str(exc),
            retries_exhausted=self.request.retries >= self.max_retries,
        )

    def retry_with_backoff(self, exc: Exception, **kwargs: Any) -> None:
        """Retry the task with exponential backoff delay."""
        delay = get_retry_delay(self.request.retries)
        self.retry(exc=exc, countdown=delay, **kwargs)
