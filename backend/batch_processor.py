
from sqlalchemy import update
from sqlalchemy.orm import Session
from sqlalchemy.dialects.postgresql import insert

from models import Link, ProcessedBatch


def process_click_batch(
    db: Session,
    batch_id: str,
    clicks_by_code: dict[str, int],
) -> bool:
    """
    Process a click batch exactly once.

    Returns:
        True  -> New batch processed successfully.
        False -> Batch was already processed.
    """

    if not batch_id:
        raise ValueError("Batch ID cannot be empty")

    if not clicks_by_code:
        raise ValueError("Click batch cannot be empty")

    if any(count <= 0 for count in clicks_by_code.values()):
        raise ValueError("Click counts must be positive")

    with db.begin():

        # Step 1: Register the batch ID.
        # Duplicate IDs will not be inserted.
        statement = (
            insert(ProcessedBatch)
            .values(batch_id=batch_id)
            .on_conflict_do_nothing(
                index_elements=[ProcessedBatch.batch_id]
            )
            .returning(ProcessedBatch.batch_id)
        )

        result = db.execute(statement)

        new_batch_id = result.scalar_one_or_none()

        # Step 2: Skip duplicate batches.
        if new_batch_id is None:
            return False

        # Step 3: Increment clicks for each short code.
        for short_code, count in clicks_by_code.items():

            result = db.execute(
                update(Link)
                .where(Link.short_code == short_code)
                .values(clicks=Link.clicks + count)
            )

            # Missing short code should rollback the entire batch.
            if result.rowcount != 1:
                raise ValueError(
                    f"Short code not found: {short_code}"
                )

    # Step 4: Transaction commits automatically here.
    return True
