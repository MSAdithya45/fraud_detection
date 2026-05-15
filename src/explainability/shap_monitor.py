import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv
import os

load_dotenv()

engine = create_engine(
    f"mysql+mysqlconnector://root:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}/{os.getenv('DB_NAME')}"
)

# ==========================================================
# STORE SHAP RESULTS
# ==========================================================

def store_shap_results(transaction_id, explanation_df):

    explanation_df["transaction_id"] = transaction_id

    explanation_df.to_sql(
        name="developer_explanations",
        con=engine,
        if_exists="append",
        index=False
    )

    print("SHAP explanation stored.")