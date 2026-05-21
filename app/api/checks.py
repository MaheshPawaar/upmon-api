import uuid
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.schemas.check_result import CheckResultResponse
from app.models.check_result import CheckResult
from app.services.monitor_service import get_monitor
from app.utils.auth import get_current_user

router = APIRouter(prefix="/api/monitors/", tags=["checks"])


@router.get("/{monitor_id}/checks", response_model=list[CheckResultResponse])
def get_monitor_checks(
    monitor_id: uuid.UUID,
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    get_monitor(monitor_id, current_user, db)
    offset = (page - 1) * limit
    return (
        db.query(CheckResult)
        .filter(CheckResult.monitor_id == monitor_id)
        .order_by(CheckResult.checked_at.desc())
        .offset(offset)
        .limi(limit)
        .all()
    )


@router.get("/{monitor_id}/checks/latest", response_model=list[CheckResultResponse])
def get_latest_checks(
    monitor_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    get_monitor(monitor_id, current_user, db)
    return (
        db.query(CheckResult)
        .filter(CheckResult.monitor_id == monitor_id)
        .order_by(CheckResult.checked_at.desc())
        .limit(10)
        .all()
    )
