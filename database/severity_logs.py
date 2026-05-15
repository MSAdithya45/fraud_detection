import os
import pandas as pd

from sqlalchemy import create_engine

from dotenv import load_dotenv

# ============================================================
# ENV
# ============================================================

load_dotenv()

engine = create_engine(
    f"mysql+mysqlconnector://root:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}/{os.getenv('DB_NAME')}"
)

# ============================================================
# LOW SEVERITY
# ============================================================

def log_low_severity(drift_result):

    df = pd.DataFrame([drift_result])

    df.to_sql(

        name="drift_analysis_log",

        con=engine,

        if_exists="append",

        index=False
    )

    print("LOW severity stored in drift_analysis_log")


# ============================================================
# MEDIUM SEVERITY
# ============================================================

def log_medium_severity(drift_result):

    df = pd.DataFrame([drift_result])

    df.to_sql(

        name="medium_severity_watchlist",

        con=engine,

        if_exists="append",

        index=False
    )

    print("MEDIUM severity stored in medium_severity_watchlist")