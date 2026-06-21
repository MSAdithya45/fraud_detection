import json

import pandas as pd

from database.connection import get_engine
from database.flush import flush_staging_to_history


# ============================================================
# ENGINE
# ============================================================

engine = get_engine()

PROCESSED_STAGING = "processed_transactions_staging"

# Normalized schema shared by all three drift tables.
_DRIFT_COLUMNS = [
    "transaction_ids",
    "iso_drift_score",
    "ae_drift_score",
    "rules_drift_score",
    "feature_drift_score",
    "final_drift_score",
    "monitoring_status",
]


# ============================================================
# GET TRANSACTION IDS OF THE CURRENT CHUNK
# ============================================================

def get_transaction_ids():

    df = pd.read_sql(
        f'SELECT "TransactionID" FROM {PROCESSED_STAGING}',
        engine,
    )

    if df.empty:
        return []

    return df["TransactionID"].tolist()


# ============================================================
# LOG SEVERITY  +  COMMIT CHUNK
# ============================================================

def _log_severity(drift_df, table):
    """Store one drift row (chunk TransactionIDs + drift scores) into the
    severity table, then commit the chunk: staging -> history, empty staging.
    """

    transaction_ids = get_transaction_ids()

    record = drift_df.copy()
    record["transaction_ids"] = json.dumps(transaction_ids)
    record["monitoring_status"] = "ACTIVE"

    # Keep only the normalized columns that exist on the drift frame.
    record = record[[c for c in _DRIFT_COLUMNS if c in record.columns]]

    record.to_sql(
        name=table,
        con=engine,
        if_exists="append",
        index=False,
    )

    print(f"Drift metadata stored in {table}.")

    # Move this chunk out of staging into history and empty the buffers.
    flush_staging_to_history()


def log_low_severity(drift_df):
    _log_severity(drift_df, "drift_low_severity")
    print("LOW severity chunk committed.")


def log_medium_severity(drift_df):
    _log_severity(drift_df, "drift_medium_severity")
    print("MEDIUM severity chunk committed.")


def log_high_severity(drift_df):
    _log_severity(drift_df, "drift_high_severity")
    print("HIGH severity chunk committed.")
