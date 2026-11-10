from redis_client import redis_client

try:
    redis_client.ping()
    print("Redis connected successfully!")

except redis.RedisError as error:
    print("Redis connection failed:", error)