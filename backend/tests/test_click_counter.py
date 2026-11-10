from redis_client import redis_client

key = "clicks:PHPs8s"

# Reset counter for this experiment
redis_client.delete(key)

# Simulate 5 clicks
for _ in range(5):
    redis_client.incr(key)

# Read total clicks
total_clicks = redis_client.get(key)

print("Total clicks:", total_clicks)