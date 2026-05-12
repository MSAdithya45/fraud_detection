# src/pipeline/fraud_isolation_forest.py

import numpy as np
import pandas as pd
import pickle
import warnings
from pathlib import Path

warnings.filterwarnings('ignore')

_REPO_ROOT   = Path(__file__).resolve().parents[2]
SAVED_MODELS = _REPO_ROOT / "saved_models"
SAVED_MODELS.mkdir(parents=True, exist_ok=True)

LOW_IMPORTANCE_FEATURES = [
    'V98', 'V100', 'V103', 'V104', 'V106', 'rule_night_txn', 'rule_email_score',
    'V25', 'V27', 'V28', 'V29', 'V241', 'V240', 'V53_is_missing',
    'rule_high_velocity', 'rule_card_velocity', 'rule_addr_missing',
    'rule_device_change', 'rule_id_missing', 'rule_risky_product',
    'rule_high_C2', 'rule_score_norm', 'id_04_is_missing', 'id_09_is_missing',
    'id_10_is_missing', 'id_13_is_missing', 'id_18_is_missing',
    'id_32_is_missing', 'addr1_is_missing', 'V30', 'V338_is_missing',
    'ae_percentile', 'V333_is_missing', 'V334_is_missing', 'V335_is_missing',
    'V261_is_missing', 'V262_is_missing', 'V263_is_missing', 'V264_is_missing',
    'V265_is_missing', 'V266_is_missing', 'V267_is_missing', 'V268_is_missing',
    'V269_is_missing', 'V91', 'V274_is_missing', 'V275_is_missing',
    'V276_is_missing', 'V277_is_missing', 'V337_is_missing', 'V68', 'V69', 'V70',
    'V75', 'V41', 'V48', 'V325', 'V83', 'V89', 'V90', 'V273_is_missing',
    'V31_is_missing', 'V32_is_missing', 'V33_is_missing', 'V34_is_missing',
    'V35_is_missing', 'V36_is_missing', 'V37_is_missing', 'V38_is_missing',
    'V39_is_missing', 'V40_is_missing', 'V41_is_missing', 'V42_is_missing',
    'V43_is_missing', 'V44_is_missing', 'addr2_is_missing', 'V46_is_missing',
    'V47_is_missing', 'V48_is_missing', 'V49_is_missing', 'V50_is_missing',
    'V51_is_missing', 'V52_is_missing', 'V278_is_missing', 'V54_is_missing',
    'V55_is_missing', 'V56_is_missing', 'V57_is_missing', 'V58_is_missing',
    'V59_is_missing', 'V60_is_missing', 'V45_is_missing', 'dist2_is_missing',
    'D4_is_missing', 'D5_is_missing', 'D6_is_missing', 'D7_is_missing',
    'D8_is_missing', 'D9_is_missing', 'D10_is_missing', 'D12_is_missing',
    'D13_is_missing', 'D14_is_missing', 'D15_is_missing', 'V12_is_missing',
    'V13_is_missing', 'V30_is_missing', 'V15_is_missing', 'V16_is_missing',
    'V17_is_missing', 'V18_is_missing', 'V19_is_missing', 'V20_is_missing',
    'V21_is_missing', 'V22_is_missing', 'V23_is_missing', 'V24_is_missing',
    'V25_is_missing', 'V26_is_missing', 'V27_is_missing', 'V28_is_missing',
    'V29_is_missing', 'V14_is_missing',
]


class ISOScorer:

    def __init__(self):
        self.scaler          = None
        self.iso_model       = None
        self.feature_columns = None

    # ── LOAD ─────────────────────────────────────────────────────────────────

    @classmethod
    def load(cls, scaler_path=None, model_path=None, features_path=None):
        obj = cls()
        sm  = SAVED_MODELS

        scaler_path   = Path(scaler_path)   if scaler_path   else sm / "iso_scaler.pkl"
        model_path    = Path(model_path)    if model_path    else sm / "isolation_forest.pkl"
        features_path = Path(features_path) if features_path else sm / "feature_columns.pkl"

        with open(scaler_path, 'rb') as f:
            obj.scaler = pickle.load(f)
        print(f">> [ISOScorer] Scaler loaded    : {scaler_path}")

        with open(model_path, 'rb') as f:
            obj.iso_model = pickle.load(f)
        print(f">> [ISOScorer] ISO model loaded : {model_path}")

        with open(features_path, 'rb') as f:
            raw = pickle.load(f)
        obj.feature_columns = (
            raw.get("feature_columns", raw.get("columns")) if isinstance(raw, dict) else raw
        )
        print(f">> [ISOScorer] Feature cols     : {len(obj.feature_columns)}")
        return obj

    # ── ALIGN / TRANSFORM ────────────────────────────────────────────────────

    def _align(self, df):
        df = df.copy()
        missing = [c for c in self.feature_columns if c not in df.columns]
        if missing:
            df = pd.concat([df, pd.DataFrame(0, index=df.index, columns=missing)], axis=1)
        return df[self.feature_columns]

    def transform(self, preprocessed_df):
        df_aligned = self._align(preprocessed_df)
        X_scaled   = self.scaler.transform(df_aligned)
        iso_score  = -self.iso_model.decision_function(X_scaled)
        result     = preprocessed_df.copy()
        result['iso_score'] = iso_score
        print(f">> [ISOScorer] transform done. Shape: {result.shape} | iso_score={iso_score[0]:.6f}")
        return result


# ── MERGE / DROP HELPERS ─────────────────────────────────────────────────────

def merge_ae_iso(ae_result_df, iso_result_df):
    ae_new  = ['ae_score', 'ae_percentile', 'very_high_ae']
    base    = ae_result_df.drop(columns=ae_new, errors='ignore').copy()
    for col in ae_new:
        if col in ae_result_df.columns:
            base[col] = ae_result_df[col].values
    if 'iso_score' in iso_result_df.columns:
        base['iso_score'] = -(iso_result_df['iso_score'].values)
    print(f">> [merge_ae_iso] Merged shape: {base.shape}")
    return base


def drop_low_features(merged_df):
    present = [c for c in LOW_IMPORTANCE_FEATURES if c in merged_df.columns]
    result  = merged_df.drop(columns=present, errors='ignore')
    print(f">> [drop_low_features] Dropped {len(present)} cols. Output shape: {result.shape}")
    return result