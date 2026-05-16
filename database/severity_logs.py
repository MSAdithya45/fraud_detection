import os
import pandas as pd

from sqlalchemy import create_engine, text

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


    df.to_sql(

        name="drift_analysis_log",

        con=engine,

        if_exists="append",

        index=False
    )

    # ========================================================
    # CLEAR DRIFT STACK AFTER STORAGE
    # ========================================================

    clear_new_transactions()

    print("LOW severity stored in drift_analysis_log")


# ============================================================
# MEDIUM SEVERITY
# ============================================================

def log_medium_severity(df):

    df.to_sql(

        name="medium_severity_watchlist",

        con=engine,

        if_exists="append",

        index=False
    )

    # ========================================================
    # CLEAR DRIFT STACK AFTER STORAGE
    # ========================================================

    clear_new_transactions()

    print("MEDIUM severity stored in medium_severity_watchlist")