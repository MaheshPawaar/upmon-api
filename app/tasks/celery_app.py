from celery import Celery
from celery.schedules import crontab
from app.config import settings

celery_app = Celery(
    "upmon",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
)

celery_app.conf.timezone = "UTC"

# Configure beat schedule
celery_app.conf.beat_schedule = {
    "dispatch-health-checks-every-minute": {
        "task": "app.tasks.dipatcher.dispatch_checks",
        "schedule": 60.0,
    },
    "cleanup-old-checks-daily": {
        "task": "app.tasks.cleanup.cleanup_old_checks",
        "schedule": crontab(hour=0, minute=0),
    },
}

celery_app.autodiscover_tasks(
    [
        "app.tasks.dispatcher",
        "app.tasks.health_check",
        "app.tasks.alerts",
        "app.tasks.cleanup",
    ],
    force=True,
)
