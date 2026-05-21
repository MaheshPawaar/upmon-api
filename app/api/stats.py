import uuid
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.schemas.stats import StatsResponse
from app.services.monitor_service import get_monitor
from app.services.stats_service import get_stats
from app.utils.auth import get_current_user
from app.utils.redis import get_cache, set_cache

router = APIRouter("/api/monitors", tags=["stats"])


@router.get("/{monitor_id}/stats", response_model=StatsResponse)
def get_monitor_stats(
    monitpr_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    get_monitor(monitpr_id, current_user, db)

    cache_key = f"stats:{monitpr_id}"
    cached = get_cache(cache_key)
    if cached:
        return StatsResponse(**cached)

    stats = get_stats(monitpr_id, db)
    set_cache(cache_key, stats.model_dump(), ttl=60)
    return stats
