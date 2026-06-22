import pandas as pd

from database.connection import get_engine, ensure_unique_transaction_id


# ============================================================
# ENGINE
# ============================================================

engine = get_engine()

RAW_STAGING = "raw_transactions_staging"

# IEEE-CIS training label. Real-time raw transactions arrive WITHOUT a
# label, so we drop it if present before storing the raw record.
LABEL_COLUMN = "isFraud"


# ============================================================
# STORE RAW TRANSACTION  ->  raw_transactions_staging
# ============================================================

def store_raw_transaction(raw_df):
    # --------------------------------------------------------
    # Normalize input to a DataFrame
    # --------------------------------------------------------

    if isinstance(raw_df, dict):
        raw_df = pd.DataFrame([raw_df])

    elif isinstance(raw_df, pd.Series):
        raw_df = raw_df.to_frame().T

    elif isinstance(raw_df, pd.DataFrame):
        raw_df = raw_df.copy()

    else:
        raise ValueError(
            f"Unsupported raw_df type: {type(raw_df)}"
        )

    # --------------------------------------------------------
    # Drop the training label if (and only if) it is present
    # --------------------------------------------------------

    raw_df = raw_df.drop(columns=[LABEL_COLUMN], errors="ignore")

    # --------------------------------------------------------
    # Append to the raw staging buffer.
    # The table is auto-created on the first insert with the
    # schema of the incoming (label-free) raw data.
    # --------------------------------------------------------

    raw_df.to_sql(
        name=RAW_STAGING,
        con=engine,
        if_exists="append",
        index=False,
    )

    # Enforce one row per TransactionID (no-op once the index exists).
    ensure_unique_transaction_id(RAW_STAGING)

    print("Raw transaction stored in raw_transactions_staging.")
