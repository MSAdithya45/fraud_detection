

import sys
from pathlib import Path

# ── make sibling imports available ──────────────────────────────────────────
_PIPELINE_DIR = Path(__file__).resolve().parent
_REPO_ROOT    = _PIPELINE_DIR.parents[1]
sys.path.insert(0, str(_PIPELINE_DIR))

import pandas as pd
from fraud_rules_engine     import RulesEngine,            SAVED_MODELS
from fraud_preprocessing    import PreprocessingPipeline
# AEScorer and ISOScorer are loaded from existing .pkl/.keras files —
# their training happens externally (Keras training loop, sklearn fit).
# train.py only fits and saves the two pipeline components we own.


def main():
    dataset_path = _REPO_ROOT / "dataset/dataset.csv"
    print(f"Loading dataset : {dataset_path}")
    train_df = pd.read_csv(dataset_path)
    print(f"Shape           : {train_df.shape}")
    print(f"Fraud rate      : {train_df['isFraud'].mean():.4f}\n")

    # ── Step 1 : fit & save RulesEngine ────────────────────────────────────
    rules_engine = RulesEngine()
    rules_engine.fit(train_df, target_col='isFraud')
    rules_engine.save()                               # → saved_models/rules_engine.pkl

    # ── Step 2 : apply rules engine to get 465-col df ──────────────────────
    train_no_target = train_df.drop(columns=['isFraud'], errors='ignore')
    train_465       = rules_engine.transform(train_no_target)
    train_465['isFraud'] = train_df['isFraud'].values
    print(f"After rules engine : {train_465.shape}")

    # ── Step 3 : fit & save PreprocessingPipeline ───────────────────────────
    pp = PreprocessingPipeline()
    pp.fit(train_465, target_col='isFraud')
    pp.save()                                         # → saved_models/preprocessing.pkl

    # ── Verification ────────────────────────────────────────────────────────
    sample = train_no_target.iloc[[0]]
    s1     = rules_engine.transform(sample)
    s2     = pp.transform(s1)

    print(f"\n{'='*50}")
    print("  TRAINING COMPLETE")
    print(f"{'='*50}")
    print(f"  raw input            : {sample.shape}")
    print(f"  after rules engine   : {s1.shape}")
    print(f"  after preprocessing  : {s2.shape}")
    print(f"  saved_models/        : {SAVED_MODELS}")
    print(f"  Files saved:")
    for f in sorted(SAVED_MODELS.glob("*")):
        print(f"    {f.name}")


if __name__ == "__main__":
    main()