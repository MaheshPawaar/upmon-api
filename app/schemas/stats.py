from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class StatsResponse(BaseModel):
    uptime_percentage_24h: Optional[float] = None
    uptime_percentage_7d: Optional[float] = None
    uptime_percentage_30d: Optional[float] = None
    avg_response_time_24h: Optional[float] = None
    avg_response_time_7d: Optional[float] = None
    p95_response_time_24h: Optional[float] = None
    total_checks_24h: int = 0
    total_incidents_30d: int = 0
    current_status: Optional[str] = None
    last_checked_at: Optional[datetime] = None

    model_config = {"from_attributes": True}
