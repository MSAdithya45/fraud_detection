import os
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv

load_dotenv()



engine = create_engine(
    f"mysql+mysqlconnector://root:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}/{os.getenv('DB_NAME')}"
)

# Load small sample to infer schema
df = pd.read_csv(
    "./dataset/final_dataset_after_feature_selection_in_xgboost.csv",
    nrows=5
)


# Create table
df.to_sql(
    name="new_transactions",
    con=engine,
    if_exists="replace",
    index=False
)

print("new_transactions table created successfully.")