import os
import pandas as pd

from sqlalchemy import create_engine
from sqlalchemy import inspect,text

from dotenv import load_dotenv

# ============================================================
# ENV
# ============================================================

load_dotenv()

engine = create_engine(
    f"mysql+mysqlconnector://root:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}/{os.getenv('DB_NAME')}"
)



# ====================================================
# DB STORAGE FUNCTION FOR DRIFT STACK
# ====================================================

def store_new_transaction(db_record):

    table_name = "new_transactions"

    inspector = inspect(engine)

    # ====================================================
    # CREATE TABLE + INSERT FIRST RECORDS IF NOT EXISTS
    # ====================================================

    if not inspector.has_table(table_name):

        db_record.to_sql(
            name=table_name,
            con=engine,
            if_exists="replace",
            index=False
        )

        print(
            f"{table_name} table created successfully "
            f"with {len(db_record)} initial record(s)."
        )

    # ====================================================
    # TABLE EXISTS -> APPEND NEW RECORDS
    # ====================================================

    else:

        existing_columns = [
            col["name"] for col in inspector.get_columns(table_name)
        ]

        incoming_columns = db_record.columns.tolist()

        missing_cols = set(existing_columns) - set(incoming_columns)
        extra_cols = set(incoming_columns) - set(existing_columns)

        if missing_cols or extra_cols:

            raise ValueError(
                f"Schema mismatch!\n"
                f"Missing columns: {missing_cols}\n"
                f"Extra columns: {extra_cols}"
            )

        # Align incoming dataframe with DB schema
        db_record = db_record[existing_columns]

        db_record.to_sql(
            name="new_transactions",
            con=engine,
            if_exists="append",
            index=False
        )

        print(
            f"{len(db_record)} new record(s) appended "
            f"to {table_name}."
        )

    # ========================================================
    # CHECK TOTAL ROW COUNT
    # ========================================================

    with engine.connect() as conn:

        result = conn.execute(
            text(
                f"SELECT COUNT(*) FROM {table_name}"
            )
        )

        row_count = result.scalar()

    print(f"Current Rows : {row_count}")

    # ========================================================
    # RETURN ROW COUNT
    # ========================================================

    return row_count