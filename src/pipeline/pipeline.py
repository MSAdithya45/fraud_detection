# src/pipeline/pipeline.py

import numpy as np
import pandas as pd
import pickle
import joblib
import warnings
from pathlib import Path

warnings.filterwarnings('ignore')

# ── path resolution ──────────────────────────────────────────────────────────
_PIPELINE_DIR = Path(__file__).resolve().parent        # src/pipeline/
_REPO_ROOT    = _PIPELINE_DIR.parents[1]               # project_root/
SAVED_MODELS  = _REPO_ROOT / "saved_models"

import sys
sys.path.insert(0, str(_PIPELINE_DIR))                 # ensure sibling imports work

from fraud_rules_engine     import RulesEngine
from fraud_preprocessing    import PreprocessingPipeline
from fraud_autoencoder      import AEScorer
from fraud_isolation_forest import ISOScorer, merge_ae_iso, drop_low_features


class FraudPipeline:

    def __init__(self):
        self.rules_engine = None
        self.preprocessor = None
        self.ae_scorer    = None
        self.iso_scorer   = None
        self.xgb_model    = None
        self.xgb_features = None

    # ── LOAD ─────────────────────────────────────────────────────────────────

    @classmethod
    def load(cls, saved_models_dir=None):
        sm  = Path(saved_models_dir) if saved_models_dir else SAVED_MODELS
        obj = cls()

        print("=" * 55)
        print("  Loading FraudPipeline ...")
        print("=" * 55)

        obj.rules_engine = RulesEngine.load(sm / "rules_engine.pkl")
        obj.preprocessor = PreprocessingPipeline.load(sm / "preprocessing.pkl")
        obj.ae_scorer    = AEScorer.load(
            scaler_path    = sm / "scaler.pkl",
            model_path     = sm / "autoencoder_model.keras",
            threshold_path = sm / "ae_threshold.pkl",
            metadata_path  = sm / "ae_metadata.pkl",
        )
        obj.iso_scorer = ISOScorer.load(
            scaler_path   = sm / "iso_scaler.pkl",
            model_path    = sm / "isolation_forest.pkl",
            features_path = sm / "feature_columns.pkl",
        )

        xgb_path = sm / "fraud_model.sav"
        try:
            obj.xgb_model = joblib.load(xgb_path)
            print(f">> [FraudPipeline] XGB model (joblib) : {xgb_path}")
        except Exception:
            with open(xgb_path, 'rb') as f:
                obj.xgb_model = pickle.load(f)
            print(f">> [FraudPipeline] XGB model (pickle) : {xgb_path}")

        with open(sm / "xgb_feature_columns.pkl", 'rb') as f:
            raw = pickle.load(f)
        obj.xgb_features = (
            raw.get("feature_columns", raw.get("columns", list(raw.values())[0]))
            if isinstance(raw, dict) else list(raw)
        )
        print(f">> [FraudPipeline] XGB feature cols    : {len(obj.xgb_features)}")
        print("=" * 55)
        print("  All artifacts loaded.")
        print("=" * 55)
        return obj

    # ── INTERNAL ─────────────────────────────────────────────────────────────

    def _align_for_xgb(self, df):
        df      = df.copy()
        missing = [c for c in self.xgb_features if c not in df.columns]
        if missing:
            df = pd.concat([df, pd.DataFrame(0, index=df.index, columns=missing)], axis=1)
        return df[self.xgb_features]

    # ── PREDICT ──────────────────────────────────────────────────────────────

    def predict(self, raw_df):
        """
        Input  : raw DataFrame (433 original columns, no isFraud)
        Output : list of dicts with prediction, probability, label
        """
        rules_out = self.rules_engine.transform(raw_df)
        pp_out    = self.preprocessor.transform(rules_out)
        ae_out    = self.ae_scorer.transform(pp_out)
        iso_out   = self.iso_scorer.transform(pp_out)
        merged    = merge_ae_iso(ae_out, iso_out)
        dropped   = drop_low_features(merged)
        xgb_input = self._align_for_xgb(dropped)

        preds  = self.xgb_model.predict(xgb_input)
        probs  = self.xgb_model.predict_proba(xgb_input)[:, 1]

        return [
            {
                "prediction" : int(preds[i]),
                "probability": round(float(probs[i]), 6),
                "label"      : "FRAUD" if preds[i] == 1 else "LEGIT",
            }
            for i in range(len(raw_df))
        ]


# ── QUICK SMOKE-TEST (python pipeline.py) ───────────────────────────────────

if __name__ == "__main__":
    dataset_path = _REPO_ROOT / "dataset/dataset.csv"
    df           = pd.read_csv(dataset_path)
    print(f"Dataset shape : {df.shape}")

    pipeline = FraudPipeline.load()

    for label, mask in [("FRAUD", df['isFraud'] == 1), ("LEGIT", df['isFraud'] == 0)]:
        row    = df[mask].sample(1, random_state=42).drop(columns=['isFraud'], errors='ignore')
        result = pipeline.predict(row)
        print(f"\n[{label}]  prediction={result[0]['label']}  prob={result[0]['probability']}")