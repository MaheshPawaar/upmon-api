import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy import func, text
from sqlalchemy.orm import Session

from app.models.check_result import CheckResult, CheckStatus
from app.models.incident import Incident
from app.schemas.stats import StatsResponse


def get_stats(monitor_id: uuid.UUID, db: Session) -> StatsResponse:
    now = datetime.now(timezone.utc)
    since_24h = now - timedelta(hours=24)
    since_7d = now - timedelta(days=7)
    since_30d = now - timedelta(days=30)

    def uptime_percentage(since):
        total = (
            db.query(func.count(CheckResult.id))
            .filter(
                CheckResult.monitor_id == monitor_id,
                CheckResult.checked_at >= since,
            )
            .scalar()
        )

        if not total:
            return None

        up = (
            db.query(func.count(CheckResult.id))
            .filter(
                CheckResult.monitor_id == monitor_id,
                CheckResult.checked_at >= since,
                CheckResult.status == CheckStatus.up,
            )
            .scalar()
        )
        return round((up / total) * 100, 2)

    def avg_response(since):
        return (
            db.query(func.avg(CheckResult.response_time_ms))
            .filter(
                CheckResult.monitor_id == monitor_id,
                CheckResult.checked_at >= since,
                CheckResult.status == CheckStatus.up,
            )
            .scalar()
        )

    p95 = db.execute(
        text("""
                          SELECT percentile_cont(0.95) WITHIN GROUP (ORDER BY response_time_ms)
                          FROM check_results
                          WHERE monitor_id = :monitor_id
                          AND checked_at >= :since
                          AND status = 'up'
                          AND response_time_ms IS NOT NULL                         
                      """),
        {"monitor_id": str(monitor_id), "since": since_24h},
    ).scalar()

    total_checks_24h = (
        db.query(func.count(CheckResult.id))
        .filter(
            CheckResult.monitor_id == monitor_id,
            CheckResult.checked_at >= since_24h,
        )
        .scalar()
    )

    total_incidents_30d = (
        db.query(func.count(Incident.id))
        .filter(
            Incident.monitor_id == monitor_id,
            Incident.started_at >= since_30d,
        )
        .scalar()
    )

    latest = (
        db.query(CheckResult)
        .filter(CheckResult.monitor_id == monitor_id)
        .order_by(CheckResult.checked_at.desc())
        .first()
    )

    return StatsResponse(
        uptime_percentage_24h=uptime_percentage(since_24h),
        uptime_percentage_7d=uptime_percentage(since_7d),
        uptime_percentage_30d=uptime_percentage(since_30d),
        avg_response_time_24h=avg_response(since_24h),
        avg_response_time_7d=avg_response(since_7d),
        p95_response_time_24h=p95,
        total_checks_24h=total_checks_24h or 0,
        total_incidents_30d=total_incidents_30d or 0,
        current_status=latest.status.value if latest else None,
        last_checked_at=latest.checked_at if latest else None,
    )
