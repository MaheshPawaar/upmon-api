from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.schemas.monitor import MonitorCreate, MonitorUpdate, MonitorResponse
from app.services.monitor_service import (
    create_monitor,
    list_monitors,
    get_monitor,
    update_monitor,
    delete_monitor,
)
from app.utils.auth import get_current_user
import uuid

router = APIRouter(prefix="/api/monitors", tags=["monitors"])


@router.post("", response_model=MonitorResponse, status_code=status.HTTP_201_CREATED)
def create(
    payload: MonitorCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return create_monitor(payload, current_user, db)


@router.get("", response_model=list[MonitorResponse])
def list_all(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    return list_monitors(current_user, db)


@router.get("/{monitor_id}", response_model=MonitorResponse)
def get_one(
    monitor_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_monitor(monitor_id, current_user, db)


@router.patch("/{monitor_id}", response_model=MonitorResponse)
def update(
    monitor_id: uuid.UUID,
    payload: MonitorUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return update_monitor(monitor_id, payload, current_user, db)


@router.delete("/{monitor_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete(
    monitor_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    delete_monitor(monitor_id, current_user, db)
