import os
import sys

# Allow running this file directly (`python database/upload_dataset.py`) by
# putting the project root on sys.path so `database` is importable.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv
load_dotenv()


from database.connection import get_engine

engine = get_engine()
df = pd.read_csv(
    "./dataset/final_dataset_after_feature_selection_in_xgboost.csv"
)

print("Dataset Shape:", df.shape)
print(df.head())

df.to_sql(
    name="training_data",
    con=engine,
    if_exists="replace",
    index=False,
    chunksize=1000   # Smaller stable chunks
)

print("Dataset uploaded successfully.")