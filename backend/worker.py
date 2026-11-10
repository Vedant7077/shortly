
import time
import logging

from click_aggregator import (
    collect_clicks,
    process_pending_batch
)
from outbox_worker import process_pending_events

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

BATCH_INTERVAL = 10


def start_worker():
    logging.info("Shortly background worker started")

    while True:
        try:
            # Step 1: Collect Redis click counters.
            batch = collect_clicks()

            if batch:
                logging.info(
                    "Collected batch: %s",
                    batch["batch_id"]
                )

            # Step 2: Transfer pending clicks to PostgreSQL.
            result = process_pending_batch()

            if result.get("processed"):
                logging.info(
                    "Click batch processed successfully: %s",
                    result["batch_id"]
                )
            else:
                logging.info("No pending clicks to process")

            # Step 3: Process pending URL-update events.
            outbox_result = process_pending_events()

            if outbox_result["processed"] or outbox_result["failed"]:
                logging.info(
                    "Outbox processing result: %s",
                    outbox_result
                )

        except Exception:
            logging.exception("Background worker processing failed")

        time.sleep(BATCH_INTERVAL)


if __name__ == "__main__":
    start_worker()
