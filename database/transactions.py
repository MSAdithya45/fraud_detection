import pandas as pd

from sqlalchemy import inspect, text

from database.connection import get_engine, ensure_unique_transaction_id


# ============================================================
# ENGINE
# ============================================================
# `engine` is imported by src/api/routes.py and
# src/llm/explanation_service.py — keep it exported.
# ============================================================

engine = get_engine()

PROCESSED_STAGING = "processed_transactions_staging"
PROCESSED_HISTORY = "processed_transactions_history"


# ============================================================
# STORE PROCESSED TRANSACTION  ->  processed_transactions_staging
# ============================================================

def store_processed_transaction(db_record):
    """Append a fully-processed record (features + AE/ISO scores +
    prediction/probability/label) to the processed staging buffer and
    return the buffer's current row count.

    The table is auto-created on the first insert.
    """

    db_record.to_sql(
        name=PROCESSED_STAGING,
        con=engine,
        if_exists="append",
        index=False,
    )

    # Enforce one row per TransactionID (no-op once the index exists).
    ensure_unique_transaction_id(PROCESSED_STAGING)

    with engine.connect() as conn:
        row_count = conn.execute(
            text(f'SELECT COUNT(*) FROM {PROCESSED_STAGING}')
        ).scalar()

    return row_count


# ============================================================
# READ PROCESSED  (history + current staging buffer)
# ============================================================

def _existing_processed_tables():
    inspector = inspect(engine)
    return [
        t for t in (PROCESSED_HISTORY, PROCESSED_STAGING)
        if inspector.has_table(t)
    ]


def read_processed(columns="*", where="", params=None, order=""):
    """Read prediction rows from the processed history UNION the current
    staging buffer, so freshly-scored transactions appear immediately
    (before their chunk is flushed to history).

    Returns an empty DataFrame if neither table exists yet.
    """

    tables = _existing_processed_tables()

    if not tables:
        return pd.DataFrame()

    union = " UNION ALL ".join(
        f'SELECT {columns} FROM {t} {where}' for t in tables
    )

    sql = f'SELECT * FROM ({union}) u {order}' if order else union

    return pd.read_sql(text(sql), engine, params=params)
