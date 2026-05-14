import json
import numpy as np

from database.batch_loader import load_recent_transactions

from src.drift_monitoring.psi_monitor import calculate_psi
from src.drift_monitoring.ks_monitor import calculate_ks


def calculate_iso_drift():

    with open("baseline/iso_baseline.json") as f:
        baseline = json.load(f)

    recent_df = load_recent_transactions(limit=500)

    current_scores = recent_df["iso_score"].values

    expected_scores = np.random.normal(
        baseline["mean"],
        baseline["std"],
        10000
    )

    psi_score = calculate_psi(
        expected_scores,
        current_scores,
        baseline["psi_bins"]
    )

    ks_result = calculate_ks(
        expected_scores,
        current_scores
    )

    ks_score = ks_result["ks_statistic"]

    drift_score = (psi_score + ks_score) / 2

    return {
        "psi_score": psi_score,
        "ks_score": ks_score,
        "drift_score": drift_score
    }