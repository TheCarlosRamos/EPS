"""Celery application instance and configuration.

Usage from repo root:
    celery -A backend.src.core.celery_app worker --loglevel=info
    celery -A backend.src.core.celery_app beat --loglevel=info
"""

from celery import Celery

from src.core.config import CelerySettings, get_beat_database_url
from src.queue.beat_schedules import BEAT_SCHEDULE

settings = CelerySettings()

app = Celery("buscador_osint")

beat_conf = {
    "beat_schedule": BEAT_SCHEDULE,
    "beat_dburi": get_beat_database_url(settings),
    "beat_scheduler": "sqlalchemy_celery_beat.schedulers:DatabaseScheduler",
}
if settings.beat_schema is not None:
    beat_conf["beat_schema"] = settings.beat_schema

app.conf.update(
    broker_url=settings.broker_url,
    result_backend=settings.result_backend,
    task_serializer=settings.task_serializer,
    result_serializer=settings.result_serializer,
    accept_content=settings.accept_content,
    task_track_started=settings.task_track_started,
    worker_hijack_root_logger=settings.worker_hijack_root_logger,
    task_default_queue=settings.task_default_queue,
    task_routes={
        "src.queue.*scraper*": {"queue": "scrapers"},
        "src.queue.*evidence*": {"queue": "evidence"},
    },
    **beat_conf,
)

app.autodiscover_tasks(["src.queue"])
