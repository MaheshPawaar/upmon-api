import logging
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from sqlalchemy import or_, func
from app.database import SessionLocal
from app.models.incident import Incident
from app.models.monitor import Monitor
from app.models.user import User
from app.models.alert_log import AlertLog
from app.tasks.celery_app import celery_app

logger = logging.getLogger(__name__)


@celery_app.task
def dispatch_checks():
    db = SessionLocal()

    try:
        now = datetime.now(timezone.utc)
        monitors = (
            db.query(Monitor)
            .filter(
                Monitor.is_active == True,
                or_(
                    Monitor.last_checked_at == None,
                    (now - Monitor.last_checked_at).total_seconds()
                    >= Monitor.interval_seconds,
                ),
            )
            .all()
        )

        for monitor in monitors:
            from app.tasks.health_check import run_health_check

            run_health_check.delay(str(monitor.id))

        logger.info(f"Dispatched {len(monitors)} health checks")
    finally:
        db.close()
