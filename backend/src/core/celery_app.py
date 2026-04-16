"""Celery application instance and configuration.

Usage from repo root:
    celery -A backend.src.core.celery_app worker --loglevel=info
"""

from celery import Celery

from src.core.config import CelerySettings

settings = CelerySettings()

app = Celery("buscador_osint")

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
)

app.autodiscover_tasks(["src.queue"])
