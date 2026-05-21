import logging
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.incident import Incident
from app.models.monitor import Monitor
from app.models.user import User
from app.models.alert_log import AlertLog
from app.tasks.celery_app import celery_app

logger = logging.getLogger(__name__)


@celery_app.task
def send_alert_email(incident_id: str):
    db = SessionLocal()

    try:
        incident = db.query(Incident).filter(Incident.id == incident_id).first()
        monitor = db.query(Monitor).filter(Monitor.id == incident.monitor_id).first()
        user = db.query(User).filter(User.id == monitor.user_id).first()
        logger.info(
            f"ALERT: {monitor.name} is DOWN since {incident.started_at}, notifying {user.email}"
        )

        alertLog = AlertLog(
            incident_id=incident.id,
            channel="email",
            sent_at=datetime.now(timezone.utc),
            status="sent",
        )
        db.add(alertLog)
        db.commit()
    finally:
        db.close()
