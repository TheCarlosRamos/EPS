"""Celery Beat periodic task schedule definitions.

health_check_scrapers: every 5 minutes
data_retention_purge: daily at 02:00
"""

from celery.schedules import crontab

BEAT_SCHEDULE = {
    "health-check-scrapers": {
        "task": "src.queue.tasks.health_check_scrapers",
        "schedule": 300.0,  # every 5 minutes
        "options": {"queue": "default"},
    },
    "data-retention-purge": {
        "task": "src.queue.tasks.data_retention_purge",
        "schedule": crontab(hour=2, minute=0),
        "options": {"queue": "default"},
    },
}
