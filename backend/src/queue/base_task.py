"""Base scraper task with retry logic, audit logging, and Vault integration."""

from __future__ import annotations

import time
from typing import Any

import structlog
from celery import Task

from src.core.vault import VaultClient
from src.queue.retry import MAX_RETRIES, get_retry_delay

logger = structlog.get_logger(__name__)

# Module-level singleton — shared across all task instances in the worker process.
_vault_client: VaultClient | None = None


def _get_vault_client() -> VaultClient:
    """Return the module-level VaultClient singleton."""
    global _vault_client  # noqa: PLW0603
    if _vault_client is None:
        _vault_client = VaultClient()
    return _vault_client


class BaseScraperTask(Task):
    """Abstract base task for all scraper operations.

    Features:
    - Exponential backoff retry: 60s / 300s / 900s (max 3 retries)
    - Structured audit logging on start and completion
    - Pre-execution hook: resolves proxy credentials from Vault (or env vars)
    - Dead letter queue integration on final failure
    """

    abstract = True
    max_retries = MAX_RETRIES
    acks_late = True

    _start_time: float | None = None
    _proxy_credentials: dict[str, str] | None = None

    def before_start(self, task_id: str, args: tuple, kwargs: dict) -> None:
        """Log task start and resolve proxy credentials for audit trail."""
        self._start_time = time.monotonic()

        vault = _get_vault_client()
        self._proxy_credentials = vault.get_proxy_credentials()

        logger.info(
            "task_started",
            task_name=self.name,
            task_id=task_id,
            args=args,
            kwargs=kwargs,
            proxy_configured=bool(self._proxy_credentials.get("proxy_url")),
        )

    @property
    def proxy_credentials(self) -> dict[str, str]:
        """Proxy credentials resolved during before_start(). Empty dict if not yet resolved."""
        return self._proxy_credentials or {}

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
