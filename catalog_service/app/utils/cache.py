import json
import logging
from typing import Optional, Any

from app.constants import CACHE_TTL
from app.utils.redis_client import redis_client
from prometheus.metrics import redis_ops

logger = logging.getLogger(__name__)


async def set_cache(key: str, value: Any, ttl: int = CACHE_TTL):
    try:
        await redis_client.setex(key, ttl, json.dumps(value))
        redis_ops.labels(operation=f"SET", status="ok").inc()
    except Exception as e:
        redis_ops.labels(operation=f"SET", status="error").inc()
        logger.error(f"{key} cache write error: {e}")


async def get_cached(key: str) -> Optional[list[dict]]:
    try:
        data = await redis_client.get(key)
        if data:
            redis_ops.labels(operation=f"GET", status="hit").inc()
            return json.loads(data)
        else:
            redis_ops.labels(operation=f"GET", status="miss").inc()
            return None

    except Exception as e:
        redis_ops.labels(operation=f"GET", status="error").inc()
        logger.error(f"{key} cache read error: {e}")
        return None


async def delete_cache(key: str):
    try:
        await redis_client.delete(key)
        redis_ops.labels(operation=f"DELETE", status="ok").inc()
    except Exception as e:
        redis_ops.labels(operation=f"DELETE", status="error").inc()
        logger.error(f"{key} cache delete error: {e}")
