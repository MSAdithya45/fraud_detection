import os
import sys

# Allow running this file directly (`python database/raw_data.py`) by
# putting the project root on sys.path so `database` is importable.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
import numpy as np

from sqlalchemy import create_engine
from dotenv import load_dotenv


# ============================================================
# LOAD ENV
# ============================================================

load_dotenv()

from database.connection import get_engine

engine = get_engine()


# ============================================================
# LOAD CSV
# ============================================================

df = pd.read_csv("dataset/dataset.csv")


# ============================================================
# BASIC CLEANING
# ============================================================

# Replace problematic infinite values
df = df.replace([np.inf, -np.inf], np.nan)

print("Dataset Shape:", df.shape)
print("Columns:", len(df.columns))


# ============================================================
# CREATE MYSQL TABLE SAFELY (SMALL CHUNKS)
# ============================================================

try:

    with engine.begin() as connection:

        df.to_sql(
            name="data",
            con=connection,
            if_exists="replace",
            index=False,
            chunksize=1000,      # Small safer chunk size
            method="multi"       # Batch insert optimization
        )

    print("data table created successfully.")

except Exception as e:

    print("Database upload failed.")
    print("Error:", str(e))


# ============================================================
# CLEANUP
# ============================================================

engine.dispose()