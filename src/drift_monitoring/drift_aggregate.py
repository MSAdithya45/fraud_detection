from src.drift_monitoring.iso_drift import calculate_iso_drift
from src.drift_monitoring.ae_drift import calculate_ae_drift
from src.drift_monitoring.rules_drift import calculate_rules_drift
from src.drift_monitoring.feature_drift import calculate_feature_drift


def aggregate_drift():

    iso_result = calculate_iso_drift()
    ae_result = calculate_ae_drift()
    rules_result = calculate_rules_drift()
    feature_result = calculate_feature_drift()

    final_score = (

        0.30 * rules_result["drift_score"] +
        0.25 * iso_result["drift_score"] +
        0.25 * ae_result["drift_score"] +
        0.20 * feature_result["feature_drift_score"]

    )

    return {
        "final_drift_score": final_score,

        "iso_drift": iso_result,
        "ae_drift": ae_result,
        "rules_drift": rules_result,
        "feature_drift": feature_result
    }