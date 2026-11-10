from database import SessionLocal
from batch_processor import process_click_batch

batch_id = "48415301-010f-4035-b48f-6894341af277"

with SessionLocal() as db:
    result = process_click_batch(
        db,
        batch_id,
        {"PHPs8s": 5}
    )

print("Duplicate batch processed:", result)