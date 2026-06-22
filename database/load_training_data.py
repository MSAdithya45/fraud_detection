import os
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv
load_dotenv()


from database.connection import get_engine

engine = get_engine()

def load_full_training_data():
    query = "SELECT * FROM data"
    return pd.read_sql(query, engine)