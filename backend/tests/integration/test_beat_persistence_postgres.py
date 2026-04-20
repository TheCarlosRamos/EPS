"""Integration test: Celery Beat schedule persists across restarts (PostgreSQL).

This validates the acceptance criterion:
  - Celery Beat persists schedule across restarts

It uses sqlalchemy-celery-beat's DatabaseScheduler with a real PostgreSQL DB.
"""

from __future__ import annotations

import os
import uuid

import pytest
from celery import Celery
from sqlalchemy import text
from sqlalchemy_celery_beat.schedulers import DatabaseScheduler

from src.queue.beat_schedules import BEAT_SCHEDULE


def _postgres_dburi() -> str | None:
    return os.getenv("CELERY_BEAT_DBURI") or os.getenv("BEAT_DBURI") or os.getenv("POSTGRES_BEAT_DBURI")


@pytest.mark.integration
class TestBeatPersistencePostgres:
    def test_schedule_persists_across_scheduler_restart(self):
        dburi = _postgres_dburi()
        if not dburi:
            pytest.skip("PostgreSQL DBURI not set (set CELERY_BEAT_DBURI)")

        schema = f"beat_{uuid.uuid4().hex[:12]}"

        def make_app() -> Celery:
            app = Celery("beat_persist_postgres_test")
            app.conf.update(
                broker_url="memory://",
                result_backend="cache+memory://",
                beat_schedule=BEAT_SCHEDULE,
                beat_dburi=dburi,
                beat_schema=schema,
                beat_scheduler="sqlalchemy_celery_beat.schedulers:DatabaseScheduler",
            )
            return app

        # First "boot": scheduler creates tables + persists beat_schedule into DB.
        first = DatabaseScheduler(app=make_app())
        first.setup_schedule()
        names_first = set(first.schedule.keys())
        assert "health-check-scrapers" in names_first
        assert "data-retention-purge" in names_first

        # Simulated restart: new scheduler instance must reload from DB.
        second = DatabaseScheduler(app=make_app())
        second.setup_schedule()
        names_second = set(second.schedule.keys())
        assert names_second == names_first

        # Cleanup: drop the dedicated schema to keep DB tidy.
        with second.engine.begin() as conn:
            conn.execute(text(f'DROP SCHEMA IF EXISTS "{schema}" CASCADE'))
