"""Celery Beat periodic task schedule definitions.

health_check_scrapers: every 5 minutes
data_retention_purge: daily at 02:00

Schedules use Celery ``schedule`` / ``crontab`` objects so they can be stored by
``sqlalchemy-celery-beat`` (DatabaseScheduler) in PostgreSQL.
"""

from celery.schedules import crontab, schedule as interval_schedule

BEAT_SCHEDULE = {
    "health-check-scrapers": {
        "task": "src.queue.tasks.health_check_scrapers",
        "schedule": interval_schedule(run_every=300.0),
        "options": {"queue": "default"},
    },
    "data-retention-purge": {
        "task": "src.queue.tasks.data_retention_purge",
        "schedule": crontab(hour=2, minute=0),
        "options": {"queue": "default"},
    },
}
