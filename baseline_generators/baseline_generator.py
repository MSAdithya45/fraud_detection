# generate_all_baselines.py
# Master runner for complete fraud governance baseline generation

from baseline_generators.rules_baseline_generator import generate_rules_baseline
from baseline_generators.iso_baseline_generator import generate_iso_baseline
from baseline_generators.ae_baseline_generator import generate_ae_baseline
from baseline_generators.feature_baselines_generator import generate_feature_baseline


def generate_all_baselines():

    # Selected important business + fraud behavioral features
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

    print("Generating rules baseline...")
    generate_rules_baseline()

    print("Generating iso baseline...")
    generate_iso_baseline()

    print("Generating AE baseline...")
    generate_ae_baseline()

    print("Generating feature baseline...")
    generate_feature_baseline(selected_features)

    print("All baseline files generated successfully.")


if __name__ == "__main__":
    generate_all_baselines()