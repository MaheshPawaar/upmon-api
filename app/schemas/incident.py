import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class IncidentResponse(BaseModel):
    id: uuid.UUID
    monitor_id: uuid.UUID
    started_at: datetime
    resolved_at: Optional[datetime] = None
    root_cause: Optional[str] = None
    model_config = {"from_attributes": True}
