import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv
import os
load_dotenv()



engine = create_engine(
    f"mysql+mysqlconnector://root:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}/{os.getenv('DB_NAME')}"
)

def load_recent_transactions(limit=500):

    query = f"""
    SELECT *
    FROM new_transactions
    LIMIT {limit}
    """

    return pd.read_sql(query, engine)