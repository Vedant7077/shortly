from outbox_worker import process_pending_events

result = process_pending_events()

print("Worker result:", result)