# feature_baseline_generator.py
# Generates statistical baseline for selected important business + behavioral features
# Excludes ae_score and iso_score since they already have dedicated baselines

import numpy as np
import json
import os
from database.load_training_data import load_full_training_data


def generate_feature_baseline(feature_columns):

    train_df = load_full_training_data()
    feature_baselines = {}

    for feature in feature_columns:

        if feature not in train_df.columns:
            print(f"Skipping missing feature: {feature}")
            continue

        series = train_df[feature].dropna()

        feature_baselines[feature] = {
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
            "severe_threshold": None
        }

    os.makedirs("baseline", exist_ok=True)

    with open("baseline/feature_baselines.json", "w") as f:
        json.dump(feature_baselines, f, indent=4)

    print("Feature baseline generated successfully.")


if __name__ == "__main__":

    selected_features = [
        "C1",
        "txn_count_1hr",
        "email_fraud_rate",
        "C14",
        "C13",
        "addr1",
        "card3",
        "D8",
        "id_17",
        "ProductCD_freq",
        "card2",
        "card6_freq",
        "TransactionAmt",
        "C11",
        "DeviceInfo_freq",
        "dist2",
        "id_31_freq",
        "D1"
    ]

    generate_feature_baseline(selected_features)