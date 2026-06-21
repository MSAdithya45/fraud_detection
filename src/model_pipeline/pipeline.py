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
# Also expose the repo root so `database.*` and `src.*` resolve when this
# file is run directly (`python src/model_pipeline/pipeline.py`).
sys.path.insert(0, str(_REPO_ROOT))


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

from database.transactions import (
    store_processed_transaction
)

# ============================================================
# DRIFT MONITORING
# ============================================================

from src.drift_monitoring.drift_aggregate import (
    aggregate_drift
)

from src.drift_monitoring.severity_router import (
    determine_severity)


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
    log_medium_severity,
    log_high_severity
)

from database.raw_transactions import (
    store_raw_transaction,
)


# Number of buffered transactions that triggers a drift run + chunk flush.
DRIFT_BATCH_SIZE = 30


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

        rules_out = self.rules_engine.transform(raw_df)
        print("rules_out TransactionID exists:", "TransactionID" in rules_out.columns)

        # ====================================================
        # PREPROCESSING
        # ====================================================

        pp_out = self.preprocessor.transform(rules_out)
        print("pp_out TransactionID exists:", "TransactionID" in pp_out.columns)

        # ====================================================
        # AE SCORE
        # ====================================================

        ae_out = self.ae_scorer.transform(pp_out)
        print("ae_out TransactionID exists:", "TransactionID" in ae_out.columns)

        # ====================================================
        # ISO SCORE
        # ====================================================

        iso_out = self.iso_scorer.transform(pp_out)
        print("iso_out TransactionID exists:", "TransactionID" in iso_out.columns)

        # ====================================================
        # MERGE AE + ISO
        # ====================================================

        merged = merge_ae_iso(ae_out, iso_out)
        print("merged TransactionID exists:", "TransactionID" in merged.columns)

        # ====================================================
        # DROP LOW FEATURES
        # ====================================================

        dropped = drop_low_features(merged)
        print("dropped TransactionID exists:", "TransactionID" in dropped.columns)

        # ====================================================
        # ALIGN XGB FEATURES
        # ====================================================

        xgb_input = self._align_for_xgb(dropped)
        print("xgb_input TransactionID exists:", "TransactionID" in xgb_input.columns)

        # ====================================================
        # XGB PREDICTION
        # ====================================================

        preds = self.xgb_model.predict(xgb_input)

        probs = self.xgb_model.predict_proba(xgb_input)[:, 1]


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
        # PREPARE DB RECORD FOR STORAGE
        # ====================================================

        # Use full aligned XGB input schema
        db_record = xgb_input.copy()
        # ====================================================
        # ADD TRANSACTION ID BACK
        # ====================================================

        if "TransactionID" in raw_df.columns:

            db_record = pd.concat(

                [
                    raw_df[["TransactionID"]].reset_index(drop=True),

                    db_record.reset_index(drop=True)
                ],

                axis=1
            )

        # ====================================================
        # ADD PREDICTION OUTPUTS
        # ====================================================

        db_record["prediction"] = preds

        db_record["probability"] = [
            round(float(prob), 6)
            for prob in probs
        ]

        db_record["label"] = [
            "FRAUD" if pred == 1 else "LEGIT"
            for pred in preds
        ]

        # ====================================================
        # STORE RAW + PROCESSED TOGETHER
        # Raw is stored here (not at the start) so that if any
        # processing step above fails, NEITHER staging buffer gets
        # the row — keeping raw and processed staging in lockstep.
        # ====================================================

        store_raw_transaction(raw_df)

        row_count = store_processed_transaction(
            db_record
        )

        # ====================================================
        # # DRIFT CHECK  (every 30 buffered rows)
        # # ====================================================

        if row_count >= DRIFT_BATCH_SIZE:

            print("=" * 60)

            print(f"{DRIFT_BATCH_SIZE} transactions reached.")

            print("Running drift monitoring...")

            print("=" * 60)

            # =================================================
            # RUN DRIFT
            # =================================================

            drift_result = aggregate_drift()

            severity = determine_severity(
                drift_result.iloc[0].to_dict()
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

                print("=" * 60)

                log_high_severity(
                    drift_result
    )

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