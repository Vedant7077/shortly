
import json
import uuid

from redis_client import redis_client
from database import SessionLocal
from batch_processor import process_click_batch


PENDING_BATCH_KEY = "clicks:pending_batch"
WORKER_LOCK_KEY = "clicks:worker_lock"
LOCK_TIMEOUT = 30


def acquire_worker_lock():
    token = str(uuid.uuid4())

    acquired = redis_client.set(
        WORKER_LOCK_KEY,
        token,
        nx=True,
        ex=LOCK_TIMEOUT
    )

    if acquired:
        return token

    return None


def release_worker_lock(token: str):
    lua_script = """
    if redis.call('GET', KEYS[1]) == ARGV[1] then
        return redis.call('DEL', KEYS[1])
    end

    return 0
    """

    return bool(
        redis_client.eval(
            lua_script,
            1,
            WORKER_LOCK_KEY,
            token
        )
    )



def collect_clicks():
    """
    Atomically collect Redis click counters into a pending batch.
    """


    lua_script = """
    local pending = redis.call('GET', KEYS[1])

    if pending then
        return pending
    end

    local codes = redis.call('SMEMBERS', KEYS[2])
    local clicks = {}

    for _, code in ipairs(codes) do
        local counter_key = 'clicks:' .. code
        local value = redis.call('GET', counter_key)

        if value then
            clicks[code] = tonumber(value)
            redis.call('DEL', counter_key)
        end

        redis.call('SREM', KEYS[2], code)
    end

    if next(clicks) == nil then
        return nil
    end

    local batch = {
        batch_id = ARGV[1],
        clicks = clicks
    }

    local encoded = cjson.encode(batch)
    redis.call('SET', KEYS[1], encoded)

    return encoded
    """

    batch_id = str(uuid.uuid4())

    result = redis_client.eval(
        lua_script,
        2,
        PENDING_BATCH_KEY,
        "clicks:active_codes",
        batch_id
    )

    if result is None:
        return None

    return json.loads(result)




def process_pending_batch():
    token = acquire_worker_lock()

    if not token:
        return {
            "message": "Another worker is processing",
            "processed": False
        }

    try:
        raw_batch = redis_client.get(PENDING_BATCH_KEY)

        if raw_batch is None:
            return {
                "message": "No pending batch",
                "processed": False
            }

        batch = json.loads(raw_batch)

        batch_id = batch["batch_id"]
        clicks_by_code = batch["clicks"]

        with SessionLocal() as db:
            processed = process_click_batch(
                db,
                batch_id,
                clicks_by_code
            )

        acknowledged = acknowledge_pending_batch(raw_batch)

        return {
            "batch_id": batch_id,
            "clicks": clicks_by_code,
            "processed": processed,
            "acknowledged": acknowledged
        }

    finally:
        release_worker_lock(token)



def acknowledge_pending_batch(raw_batch: str) -> bool:
    """
    Delete a pending batch only if it is still the same batch.
    """

    lua_script = """
    if redis.call('GET', KEYS[1]) == ARGV[1] then
        return redis.call('DEL', KEYS[1])
    end

    return 0
    """

    result = redis_client.eval(
        lua_script,
        1,
        PENDING_BATCH_KEY,
        raw_batch
    )

    return bool(result)
