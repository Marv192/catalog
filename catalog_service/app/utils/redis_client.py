import redis.asyncio as redis

from app.config import settings

REDIS_URL = f"redis://{settings.redis_host}:{settings.redis_port}"

redis_client = redis.from_url(REDIS_URL, decode_responses=True)
