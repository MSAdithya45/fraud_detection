import os
import json
import pandas as pd

from pathlib import Path

from sqlalchemy import (
    create_engine,
    text,
    inspect
)

from dotenv import load_dotenv


# ============================================================
# ENV
# ============================================================

load_dotenv()

engine = create_engine(
    f"mysql+mysqlconnector://root:{os.getenv('DB_PASSWORD')}@"
    f"{os.getenv('DB_HOST')}/{os.getenv('DB_NAME')}"
)


# ============================================================
# GET ALL TRANSACTION IDS
# ============================================================

def get_transaction_ids():

    query = """
    SELECT TransactionID
    FROM new_transactions
    """

    df = pd.read_sql(
        query,
        engine
    )

    if df.empty:
        return []

    return df["TransactionID"].tolist()


# ============================================================
# COPY RAW TRANSACTIONS
# ============================================================

def copy_transactions(
    transaction_ids,
    target_table
):

    if not transaction_ids:

        print("No transaction IDs found.")
        return

    inspector = inspect(engine)

    with engine.connect() as conn:

        # ====================================================
        # CREATE TARGET TABLE
        # SAME SCHEMA AS raw_new_transactions
        # ====================================================

        if not inspector.has_table(target_table):

            conn.execute(
                text(
                    f"""
                    CREATE TABLE {target_table}
                    AS
                    SELECT *
                    FROM raw_new_transactions
                    WHERE 1=0
                    """
                )
            )

            conn.commit()

            print(
                f"{target_table} created successfully."
            )

        # ====================================================
        # PREPARE IDS
        # ====================================================

        ids_string = ",".join(
            map(str, transaction_ids)
        )

        # ====================================================
        # COPY RAW ROWS
        # ====================================================

        conn.execute(
            text(
                f"""
                INSERT INTO {target_table}

                SELECT *
                FROM raw_new_transactions

                WHERE TransactionID IN ({ids_string})
                """
            )
        )

        conn.commit()

    print(
        f"Transactions copied to {target_table}"
    )


# ============================================================
# EXPORT MEDIUM BATCH CSV
# ============================================================

def export_medium_batch_csv(transaction_ids):

    if not transaction_ids:

        print("No transaction IDs found.")
        return

    dataset_dir = Path("dataset")

    dataset_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    existing_files = list(
        dataset_dir.glob("medium_batch_*.csv")
    )

    batch_numbers = []

    for file in existing_files:

        try:

            number = int(
                file.stem.split("_")[-1]
            )

            batch_numbers.append(number)

        except Exception:

            pass

    next_batch = (
        max(batch_numbers) + 1
        if batch_numbers
        else 1
    )

    ids_string = ",".join(
        map(str, transaction_ids)
    )

    query = f"""
    SELECT *
    FROM medium_transactions_record
    WHERE TransactionID IN ({ids_string})
    """

    batch_df = pd.read_sql(
        query,
        engine
    )

    output_path = (
        dataset_dir /
        f"medium_batch_{next_batch}.csv"
    )

    batch_df.to_csv(

        output_path,

        index=False
    )

    print(
        f"Medium batch exported : {output_path}"
    )


# ============================================================
# EXPORT HIGH BATCH CSV
# ============================================================

def export_high_batch_csv(transaction_ids):

    if not transaction_ids:

        print("No transaction IDs found.")
        return

    dataset_dir = Path("dataset")

    dataset_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    existing_files = list(
        dataset_dir.glob("high_batch_*.csv")
    )

    batch_numbers = []

    for file in existing_files:

        try:

            number = int(
                file.stem.split("_")[-1]
            )

            batch_numbers.append(number)

        except Exception:

            pass

    next_batch = (
        max(batch_numbers) + 1
        if batch_numbers
        else 1
    )

    ids_string = ",".join(
        map(str, transaction_ids)
    )

    query = f"""
    SELECT *
    FROM high_transactions_record
    WHERE TransactionID IN ({ids_string})
    """

    batch_df = pd.read_sql(
        query,
        engine
    )

    output_path = (
        dataset_dir /
        f"high_batch_{next_batch}.csv"
    )

    batch_df.to_csv(

        output_path,

        index=False
    )

    print(
        f"High batch exported : {output_path}"
    )


# ============================================================
# CLEAR NEW TRANSACTIONS TABLE
# ============================================================

def clear_new_transactions():

    with engine.connect() as conn:

        conn.execute(
            text(
                "DELETE FROM new_transactions"
            )
        )

        conn.commit()

    print("new_transactions table cleared.")


# ============================================================
# LOW SEVERITY
# ============================================================

def log_low_severity(df):

    transaction_ids = get_transaction_ids()

    df["transaction_ids"] = json.dumps(
        transaction_ids
    )

    df.to_sql(

        name="drift_analysis_log",

        con=engine,

        if_exists="append",

        index=False
    )

    print(
        "LOW severity metadata stored."
    )

    copy_transactions(

        transaction_ids=transaction_ids,

        target_table="low_transactions_record"
    )

    clear_new_transactions()

    print(
        "LOW severity completed successfully."
    )


# ============================================================
# MEDIUM SEVERITY
# ============================================================

def log_medium_severity(df):

    transaction_ids = get_transaction_ids()

    df["transaction_ids"] = json.dumps(
        transaction_ids
    )

    df.to_sql(

        name="medium_severity_watchlist",

        con=engine,

        if_exists="append",

        index=False
    )

    print(
        "MEDIUM severity metadata stored."
    )

    copy_transactions(

        transaction_ids=transaction_ids,

        target_table="medium_transactions_record"
    )

    export_medium_batch_csv(
        transaction_ids
    )

    clear_new_transactions()

    print(
        "MEDIUM severity completed successfully."
    )


# ============================================================
# HIGH SEVERITY
# ============================================================

def log_high_severity(df):

    transaction_ids = get_transaction_ids()

    # ========================================================
    # ADD TRANSACTION IDS
    # ========================================================

    df["transaction_ids"] = json.dumps(
        transaction_ids
    )

    # ========================================================
    # STORE METADATA
    # ========================================================

    df.to_sql(

        name="feedback_queue",

        con=engine,

        if_exists="append",

        index=False
    )

    print(
        "HIGH severity metadata stored."
    )

    # ========================================================
    # STORE RAW TRANSACTIONS
    # ========================================================

    copy_transactions(

        transaction_ids=transaction_ids,

        target_table="high_transactions_record"
    )

    # ========================================================
    # EXPORT HIGH BATCH CSV
    # ========================================================

    export_high_batch_csv(
        transaction_ids
    )

    # ========================================================
    # CLEAR DRIFT STACK
    # ========================================================

    clear_new_transactions()

    print(
        "HIGH severity completed successfully."
    )