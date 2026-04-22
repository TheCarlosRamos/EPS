"""Celery Beat persistence via sqlalchemy-celery-beat DatabaseScheduler."""

import pytest
from celery import Celery
from sqlalchemy_celery_beat.schedulers import DatabaseScheduler

from src.queue.beat_schedules import BEAT_SCHEDULE


@pytest.fixture
def reset_sqlalchemy_celery_session_manager():
    """DatabaseScheduler uses a module-level SessionManager with a global prepared flag."""

    import sqlalchemy_celery_beat.schedulers as beat_sched

    beat_sched.session_manager.prepared = False
    beat_sched.session_manager._engines.clear()
    beat_sched.session_manager._sessions.clear()
    yield
    beat_sched.session_manager.prepared = False
    beat_sched.session_manager._engines.clear()
    beat_sched.session_manager._sessions.clear()


@pytest.mark.unit
class TestProductionCeleryBeatConfig:
    def test_app_uses_database_scheduler_and_beat_schedule(self):
        from src.core.celery_app import app

        assert app.conf.beat_scheduler == "sqlalchemy_celery_beat.schedulers:DatabaseScheduler"
        assert app.conf.beat_schedule == BEAT_SCHEDULE
        assert app.conf.beat_dburi.startswith("postgresql+psycopg://")


@pytest.mark.unit
class TestDatabaseBeatScheduler:
    def test_periodic_tasks_persist_across_scheduler_restart(self, tmp_path, reset_sqlalchemy_celery_session_manager):
        """Schedule rows live in the DB file — a new scheduler instance reloads them."""

        db_file = tmp_path / "beat.db"
        uri = f"sqlite:///{db_file}"

        def make_app() -> Celery:
            a = Celery("beat_persist_test")
            a.conf.update(
                broker_url="memory://",
                result_backend="cache+memory://",
                beat_schedule=BEAT_SCHEDULE,
                beat_dburi=uri,
            )
            return a

        first = DatabaseScheduler(app=make_app())
        first.setup_schedule()
        names_first = set(first.schedule.keys())
        assert "health-check-scrapers" in names_first
        assert "data-retention-purge" in names_first

        second = DatabaseScheduler(app=make_app())
        second.setup_schedule()
        names_second = set(second.schedule.keys())
        assert names_second == names_first
