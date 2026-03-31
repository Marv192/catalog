import json
import logging
from typing import Optional, Any

from app.utils.redis_client import redis_client

CACHE_TTL = 60 * 60

logger = logging.getLogger(__name__)


async def set_cache(key: str, value: Any, ttl: int = CACHE_TTL):
    try:
        await redis_client.setex(key, ttl, json.dumps(value))
    except Exception as e:
        logger.error(f"{key} cache write error: {e}")


async def get_cached(key: str) -> Optional[list[dict]]:
    try:
        data = await redis_client.get(key)
        return json.loads(data) if data else None
    except Exception as e:
        logger.error(f"{key} cache read error: {e}")
        return None
