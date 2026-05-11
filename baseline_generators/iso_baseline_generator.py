# iso_baseline_generator.py
# Generates statistical baseline for iso_score

import numpy as np
import json
import os
from database.load_training_data import load_full_training_data


def generate_iso_baseline(iso_column="iso_score"):

    train_df = load_full_training_data()
    series = train_df[iso_column]

    baseline = {
        "feature_name": "iso_score",

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

    with open("baseline/iso_baseline.json", "w") as f:
        json.dump(baseline, f, indent=4)

    print("ISO baseline generated successfully.")


if __name__ == "__main__":
    generate_iso_baseline()