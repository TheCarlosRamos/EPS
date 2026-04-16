"""Unit tests for Vault client and settings."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from src.core.config import VaultSettings
from src.core.vault import VaultClient


@pytest.mark.unit
class TestVaultSettings:
    def test_defaults(self, monkeypatch):
        monkeypatch.delenv("VAULT_ENABLED", raising=False)
        monkeypatch.delenv("VAULT_TOKEN", raising=False)
        settings = VaultSettings()
        assert settings.enabled is False
        assert settings.addr == "http://localhost:8200"
        assert settings.token == ""
        assert settings.mount_point == "secret"
        assert settings.proxy_path == "osint/proxy"
        assert settings.timeout == 5

    def test_disabled_by_default(self, monkeypatch):
        monkeypatch.delenv("VAULT_ENABLED", raising=False)
        settings = VaultSettings()
        assert settings.enabled is False

    def test_from_env(self, monkeypatch):
        monkeypatch.setenv("VAULT_ENABLED", "true")
        monkeypatch.setenv("VAULT_ADDR", "http://vault.internal:8200")
        monkeypatch.setenv("VAULT_TOKEN", "s.test-token")
        monkeypatch.setenv("VAULT_MOUNT_POINT", "kv")
        monkeypatch.setenv("VAULT_PROXY_PATH", "infra/proxy")
        monkeypatch.setenv("VAULT_TIMEOUT", "10")
        settings = VaultSettings()
        assert settings.enabled is True
        assert settings.addr == "http://vault.internal:8200"
        assert settings.token == "s.test-token"
        assert settings.mount_point == "kv"
        assert settings.proxy_path == "infra/proxy"
        assert settings.timeout == 10


@pytest.mark.unit
class TestVaultClientDisabled:
    def test_read_secret_returns_empty(self):
        client = VaultClient(VaultSettings(enabled=False))
        assert client.read_secret("any/path") == {}

    def test_get_proxy_credentials_falls_back_to_env(self, monkeypatch):
        monkeypatch.setenv("PROXY_URL", "http://proxy.test:8080")
        monkeypatch.setenv("PROXY_USERNAME", "user1")
        monkeypatch.setenv("PROXY_PASSWORD", "pass1")
        client = VaultClient(VaultSettings(enabled=False))
        creds = client.get_proxy_credentials()
        assert creds["proxy_url"] == "http://proxy.test:8080"
        assert creds["proxy_username"] == "user1"
        assert creds["proxy_password"] == "pass1"

    def test_get_proxy_credentials_empty_when_no_env(self, monkeypatch):
        monkeypatch.delenv("PROXY_URL", raising=False)
        monkeypatch.delenv("PROXY_USERNAME", raising=False)
        monkeypatch.delenv("PROXY_PASSWORD", raising=False)
        client = VaultClient(VaultSettings(enabled=False))
        creds = client.get_proxy_credentials()
        assert creds["proxy_url"] == ""
        assert creds["proxy_username"] == ""
        assert creds["proxy_password"] == ""


@pytest.mark.unit
class TestVaultClientEnabled:
    def _make_mock_hvac(self, authenticated=True, secret_data=None):
        mock_hvac_module = MagicMock()
        mock_client_instance = MagicMock()
        mock_client_instance.is_authenticated.return_value = authenticated
        if secret_data is not None:
            mock_client_instance.secrets.kv.v2.read_secret_version.return_value = {"data": {"data": secret_data}}
        mock_hvac_module.Client.return_value = mock_client_instance
        return mock_hvac_module, mock_client_instance

    def test_reads_secret_from_vault(self):
        mock_hvac, mock_instance = self._make_mock_hvac(
            secret_data={"proxy_url": "http://proxy:8080", "proxy_username": "u", "proxy_password": "p"}
        )
        settings = VaultSettings(enabled=True, addr="http://vault:8200", token="test-token")
        client = VaultClient(settings)
        with patch.dict("sys.modules", {"hvac": mock_hvac}):
            creds = client.get_proxy_credentials()
        assert creds["proxy_url"] == "http://proxy:8080"
        assert creds["proxy_username"] == "u"
        assert creds["proxy_password"] == "p"

    def test_auth_failure_falls_back_to_env(self, monkeypatch):
        monkeypatch.setenv("PROXY_URL", "http://fallback:8080")
        mock_hvac, _ = self._make_mock_hvac(authenticated=False)
        settings = VaultSettings(enabled=True, addr="http://vault:8200", token="bad-token")
        client = VaultClient(settings)
        with patch.dict("sys.modules", {"hvac": mock_hvac}):
            creds = client.get_proxy_credentials()
        assert creds["proxy_url"] == "http://fallback:8080"

    def test_connection_error_falls_back_to_env(self, monkeypatch):
        monkeypatch.setenv("PROXY_URL", "http://fallback:8080")
        mock_hvac = MagicMock()
        mock_hvac.Client.side_effect = ConnectionError("unreachable")
        settings = VaultSettings(enabled=True, addr="http://unreachable:9999", token="t", timeout=1)
        client = VaultClient(settings)
        with patch.dict("sys.modules", {"hvac": mock_hvac}):
            creds = client.get_proxy_credentials()
        assert creds["proxy_url"] == "http://fallback:8080"

    def test_read_exception_returns_empty(self):
        mock_hvac, mock_instance = self._make_mock_hvac(authenticated=True)
        mock_instance.secrets.kv.v2.read_secret_version.side_effect = Exception("read error")
        settings = VaultSettings(enabled=True, addr="http://vault:8200", token="test-token")
        client = VaultClient(settings)
        with patch.dict("sys.modules", {"hvac": mock_hvac}):
            result = client.read_secret("some/path")
        assert result == {}

    def test_ensure_client_caches_result(self):
        mock_hvac, _ = self._make_mock_hvac(authenticated=True)
        settings = VaultSettings(enabled=True, addr="http://vault:8200", token="t")
        client = VaultClient(settings)
        with patch.dict("sys.modules", {"hvac": mock_hvac}):
            assert client._ensure_client() is True
            assert client._ensure_client() is True
        # Client constructor called only once
        mock_hvac.Client.assert_called_once()


@pytest.mark.unit
class TestBaseScraperTaskVaultIntegration:
    def test_before_start_resolves_proxy_credentials(self, celery_app):
        from src.queue import base_task

        mock_vault = MagicMock()
        mock_vault.get_proxy_credentials.return_value = {
            "proxy_url": "http://proxy:8080",
            "proxy_username": "u",
            "proxy_password": "p",
        }

        original = base_task._vault_client
        base_task._vault_client = mock_vault
        try:

            @celery_app.task(base=base_task.BaseScraperTask, bind=True, name="test.vault_task")
            def vault_task(self):
                return self.proxy_credentials

            result = vault_task.apply()
            creds = result.get()
            assert creds["proxy_url"] == "http://proxy:8080"
        finally:
            base_task._vault_client = original

    def test_proxy_credentials_empty_before_start(self):
        from src.queue.base_task import BaseScraperTask

        task = BaseScraperTask()
        assert task.proxy_credentials == {}
