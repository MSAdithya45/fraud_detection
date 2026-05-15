import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

from sqlalchemy import create_engine
from dotenv import load_dotenv
import os

# ==========================================================
# ENV
# ==========================================================

load_dotenv()

engine = create_engine(
    f"mysql+mysqlconnector://root:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}/{os.getenv('DB_NAME')}"
)

# ==========================================================
# PAGE
# ==========================================================

st.set_page_config(
    page_title="SHAP Developer Dashboard",
    layout="wide"
)

st.title("Fraud Detection SHAP Dashboard")

# ==========================================================
# LOAD SHAP DATA
# ==========================================================

query = """
SELECT *
FROM developer_explanations
LIMIT 500
"""

df = pd.read_sql(query, engine)

# ==========================================================
# RECENT EXPLANATIONS
# ==========================================================

st.subheader("Recent SHAP Explanations")

st.dataframe(
    df,
    use_container_width=True
)

# ==========================================================
# GLOBAL FEATURE IMPORTANCE
# ==========================================================

st.subheader("Global Feature Importance")

importance_df = (
    df.groupby("feature")["absolute_impact"]
    .mean()
    .reset_index()
)

importance_df = importance_df.sort_values(
    "absolute_impact",
    ascending=False
)

st.bar_chart(
    importance_df.set_index("feature")
)

# ==========================================================
# TRANSACTION VIEW
# ==========================================================

st.subheader("Transaction-Level Explanation")

transaction_ids = df["transaction_id"].unique()

selected_txn = st.selectbox(
    "Select Transaction ID",
    transaction_ids
)

txn_df = df[
    df["transaction_id"] == selected_txn
]

st.dataframe(txn_df)

# ==========================================================
# TOP DRIVERS
# ==========================================================

st.subheader("Top Fraud Drivers")

top_features = txn_df.sort_values(
    "absolute_impact",
    ascending=False
)

fig, ax = plt.subplots(figsize=(10, 5))

ax.barh(
    top_features["feature"],
    top_features["impact"]
)

ax.invert_yaxis()

st.pyplot(fig)