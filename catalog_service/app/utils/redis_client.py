import os

import redis.asyncio as redis

REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
REDIS_PORT = os.getenv('REDIS_PORT', '6379')
REDIS_URL = f"redis://{REDIS_HOST}:{REDIS_PORT}"

redis_client = redis.from_url(REDIS_URL, decode_responses=True)
