import pandas as pd

from database.connection import get_engine

engine = get_engine()


# ============================================================
# LOAD RECENT TRANSACTIONS FOR DRIFT
# ============================================================
# Drift monitoring runs on the current processed staging buffer,
# which holds at most one chunk (~30 rows) before it is flushed.
# ============================================================

def load_recent_transactions(limit=30):

    query = f"""
    SELECT *
    FROM processed_transactions_staging
    LIMIT {limit}
    """

    return pd.read_sql(query, engine)
