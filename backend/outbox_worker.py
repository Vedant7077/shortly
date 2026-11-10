
from datetime import datetime, timezone
import logging

import redis

from database import SessionLocal
from models import OutboxEvent
from redis_client import redis_client

logger = logging.getLogger(__name__)


def process_pending_events():
    processed_count = 0
    failed_count = 0

    with SessionLocal() as db:

        # Step 1: Fetch pending events
        events = (
            db.query(OutboxEvent)
            .filter(OutboxEvent.status == "pending")
            .order_by(OutboxEvent.id.asc())
            .all()
        )

        for event in events:

            try:
                # Step 2: Extract short code
                short_code = event.payload["short_code"]

                # Step 3: Invalidate Redis cache
                redis_client.delete(f"short:{short_code}")

                # Step 4: Mark event as processed
                event.status = "processed"
                event.attempts += 1
                event.processed_at = datetime.now(timezone.utc)
                event.last_error = None

                db.commit()

                processed_count += 1

                logger.info(
                    "Event %s processed successfully",
                    event.id,
                )

            except (redis.RedisError, KeyError, TypeError) as error:

                # Step 5: Record failure for future retry
                event.attempts += 1
                event.last_error = str(error)

                db.commit()

                failed_count += 1

                logger.exception(
                    "Failed to process event %s",
                    event.id,
                )

    return {
        "processed": processed_count,
        "failed": failed_count,
    }
