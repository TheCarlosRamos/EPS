"""Integration tests for Vault client with a real Vault instance.

Requires: docker compose up vault -d
Auto-skips if Vault is not available.
"""

from __future__ import annotations

import os

import pytest

from src.core.config import VaultSettings
from src.core.vault import VaultClient


def _vault_settings() -> VaultSettings:
    return VaultSettings(
        enabled=True,
        addr=os.getenv("VAULT_ADDR", "http://localhost:8200"),
        token=os.getenv("VAULT_TOKEN", "dev-only-token"),
    )


@pytest.fixture
def vault_client():
    """Real Vault connection. Skips if Vault is not running."""
    settings = _vault_settings()
    client = VaultClient(settings)
    if not client._ensure_client():
        pytest.skip("Vault not available — start with: docker compose up vault -d")
    return client


@pytest.fixture
def hvac_client():
    """Raw hvac client for test setup (writing secrets)."""
    settings = _vault_settings()
    try:
        import hvac

        client = hvac.Client(url=settings.addr, token=settings.token)
        if not client.is_authenticated():
            pytest.skip("Vault not authenticated")
        return client
    except Exception:  # noqa: BLE001
        pytest.skip("Vault not available")


@pytest.mark.integration
class TestVaultIntegration:
    def test_write_and_read_secret(self, vault_client, hvac_client):
        hvac_client.secrets.kv.v2.create_or_update_secret(
            path="test/integration",
            secret={"key": "value123"},
            mount_point="secret",
        )
        result = vault_client.read_secret("test/integration")
        assert result["key"] == "value123"

    def test_get_proxy_credentials_from_vault(self, vault_client, hvac_client):
        hvac_client.secrets.kv.v2.create_or_update_secret(
            path="osint/proxy",
            secret={
                "proxy_url": "http://test-proxy:8080",
                "proxy_username": "test_user",
                "proxy_password": "test_pass",
            },
            mount_point="secret",
        )
        creds = vault_client.get_proxy_credentials()
        assert creds["proxy_url"] == "http://test-proxy:8080"
        assert creds["proxy_username"] == "test_user"
        assert creds["proxy_password"] == "test_pass"

    def test_nonexistent_path_returns_empty(self, vault_client):
        result = vault_client.read_secret("nonexistent/path/that/does/not/exist")
        assert result == {}
