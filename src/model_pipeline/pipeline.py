# src/model_pipeline/pipeline.py

import numpy as np
import pandas as pd
import pickle
import joblib
import warnings

from pathlib import Path

warnings.filterwarnings('ignore')

# ─────────────────────────────────────────────────────────────
# PATH RESOLUTION
# ─────────────────────────────────────────────────────────────

_PIPELINE_DIR = Path(__file__).resolve().parent
_REPO_ROOT    = _PIPELINE_DIR.parents[1]

SAVED_MODELS  = _REPO_ROOT / "saved_models"

import sys
sys.path.insert(0, str(_PIPELINE_DIR))

# ─────────────────────────────────────────────────────────────
# IMPORTS
# ─────────────────────────────────────────────────────────────

from fraud_rules_engine import RulesEngine
from fraud_preprocessing import PreprocessingPipeline
from fraud_autoencoder import AEScorer
from fraud_isolation_forest import (
    ISOScorer,
    merge_ae_iso,
    drop_low_features
)


# ============================================================
# DATABASE
# ============================================================

from database.transactions import insert_transaction

# ============================================================
# DRIFT MONITORING
# ============================================================

from src.drift_monitoring.drift_aggregate import (
    aggregate_drift
)





# ============================================================
# SHAP IMPORTS
# ============================================================

from src.explainability.shap_explainer import (
    generate_shap_explanation
)

from src.explainability.shap_monitor import (
    store_shap_results
)


# ============================================================
# SEVERITY DATABASE LOGGING
# ============================================================

from database.severity_logs import (
    log_low_severity,
    log_medium_severity
)

# ============================================================
# FRAUD PIPELINE
# ============================================================

class FraudPipeline:

    def __init__(self):

        self.rules_engine = None
        self.preprocessor = None
        self.ae_scorer    = None
        self.iso_scorer   = None
        self.xgb_model    = None
        self.xgb_features = None

    # ========================================================
    # LOAD PIPELINE
    # ========================================================

    @classmethod
    def load(cls, saved_models_dir=None):

        sm = (
            Path(saved_models_dir)
            if saved_models_dir
            else SAVED_MODELS
        )

        obj = cls()

        print("=" * 60)
        print("Loading FraudPipeline ...")
        print("=" * 60)

        # ====================================================
        # RULES ENGINE
        # ====================================================

        obj.rules_engine = RulesEngine.load(
            sm / "rules_engine.pkl"
        )

        # ====================================================
        # PREPROCESSOR
        # ====================================================

        obj.preprocessor = PreprocessingPipeline.load(
            sm / "preprocessing.pkl"
        )

        # ====================================================
        # AUTOENCODER
        # ====================================================

        obj.ae_scorer = AEScorer.load(

            scaler_path = sm / "scaler.pkl",

            model_path = sm / "autoencoder_model.keras",

            threshold_path = sm / "ae_threshold.pkl",

            metadata_path = sm / "ae_metadata.pkl"
        )

        # ====================================================
        # ISOLATION FOREST
        # ====================================================

        obj.iso_scorer = ISOScorer.load(

            scaler_path = sm / "iso_scaler.pkl",

            model_path = sm / "isolation_forest.pkl",

            features_path = sm / "feature_columns.pkl"
        )

        # ====================================================
        # XGBOOST MODEL
        # ====================================================

        xgb_path = sm / "fraud_model.sav"

        try:

            obj.xgb_model = joblib.load(xgb_path)

            print(
                f">> XGB model loaded (joblib) : {xgb_path}"
            )

        except Exception:

            with open(xgb_path, 'rb') as f:

                obj.xgb_model = pickle.load(f)

            print(
                f">> XGB model loaded (pickle) : {xgb_path}"
            )

        # ====================================================
        # FEATURE COLUMNS
        # ====================================================

        with open(
            sm / "xgb_feature_columns.pkl",
            'rb'
        ) as f:

            raw = pickle.load(f)

        obj.xgb_features = (

            raw.get(
                "feature_columns",
                raw.get(
                    "columns",
                    list(raw.values())[0]
                )
            )

            if isinstance(raw, dict)

            else list(raw)
        )

        print(
            f">> XGB feature columns : {len(obj.xgb_features)}"
        )

        print("=" * 60)
        print("All artifacts loaded successfully.")
        print("=" * 60)

        return obj

    # ========================================================
    # ALIGN FEATURES
    # ========================================================

    def _align_for_xgb(self, df):

        df = df.copy()

        missing = [

            c for c in self.xgb_features

            if c not in df.columns
        ]

        if missing:

            df = pd.concat(

                [
                    df,

                    pd.DataFrame(
                        0,
                        index=df.index,
                        columns=missing
                    )
                ],

                axis=1
            )

        return df[self.xgb_features]

    # ========================================================
    # PREDICT
    # ========================================================

    def predict(self, raw_df):

        """
        Input:
            raw_df -> raw transaction dataframe

        Output:
            prediction results
        """

        # ====================================================
        # RULES ENGINE
        # ====================================================

        rules_out = self.rules_engine.transform(
            raw_df
        )

        # ====================================================
        # PREPROCESSING
        # ====================================================

        pp_out = self.preprocessor.transform(
            rules_out
        )

        # ====================================================
        # AE SCORE
        # ====================================================

        ae_out = self.ae_scorer.transform(
            pp_out
        )

        # ====================================================
        # ISO SCORE
        # ====================================================

        iso_out = self.iso_scorer.transform(
            pp_out
        )

        # ====================================================
        # MERGE AE + ISO
        # ====================================================

        merged = merge_ae_iso(
            ae_out,
            iso_out
        )

        # ====================================================
        # DROP LOW FEATURES
        # ====================================================

        dropped = drop_low_features(
            merged
        )

        # ====================================================
        # ALIGN XGB FEATURES
        # ====================================================

        xgb_input = self._align_for_xgb(
            dropped
        )

        # ====================================================
        # XGB PREDICTION
        # ====================================================

        preds = self.xgb_model.predict(
            xgb_input
        )

        probs = self.xgb_model.predict_proba(
            xgb_input
        )[:, 1]

        # ====================================================
        # SHAP EXPLANATION
        # ====================================================

        shap_result = generate_shap_explanation(
            xgb_input
        )

        # ====================================================
        # TRANSACTION ID
        # ====================================================

        transaction_id = (

            raw_df["TransactionID"].iloc[0]

            if "TransactionID" in raw_df.columns

            else None
        )

        # ====================================================
        # STORE SHAP RESULTS
        # ====================================================

        store_shap_results(

            transaction_id,

            shap_result["explanation_df"]
        )

        # ====================================================
        # PREPARE DB RECORD
        # ====================================================

        db_record = raw_df.iloc[0].to_dict()

        db_record["prediction"] = int(preds[0])

        db_record["probability"] = round(
            float(probs[0]),
            6
        )

        db_record["label"] = (

            "FRAUD"

            if preds[0] == 1

            else "LEGIT"
        )

        # ====================================================
        # INSERT TRANSACTION
        # ====================================================

        row_count = insert_transaction(
            db_record
        )

        # ====================================================
        # # DRIFT CHECK
        # # ====================================================

        if row_count % 500 == 0:

            print("=" * 60)

            print("500 transactions reached.")

            print("Running drift monitoring...")

            print("=" * 60)

            # =================================================
            # RUN DRIFT
            # =================================================

            drift_result = aggregate_drift()

            severity = determine_severity(
                drift_result["final_drift_score"]
            )

            print("Drift Result :", drift_result)

            print("Severity :", severity)

            # =================================================
            # LOW SEVERITY
            # =================================================

            if severity == "LOW":

                log_low_severity(
                    drift_result
                )

            # =================================================
            # MEDIUM SEVERITY
            # =================================================

            elif severity == "MEDIUM":

                log_medium_severity(
                    drift_result
                )

            # =================================================
            # HIGH SEVERITY
            # =================================================

            else:

                print("=" * 60)

                print("HIGH SEVERITY DETECTED")

                print("Feedback Loop")

                print("=" * 60)

        else:

            print(
                f"Transaction stored successfully. "
                f"Current rows : {row_count}"
            )

        # ====================================================
        # RETURN RESULTS
        # ====================================================

        return [

            {
                "prediction": int(preds[i]),

                "probability": round(
                    float(probs[i]),
                    6
                ),

                "label": (
                    "FRAUD"
                    if preds[i] == 1
                    else "LEGIT"
                )
            }

            for i in range(len(raw_df))
        ]


