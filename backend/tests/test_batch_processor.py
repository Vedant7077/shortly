
from uuid import uuid4

from sqlalchemy import select

from database import SessionLocal
from models import Link, ProcessedBatch
from batch_processor import process_click_batch


SHORT_CODE = "PHPs8s"

# Generate fresh IDs so previous test runs don't interfere.
batch_id = f"python-test-{uuid4().hex[:8]}"
rollback_batch_id = f"rollback-test-{uuid4().hex[:8]}"


def get_clicks():
    with SessionLocal() as db:
        return db.scalar(
            select(Link.clicks).where(
                Link.short_code == SHORT_CODE
            )
        )


def batch_exists(batch_id):
    with SessionLocal() as db:
        return db.get(ProcessedBatch, batch_id) is not None


# Record initial count.
initial_clicks = get_clicks()
print("\nInitial clicks:", initial_clicks)


# TEST 1: New batch
print("\n--- TEST 1: New batch ---")

result = process_click_batch(
    SessionLocal(),
    batch_id,
    {"PHPs8s": 10}
)

print("Processed:", result)
print("Clicks:", get_clicks())


# TEST 2: Duplicate batch
print("\n--- TEST 2: Duplicate batch ---")

result = process_click_batch(
    SessionLocal(),
    batch_id,
    {"PHPs8s": 20}
)

print("Processed:", result)
print("Clicks:", get_clicks())


# TEST 3: Invalid short code should rollback everything.
print("\n--- TEST 3: Rollback test ---")

try:
    process_click_batch(
        SessionLocal(),
        rollback_batch_id,
        {
            "PHPs8s": 5,
            "INVALID": 10
        }
    )
except ValueError as error:
    print("Expected error:", error)

print("Clicks:", get_clicks())
print("Rollback batch registered:", batch_exists(rollback_batch_id))


# Final verification
final_clicks = get_clicks()

print("\n--- FINAL VERIFICATION ---")
print("Initial clicks:", initial_clicks)
print("Final clicks:", final_clicks)
print("Expected final clicks:", initial_clicks + 10)
print("New batch registered:", batch_exists(batch_id))
