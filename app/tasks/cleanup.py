import logging
from datetime import datetime, timedelta, timezone
from app.database import SessionLocal
from app.models.check_result import CheckResult
from app.tasks.celery_app import celery_app

logger = logging.getLogger(__name__)


@celery_app.task
def cleanup_old_checks():
    db = SessionLocal()
    try:
        # calculate the cut off to clear the CheckResult records (30 days ago)
        cutoff = datetime.now(timezone.utc) - timedelta(days=30)

        deleted_count = (
            db.query(CheckResult)
            .filter(CheckResult.checked_at < cutoff)
            .delete(synchronize_session=False)
        )

        db.commit()
        logger.info(
            f"Successfully cleaned up {deleted_count} check results older than 30 days"
        )
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to clean up old check results: {e}")
        raise e
    finally:
        db.close()
