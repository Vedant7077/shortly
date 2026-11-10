
import os
import redis

REDIS_URL = os.getenv("REDIS_URL")

if REDIS_URL:
    # Production: hosted Redis (Upstash)
    redis_client = redis.Redis.from_url(
        REDIS_URL,
        decode_responses=True,
        socket_connect_timeout=10,
        socket_timeout=10,
        health_check_interval=30,
    )
else:
    # Local development: Docker Redis
    redis_client = redis.Redis(
        host=os.getenv("REDIS_HOST", "localhost"),
        port=int(os.getenv("REDIS_PORT", "6379")),
        db=0,
        decode_responses=True,
        socket_connect_timeout=10,
        socket_timeout=10,
        health_check_interval=30,
    )


RECORD_CLICK_SCRIPT = """
local count = redis.call('INCR', KEYS[1])
redis.call('SADD', KEYS[2], ARGV[1])
return count
"""


def record_click(short_code: str):
    return redis_client.eval(
        RECORD_CLICK_SCRIPT,
        2,
        f"clicks:{short_code}",
        "clicks:active_codes",
        short_code
    )
