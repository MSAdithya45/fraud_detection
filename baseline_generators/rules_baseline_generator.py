# rules_baseline_generator.py
# Generates statistical baseline for rules_score

import numpy as np
import json
import os
from database.load_training_data import load_full_training_data


def generate_rules_baseline(rules_column="rule_score"):

    train_df = load_full_training_data()
    series = train_df[rules_column]

    baseline = {
        "feature_name": "rule_score",

        "mean": float(series.mean()),
        "std": float(series.std()),
        "min": float(series.min()),
        "max": float(series.max()),

        "p50": float(np.percentile(series, 50)),
        "p75": float(np.percentile(series, 75)),
        "p90": float(np.percentile(series, 90)),
        "p95": float(np.percentile(series, 95)),
        "p99": float(np.percentile(series, 99)),

        "warning_threshold": None,
        "severe_threshold": None,

        "psi_bins": list(np.histogram_bin_edges(series, bins=10))
    }

    os.makedirs("baseline", exist_ok=True)

    with open("baseline/rules_baseline.json", "w") as f:
        json.dump(baseline, f, indent=4)

    print("Rules baseline generated successfully.")


if __name__ == "__main__":
    generate_rules_baseline()