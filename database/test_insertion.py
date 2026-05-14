from database.transactions import insert_transaction
import pandas as pd

sample = pd.read_csv(
    "./dataset/final_dataset_after_feature_selection_in_xgboost.csv",
    nrows=1
)

row = sample.iloc[0].to_dict()


insert_transaction(row)