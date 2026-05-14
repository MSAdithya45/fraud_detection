import os
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv
load_dotenv()

engine = create_engine(
    f"mysql+mysqlconnector://root:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}/{os.getenv('DB_NAME')}"
)

def insert_transaction(data):

    df = pd.DataFrame([data])

    df.to_sql(
        name="new_transactions",
        con=engine,
        if_exists="append",
        index=False
    )

    print("Transaction inserted successfully.")