import pandas as pd

from src.drift_monitoring.iso_drift import calculate_iso_drift
from src.drift_monitoring.ae_drift import calculate_ae_drift
from src.drift_monitoring.rules_drift import calculate_rules_drift
from src.drift_monitoring.feature_drift import calculate_feature_drift


# ============================================================
# AGGREGATE DRIFT
# ============================================================

def aggregate_drift():

    # ========================================================
    # INDIVIDUAL DRIFT COMPONENTS
    # ========================================================

    iso_result = calculate_iso_drift()

    ae_result = calculate_ae_drift()

    rules_result = calculate_rules_drift()

    feature_result = calculate_feature_drift()

    # ========================================================
    # FINAL WEIGHTED DRIFT SCORE
    # ========================================================

    final_drift_score = (

        0.30 * rules_result["drift_score"] +

        0.25 * iso_result["drift_score"] +

        0.25 * ae_result["drift_score"] +

        0.20 * feature_result["feature_drift_score"]

    )

    # ========================================================
    # CREATE FINAL DATAFRAME
    # ========================================================

    drift_df = pd.DataFrame([{

        "final_drift_score": final_drift_score,

        "iso_drift_score": iso_result["drift_score"],

        "ae_drift_score": ae_result["drift_score"],

        "rules_drift_score": rules_result["drift_score"],

        "feature_drift_score": feature_result[
            "feature_drift_score"
        ]

    }])

    # ========================================================
    # RETURN DATAFRAME
    # ========================================================

    return drift_df