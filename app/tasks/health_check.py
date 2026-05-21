import logging
import time
from datetime import datetime, timezone

import httpx
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models.check_result import CheckResult, CheckStatus
from app.models.incident import Incident
from app.models.monitor import Monitor
from app.tasks.celery_app import celery_app

logger = logging.getLogger(__name__)


@celery_app.task
def run_health_check(monitor_id: str):
    db: Session = SessionLocal()
    try:
        monitor = db.query(Monitor).filter(Monitor.id == monitor_id).first()
        if not monitor:
            logger.warning(f"Monitor {monitor_id} not found, skipping")
            return

        status_code = None
        response_time_ms = None
        error_message = None
        status = CheckStatus.down

        start = time.time()
        try:
            response = httpx.get(str(monitor.url), timeout=monitor.timeout_seconds)
            response_time_ms = int((time.time() - start) * 1000)
            status_code = response.status_code
            if response.status_code == monitor.expected_status_code:
                status = CheckStatus.up
            else:
                error_message = f"Expected {monitor.expected_status_code}, got {response.status_code}"
        except httpx.TimeoutException:
            error_message = "Request timed out"
        except httpx.ConnectError:
            error_message = "Connection failed"
        except Exception as e:
            error_message = str(e)

        check = CheckResult(
            monitor_id=monitor.id,
            status=status,
            status_code=status_code,
            response_time_ms=response_time_ms,
            error_message=error_message,
            checked_at=datetime.now(timezone.utc),
        )
        db.add(check)
        db.commit()

        open_incident = (
            db.query(Incident)
            .filter(Incident.monitor_id == monitor.id, Incident.resolved_at == None)
            .first()
        )

        if status == CheckStatus.down and not open_incident:
            incident = Incident(
                monitor_id=monitor.id, started_at=datetime.now(timezone.utc)
            )
            db.add(incident)
            db.commit()
            from app.tasks.alerts import send_alert_email

            send_alert_email.delay(str(incident.id))
        elif status == CheckStatus.up and open_incident:
            open_incident.resolved_at = datetime.now(timezone.utc)
            db.commit()

        from app.utils.redis import delete_cache

        delete_cache(f"stats:{monitor.id}")
    finally:
        db.close()
