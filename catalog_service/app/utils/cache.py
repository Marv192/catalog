import json
from typing import Optional, Any

from app.utils.redis_client import redis_client


async def set_cache(key: str, value: Any, ttl: int = 60 * 60):
    try:
        await redis_client.setex(key, ttl, json.dumps(value))
    except Exception as e:
        print(f"{key} cache write error: {e}")

async def get_cached(key: str) -> Optional[list[dict]]:
    try:
        data = await redis_client.get(key)
        return json.loads(data) if data else None
    except Exception as e:
        print(f"{key} cache read error: {e}")
        return None
