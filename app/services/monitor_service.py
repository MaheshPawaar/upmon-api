from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.monitor import Monitor
from app.models.user import User
from app.schemas.monitor import MonitorCreate, MonitorUpdate
import uuid


def create_monitor(payload: MonitorCreate, user: User, db: Session) -> Monitor:
    monitor = Monitor(
        user_id=user.id,
        name=payload.name,
        url=str(payload.url),
        interval_seconds=payload.interval_seconds,
        timeout_seconds=payload.timeout_seconds,
        expected_status_code=payload.expected_status_code,
    )
    db.add(monitor)
    db.commit()
    db.refresh(monitor)
    return monitor


def list_monitors(user: User, db: Session) -> list[Monitor]:
    return db.query(Monitor).filter(Monitor.user_id == user.id).all()


def get_monitor(monitor_id: uuid.UUID, user: User, db: Session) -> Monitor:
    monitor = db.query(Monitor).filter(Monitor.id == monitor_id).first()

    if not monitor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Monitor not found"
        )

    if monitor.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Access denied"
        )
    return monitor


def update_monitor(
    monitor_id: uuid.UUID, payload: MonitorUpdate, user: User, db: Session
) -> Monitor:
    monitor = get_monitor(monitor_id, user, db)

    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(monitor, field, str(value) if field == "url" else value)

    db.commit()
    db.refresh(monitor)
    return monitor


def delete_monitor(monitor_id: uuid.UUID, user: User, db: Session) -> None:
    monitor = get_monitor(monitor_id, user, db)
    db.delete(monitor)
    db.commit()
