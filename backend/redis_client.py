import redis
import os

redis_client = redis.Redis(
    host=os.getenv("REDIS_HOST", "localhost"),
    port=int(os.getenv("REDIS_PORT", "6379")),
    db=0,
    decode_responses=True
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
