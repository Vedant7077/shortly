from redis_client import redis_client

# Store a shortened URL mapping
redis_client.set(
    "short:PHPs8s",
    "https://www.google.com"
)

# Retrieve the URL
original_url = redis_client.get("short:PHPs8s")

print("Retrieved URL:", original_url)

# Check whether the key exists
exists = redis_client.exists("short:PHPs8s")

print("Key exists:", bool(exists))