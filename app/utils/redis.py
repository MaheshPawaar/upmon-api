import json
import redis
from app.config import settings

_client = redis.from_url(settings.REDIS_URL, decode_responses=True)


def get_cache(key: str):
    value = _client.get(key)
    if value is None:
        return None
    return json.loads(value)


def set_cache(key: str, value: dict, ttl: int = 60):
    _client.setex(key, ttl, json.dumps(value))


def delete_cache(key: str):
    _client.delete(key)
