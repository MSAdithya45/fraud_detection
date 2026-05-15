import shap
import joblib
import pandas as pd
import matplotlib.pyplot as plt

# ==========================================================
# LOAD SAVED MODEL
# ==========================================================

model = joblib.load("saved_models/fraud_model.sav")

# ==========================================================
# CREATE EXPLAINER
# ==========================================================

explainer = shap.TreeExplainer(model)

# ==========================================================
# GENERATE SHAP EXPLANATION
# ==========================================================

def generate_shap_explanation(transaction_df):

    shap_values = explainer.shap_values(transaction_df)

    if isinstance(shap_values, list):
        shap_values = shap_values[1]

    vals = shap_values[0]

    explanation_df = pd.DataFrame({
        "feature": transaction_df.columns,
        "impact": vals
    })

    explanation_df["absolute_impact"] = (
        explanation_df["impact"].abs()
    )

    explanation_df = explanation_df.sort_values(
        "absolute_impact",
        ascending=False
    )

    return {
        "shap_values": vals,
        "explanation_df": explanation_df.head(10),
        "expected_value": explainer.expected_value
    }