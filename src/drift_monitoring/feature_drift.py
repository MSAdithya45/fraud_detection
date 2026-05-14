import json
import numpy as np

from database.batch_loader import load_recent_transactions

from src.drift_monitoring.psi_monitor import calculate_psi
from src.drift_monitoring.ks_monitor import calculate_ks


def calculate_feature_drift():

    with open("baseline/feature_baselines.json") as f:
        baselines = json.load(f)

    recent_df = load_recent_transactions(limit=500)

    feature_scores = []

    for feature, baseline in baselines.items():

        if feature not in recent_df.columns:
            continue

        current_values = recent_df[feature].dropna().values

        expected_values = np.random.normal(
            baseline["mean"],
            baseline["std"],
            10000
        )

        bins = np.linspace(
            baseline["min"],
            baseline["max"],
            10
        )

        psi_score = calculate_psi(
            expected_values,
            current_values,
            bins
        )

        ks_result = calculate_ks(
            expected_values,
            current_values
        )

        ks_score = ks_result["ks_statistic"]

        drift_score = (psi_score + ks_score) / 2

        feature_scores.append(drift_score)

    overall_feature_drift = np.mean(feature_scores)

    return {
        "feature_drift_score": overall_feature_drift
    }