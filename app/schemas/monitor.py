from pydantic import BaseModel, HttpUrl
from typing import Optional
from datetime import datetime
import uuid


class MonitorCreate(BaseModel):
    name: str
    url: HttpUrl
    interval_seconds: int = 60
    timeout_seconds: int = 10
    expected_status_code: int = 200


class MonitorUpdate(BaseModel):
    name: Optional[str] = None
    url: Optional[HttpUrl] = None
    interval_seconds: Optional[int] = None
    timeout_seconds: Optional[int] = None
    expected_status_code: Optional[int] = None
    is_active: Optional[bool] = None


class MonitorResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    name: str
    url: str
    interval_seconds: int
    timeout_seconds: int
    expected_status_code: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
