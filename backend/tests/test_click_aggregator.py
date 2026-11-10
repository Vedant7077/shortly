from click_aggregator import collect_clicks
from redis_client import redis_client

# Create test click counters
redis_client.set("clicks:TEST01", 10)
redis_client.set("clicks:TEST02", 20)

# Collect counters
batch = collect_clicks()

print("Collected batch:", batch)

# Check original counters
print("TEST01:", redis_client.get("clicks:TEST01"))
print("TEST02:", redis_client.get("clicks:TEST02"))

# Check pending batch
print("Pending:", redis_client.get("clicks:pending_batch"))