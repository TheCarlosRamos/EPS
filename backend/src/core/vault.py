"""HashiCorp Vault client for secret retrieval.

Falls back to environment variables when Vault is disabled or unreachable,
ensuring development environments work without a running Vault instance.
"""

from __future__ import annotations

import os
from typing import Any

import structlog

from src.core.config import VaultSettings

logger = structlog.get_logger(__name__)


class VaultClient:
    """Thin wrapper around hvac for KV-v2 secret retrieval."""

    def __init__(self, settings: VaultSettings | None = None) -> None:
        self._settings = settings or VaultSettings()
        self._client: Any | None = None
        self._initialized = False

    def _ensure_client(self) -> bool:
        """Lazily initialize the hvac client. Returns True if Vault is usable."""
        if self._initialized:
            return self._client is not None

        self._initialized = True

        if not self._settings.enabled:
            logger.info("vault_disabled", msg="Vault integration disabled, using env var fallback")
            return False

        try:
            import hvac  # noqa: PLC0415

            self._client = hvac.Client(
                url=self._settings.addr,
                token=self._settings.token,
                timeout=self._settings.timeout,
            )
            if not self._client.is_authenticated():
                logger.warning("vault_auth_failed", addr=self._settings.addr)
                self._client = None
                return False
            logger.info("vault_connected", addr=self._settings.addr)
            return True
        except Exception as exc:  # noqa: BLE001
            logger.warning("vault_connection_failed", addr=self._settings.addr, error=str(exc))
            self._client = None
            return False

    def read_secret(self, path: str, mount_point: str | None = None) -> dict[str, Any]:
        """Read a KV-v2 secret. Returns empty dict on failure."""
        if not self._ensure_client():
            return {}

        mount = mount_point or self._settings.mount_point
        try:
            response = self._client.secrets.kv.v2.read_secret_version(
                path=path,
                mount_point=mount,
            )
            return response.get("data", {}).get("data", {})
        except Exception as exc:  # noqa: BLE001
            logger.warning("vault_read_failed", path=path, error=str(exc))
            return {}

    def get_proxy_credentials(self) -> dict[str, str]:
        """Resolve proxy credentials from Vault or fall back to env vars.

        Returns dict with keys: proxy_url, proxy_username, proxy_password.
        All values may be empty strings if neither Vault nor env vars are configured.
        """
        secrets = self.read_secret(self._settings.proxy_path)
        if secrets:
            logger.info("proxy_credentials_from_vault")
            return {
                "proxy_url": secrets.get("proxy_url", ""),
                "proxy_username": secrets.get("proxy_username", ""),
                "proxy_password": secrets.get("proxy_password", ""),
            }

        logger.info("proxy_credentials_from_env")
        return {
            "proxy_url": os.environ.get("PROXY_URL", ""),
            "proxy_username": os.environ.get("PROXY_USERNAME", ""),
            "proxy_password": os.environ.get("PROXY_PASSWORD", ""),
        }
