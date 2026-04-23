"""Integration tests for Celery Beat schedule configuration."""

import pytest
from celery.schedules import crontab
from src.queue.beat_schedules import BEAT_SCHEDULE


@pytest.mark.integration
class TestBeatScheduleIntegration:
    def test_health_check_schedule_exists(self):
        assert "health-check-scrapers" in BEAT_SCHEDULE

    def test_health_check_interval(self):
        entry = BEAT_SCHEDULE["health-check-scrapers"]
        assert entry["schedule"].run_every.total_seconds() == 300

    def test_retention_purge_schedule_exists(self):
        assert "data-retention-purge" in BEAT_SCHEDULE

    def test_retention_purge_is_daily(self):
        entry = BEAT_SCHEDULE["data-retention-purge"]
        schedule = entry["schedule"]
        assert isinstance(schedule, crontab)

    def test_all_tasks_have_queue(self):
        for name, entry in BEAT_SCHEDULE.items():
            assert "options" in entry, f"{name} missing options"
            assert "queue" in entry["options"], f"{name} missing queue option"
