# src/pipeline/fraud_preprocessing.py

import pandas as pd
import numpy as np
import pickle
import warnings
from pathlib import Path

warnings.filterwarnings('ignore')

_REPO_ROOT   = Path(__file__).resolve().parents[2]
SAVED_MODELS = _REPO_ROOT / "saved_models"
SAVED_MODELS.mkdir(parents=True, exist_ok=True)


class PreprocessingPipeline:

    def __init__(self):
        self.cols_to_drop        = []
        self.cat_cols            = []
        self.num_cols            = []
        self.train_missing_ratio = {}
        self.freq_maps           = {}

    # ── FIT ──────────────────────────────────────────────────────────────────

    def fit(self, train_df, target_col='isFraud'):
        print(">> [Preprocessing] Starting fit ...")
        df = train_df.copy().drop(columns=[target_col], errors='ignore')

        null_percent    = df.isnull().mean() * 100
        cols_null       = null_percent[null_percent >= 80].index.tolist()
        cols_constant   = [c for c in df.columns if df[c].nunique(dropna=False) <= 1]
        cols_near_const = [
            c for c in df.columns
            if df[c].value_counts(normalize=True, dropna=False).iloc[0] >= 0.99
        ]
        self.cols_to_drop = list(set(cols_null) | set(cols_constant) | set(cols_near_const))

        print(f"   Null cols (>=80%)  : {len(cols_null)}")
        print(f"   Constant cols      : {len(cols_constant)}")
        print(f"   Near-constant cols : {len(cols_near_const)}")
        print(f"   Total to drop      : {len(self.cols_to_drop)}")

        df = df.drop(columns=self.cols_to_drop, errors='ignore')
        print(f"   Shape after drop   : {df.shape}")

        self.cat_cols = df.select_dtypes(include=['object']).columns.tolist()
        self.num_cols = df.select_dtypes(include=['int64', 'float64']).columns.tolist()
        print(f"   Categorical cols   : {len(self.cat_cols)}")
        print(f"   Numerical cols     : {len(self.num_cols)}")

        df[self.cat_cols] = df[self.cat_cols].fillna('Missing')

        self.train_missing_ratio = {col: df[col].isnull().mean() for col in self.num_cols}
        missing_flag_cols = [c for c, r in self.train_missing_ratio.items() if r > 0.05]
        print(f"   Missing-flag cols  : {len(missing_flag_cols)}")

        self.freq_maps = {col: df[col].value_counts(normalize=True) for col in self.cat_cols}

        print(">> [Preprocessing] Fit complete.")
        return self

    # ── TRANSFORM ────────────────────────────────────────────────────────────

    def transform(self, incoming_df):
        df = incoming_df.copy().drop(columns=['isFraud'], errors='ignore')

        df = df.drop(columns=[c for c in self.cols_to_drop if c in df.columns], errors='ignore')

        for col in self.cat_cols:
            if col in df.columns:
                df[col] = df[col].fillna('Missing')

        flag_dict = {
            f'{col}_is_missing': df[col].isnull().astype(int)
            for col in self.num_cols
            if col in df.columns and self.train_missing_ratio.get(col, 0) > 0.05
        }
        if flag_dict:
            df = pd.concat([df, pd.DataFrame(flag_dict, index=df.index)], axis=1)

        freq_dict = {
            col + '_freq': df[col].map(self.freq_maps.get(col, {})).fillna(0)
            for col in self.cat_cols
            if col in df.columns
        }
        if freq_dict:
            df = pd.concat([df, pd.DataFrame(freq_dict, index=df.index)], axis=1)

        print("\n>> [Preprocessing] Dropping categorical columns:", self.cat_cols)
        df = df.drop(columns=[c for c in self.cat_cols if c in df.columns], errors='ignore')

        cols_to_remove = [
            'D3', 'D2',
            'id_06_is_missing', 'D2_is_missing', 'D3_is_missing', 'id_05_is_missing',
        ]
        df = df.drop(columns=[c for c in cols_to_remove if c in df.columns], errors='ignore')

        df['email_fraud_rate_is_missing'] = 0

        print(f">> [Preprocessing] transform done. Output shape: {df.shape}")
        return df

    # ── SAVE / LOAD ──────────────────────────────────────────────────────────

    def save(self, filepath=None):
        path = Path(filepath) if filepath else SAVED_MODELS / "preprocessing.pkl"
        with open(path, 'wb') as f:
            pickle.dump(self, f)
        print(f">> [Preprocessing] Saved → {path}")

    @classmethod
    def load(cls, filepath=None):
        path = Path(filepath) if filepath else SAVED_MODELS / "preprocessing.pkl"
        with open(path, 'rb') as f:
            obj = pickle.load(f)
        print(f">> [Preprocessing] Loaded ← {path}")
        return obj