import pandas as pd
from sqlalchemy import create_engine

engine = create_engine(
    "mysql+mysqlconnector://root:msa45ad@localhost/fraud_detection"
)

def load_full_training_data():
    query = "SELECT * FROM data"
    return pd.read_sql(query, engine)