from sqlalchemy import inspect, text

from database.connection import get_engine, ensure_unique_transaction_id


# ============================================================
# FLUSH STAGING BUFFERS  ->  HISTORY
# ============================================================

engine = get_engine()

# (staging table, history table) pairs
_PAIRS = [
    ("raw_transactions_staging", "raw_transactions_history"),
    ("processed_transactions_staging", "processed_transactions_history"),
]


def flush_staging_to_history():
    """Commit the current chunk: copy every staging row into its history
    table (skipping TransactionIDs already in history), then empty staging.

    On the first flush the history table is created with the exact schema of
    its staging table. The NOT EXISTS guard keeps history free of duplicate
    TransactionIDs across chunks; a unique index is also enforced as a hard
    guarantee.
    """

    inspector = inspect(engine)

    for staging, history in _PAIRS:

        if not inspector.has_table(staging):
            # Nothing buffered for this stream yet.
            continue

        with engine.begin() as conn:

            conn.execute(text(
                f'CREATE TABLE IF NOT EXISTS "{history}" '
                f'(LIKE "{staging}" INCLUDING DEFAULTS)'
            ))

            # Copy only rows whose TransactionID is not already in history.
            conn.execute(text(
                f'INSERT INTO "{history}" '
                f'SELECT s.* FROM "{staging}" s '
                f'WHERE NOT EXISTS ('
                f'  SELECT 1 FROM "{history}" h '
                f'  WHERE h."TransactionID" = s."TransactionID"'
                f')'
            ))

            conn.execute(text(f'DELETE FROM "{staging}"'))

        # Hard uniqueness guarantee on history (no-op once the index exists).
        ensure_unique_transaction_id(history)

    print("Staging buffers flushed to history and cleared.")
