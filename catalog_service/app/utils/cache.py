import json
import logging
import time
from typing import Optional, Any

from app.constants import CACHE_TTL
from app.utils.redis_client import redis_client
from app.observability.metrics import redis_ops, redis_latency

logger = logging.getLogger(__name__)


async def set_cache(key: str, value: Any, ttl: int = CACHE_TTL):
    latency_start = time.perf_counter()
    try:
        await redis_client.setex(key, ttl, json.dumps(value))
        redis_ops.labels(operation=f"SET", status="ok").inc()
        logger.info("Set cache OK", extra={"key": key})

    except Exception as e:
        redis_ops.labels(operation=f"SET", status="error").inc()
        logger.exception("Cache write error", extra={"key": key, "error_type": type(e).__name__})

    finally:
        redis_latency.labels(operation=f"SET").observe(time.perf_counter() - latency_start)

async def get_cached(key: str) -> Optional[list[dict]]:
    latency_start = time.perf_counter()
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
        logger.exception("Cache read error", extra={"key": key, "error_type": type(e).__name__})
        return None

    finally:
        redis_latency.labels(operation=f"GET").observe(time.perf_counter() - latency_start)


async def delete_cache(key: str):
    latency_start = time.perf_counter()
    try:
        await redis_client.delete(key)
        redis_ops.labels(operation=f"DELETE", status="ok").inc()
        logger.info("Delete cache OK", extra={"key": key})

    except Exception as e:
        redis_ops.labels(operation=f"DELETE", status="error").inc()
        logger.exception("Cache delete error", extra={"key": key, "error_type": type(e).__name__})

    finally:
        redis_latency.labels(operation=f"DELETE").observe(time.perf_counter() - latency_start)
