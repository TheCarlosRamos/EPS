"""Shared test fixtures and marker registration."""

import pytest


def pytest_configure(config: pytest.Config) -> None:
    """Register custom markers."""
    config.addinivalue_line("markers", "unit: Unit tests (no external services)")
    config.addinivalue_line("markers", "integration: Integration tests (requires Redis)")
