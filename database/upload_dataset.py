import pandas as pd
from sqlalchemy import create_engine

engine = create_engine(
    "mysql+mysqlconnector://root:msa45ad@localhost/fraud_detection"
)

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