# ====================================================
# DETERMINE DRIFT SEVERITY
# ====================================================

def determine_severity(drift_result):
    """
    Determines drift severity level based on final aggregated drift score.

    Parameters:
        drift_result (dict): Drift result dictionary from aggregate_drift()

    Returns:
        str: LOW / MEDIUM / HIGH
    """

    # ====================================================
    # EXTRACT FINAL SCORE
    # ====================================================

    final_drift_score = drift_result["final_drift_score"]

    # ====================================================
    # LOW DRIFT
    # ====================================================

    if final_drift_score < 0.10:
        return "LOW"

    # ====================================================
    # MEDIUM DRIFT
    # ====================================================

    elif final_drift_score <= 0.5:
        return "MEDIUM"

    # ====================================================
    # HIGH DRIFT
    # ====================================================

    else:
        return "HIGH"