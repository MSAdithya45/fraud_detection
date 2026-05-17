import os
import pandas as pd

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
# STORE RAW TRANSACTION
# ============================================================

def store_raw_transaction(raw_df):
    # ========================================================
    # CONVERT INPUT TO DATAFRAME
    # ========================================================

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

    table_name = "raw_new_transactions"

    inspector = inspect(engine)

    with engine.connect() as conn:

        # ====================================================
        # CREATE TABLE USING data SCHEMA
        # ====================================================

        if not inspector.has_table(table_name):

            conn.execute(
                text(
                    f"""
                    CREATE TABLE {table_name}
                    AS
                    SELECT *
                    FROM data
                    WHERE 1=0
                    """
                )
            )

            conn.commit()

            print(
                f"{table_name} created successfully."
            )

    # ========================================================
    # INSERT RAW ROWS
    # ========================================================

    raw_df.to_sql(

        name=table_name,

        con=engine,

        if_exists="append",

        index=False
    )

    print(
        "Raw transaction stored successfully."
    )