# ============================================================
# QUICK TEST
# ============================================================

if __name__ == "__main__":

    dataset_path = (
        _REPO_ROOT / "dataset/dataset.csv"
    )

    df = pd.read_csv(dataset_path)

    print(f"Dataset shape : {df.shape}")

    pipeline = FraudPipeline.load()

    for label, mask in [

        ("FRAUD", df['isFraud'] == 1),

        ("LEGIT", df['isFraud'] == 0)
    ]:

        row = (

            df[mask]

            .sample(1, random_state=42)

            .drop(
                columns=['isFraud'],
                errors='ignore'
            )
        )

        result = pipeline.predict(row)

        print(
            f"\n[{label}] "
            f"prediction={result[0]['label']} "
            f"prob={result[0]['probability']}"
        )


# ============================================================
# BULK TRANSACTION TEST
# ============================================================

if __name__ == "__main__":

    dataset_path = (
        _REPO_ROOT / "dataset/dataset.csv"
    )

    # ========================================================
    # LOAD DATASET
    # ========================================================

    df = pd.read_csv(dataset_path)

    print("=" * 60)
    print(f"Dataset shape : {df.shape}")
    print("=" * 60)

    # ========================================================
    # REMOVE TARGET COLUMN
    # ========================================================

    prediction_df = df.drop(
        columns=["isFraud"],
        errors="ignore"
    )

    # ========================================================
    # TAKE FIRST 500 TRANSACTIONS
    # ========================================================

    prediction_df = prediction_df.head(500)

    print(
        f"Running predictions on "
        f"{len(prediction_df)} transactions..."
    )

    print("=" * 60)

    # ========================================================
    # LOAD PIPELINE
    # ========================================================

    pipeline = FraudPipeline.load()

    # ========================================================
    # LOOP THROUGH TRANSACTIONS
    # ========================================================

    for idx in range(len(prediction_df)):

        row = prediction_df.iloc[[idx]]

        result = pipeline.predict(row)

        transaction_id = (

            row["TransactionID"].iloc[0]

            if "TransactionID" in row.columns

            else idx
        )

        print(
            f"[{idx+1}/500] "
            f"TransactionID={transaction_id} | "
            f"Prediction={result[0]['label']} | "
            f"Probability={result[0]['probability']}"
        )

    print("=" * 60)
    print("500 transaction predictions completed.")
    print("=" * 60)