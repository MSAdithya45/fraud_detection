import os
import pandas as pd

from sqlalchemy import create_engine
from sqlalchemy import text

from dotenv import load_dotenv

# ============================================================
# ENV
# ============================================================

load_dotenv()

engine = create_engine(
    f"mysql+mysqlconnector://root:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}/{os.getenv('DB_NAME')}"
)

# ============================================================
# INSERT TRANSACTION
# ============================================================

def insert_transaction(data):

    df = pd.DataFrame([data])

    # ========================================================
    # INSERT INTO TABLE
    # ========================================================

    df.to_sql(

        name="new_transactions",

        con=engine,

        if_exists="append",

        index=False
    )

    print("Transaction inserted successfully.")

    # ========================================================
    # CHECK ROW COUNT
    # ========================================================

    with engine.connect() as conn:

        result = conn.execute(

            text(
                "SELECT COUNT(*) FROM new_transactions"
            )
        )

        row_count = result.scalar()

    print(f"Current Rows : {row_count}")

    # ========================================================
    # RETURN ROW COUNT
    # ========================================================

    return row_count