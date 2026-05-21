import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel
from app.models.check_result import CheckStatus


class CheckResultResponse(BaseModel):
    id: uuid.UUID
    monitor_id: uuid.UUID
    status: CheckStatus
    status_code: Optional[int] = None
    response_time_ms: Optional[int] = None
    error_message: Optional[str] = None
    checked_at: datetime

    model_config = {"from_attributes": True}
