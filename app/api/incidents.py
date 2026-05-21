import uuid
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.models.incident import Incident
from app.schemas.incident import IncidentResponse
from app.services.monitor_service import get_monitor
from app.utils.auth import get_current_user

router = APIRouter("/api/monitors", tags=["incidents"])


@router.get("/{monitor_id}/incidents", response_model=list[IncidentResponse])
def get_monitor_incidents(
    monitor_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    get_monitor(monitor_id, current_user, db)
    return (
        db.query(Incident)
        .filter(Incident.monitor_id == monitor_id)
        .order_by(Incident.started_at.desc())
        .all()
    )
