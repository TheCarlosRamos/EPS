"""Application configuration via Pydantic Settings.

All secrets are loaded from environment variables — never hardcoded.
"""

from pydantic_settings import BaseSettings


class RedisSettings(BaseSettings):
    """Redis connection settings."""

    model_config = {"env_prefix": "REDIS_"}

    host: str = "localhost"
    port: int = 6379
    db: int = 0
    password: str = ""
    max_memory: str = "512mb"

    @property
    def url(self) -> str:
        """Build the Redis connection URL."""
        if self.password:
            return f"redis://:{self.password}@{self.host}:{self.port}/{self.db}"
        return f"redis://{self.host}:{self.port}/{self.db}"


class VaultSettings(BaseSettings):
    """HashiCorp Vault connection settings.

    When enabled=False (default), secrets fall back to environment variables.
    This allows development without a Vault instance.
    """

    model_config = {"env_prefix": "VAULT_"}

    enabled: bool = False
    addr: str = "http://localhost:8200"
    token: str = ""
    mount_point: str = "secret"
    proxy_path: str = "osint/proxy"
    timeout: int = 5


class CelerySettings(BaseSettings):
    """Celery application settings."""

    model_config = {"env_prefix": "CELERY_"}

    broker_url: str = "redis://localhost:6379/0"
    result_backend: str = "redis://localhost:6379/0"
    task_serializer: str = "json"
    result_serializer: str = "json"
    accept_content: list[str] = ["json"]
    task_track_started: bool = True
    worker_hijack_root_logger: bool = False
    task_default_queue: str = "default"
