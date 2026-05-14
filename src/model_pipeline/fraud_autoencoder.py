# src/pipeline/fraud_autoencoder.py

import numpy as np
import pandas as pd
import pickle
import warnings
from pathlib import Path

warnings.filterwarnings('ignore')

_REPO_ROOT   = Path(__file__).resolve().parents[2]
SAVED_MODELS = _REPO_ROOT / "saved_models"
SAVED_MODELS.mkdir(parents=True, exist_ok=True)


class AEScorer:

    def __init__(self):
        self.scaler          = None
        self.autoencoder     = None
        self.ae_threshold    = None
        self.feature_columns = None
        self.train_errors    = None

    # ── LOAD ─────────────────────────────────────────────────────────────────

    @classmethod
    def load(cls,
             scaler_path    = None,
             model_path     = None,
             threshold_path = None,
             metadata_path  = None):

        import tensorflow as tf

        obj = cls()
        sm  = SAVED_MODELS

        scaler_path    = Path(scaler_path)    if scaler_path    else sm / "scaler.pkl"
        model_path     = Path(model_path)     if model_path     else sm / "autoencoder_model.keras"
        threshold_path = Path(threshold_path) if threshold_path else sm / "ae_threshold.pkl"
        metadata_path  = Path(metadata_path)  if metadata_path  else sm / "ae_metadata.pkl"

        with open(scaler_path, 'rb') as f:
            obj.scaler = pickle.load(f)
        print(f">> [AEScorer] Scaler loaded     : {scaler_path}")

        obj.autoencoder = tf.keras.models.load_model(model_path)
        print(f">> [AEScorer] Model loaded      : {model_path}")

        with open(threshold_path, 'rb') as f:
            obj.ae_threshold = pickle.load(f)
        print(f">> [AEScorer] Threshold loaded  : {obj.ae_threshold:.6f}")

        with open(metadata_path, 'rb') as f:
            metadata = pickle.load(f)
        obj.feature_columns = metadata.get("feature_columns")
        obj.train_errors    = metadata.get("train_errors")
        print(f">> [AEScorer] Feature cols      : {len(obj.feature_columns)}")

        return obj

    # ── ALIGN ────────────────────────────────────────────────────────────────

    def _align(self, df):
        df      = df.copy()
        missing = [c for c in self.feature_columns if c not in df.columns]
        if missing:
            df = pd.concat([df, pd.DataFrame(0, index=df.index, columns=missing)], axis=1)
        return df[self.feature_columns]

    # ── TRANSFORM ────────────────────────────────────────────────────────────

    def transform(self, preprocessed_df, batch_size=2048):
        df_aligned = self._align(preprocessed_df).fillna(0)
        X_scaled   = self.scaler.transform(df_aligned)
        X_pred     = self.autoencoder.predict(X_scaled, batch_size=batch_size, verbose=0)
        raw_mse    = np.mean(np.power(X_scaled - X_pred, 2), axis=1)
        ae_score   = np.log1p(raw_mse)

        if self.train_errors is not None:
            ae_percentile = np.array([np.mean(self.train_errors <= e) for e in raw_mse])
        else:
            ae_percentile = np.full(len(raw_mse), np.nan)

        very_high_ae = (ae_percentile > 0.95).astype(int)

        result = pd.concat([preprocessed_df.copy(), pd.DataFrame({
            'ae_score': ae_score, 'ae_percentile': ae_percentile, 'very_high_ae': very_high_ae,
        }, index=preprocessed_df.index)], axis=1)

        print(f">> [AEScorer] transform done. Shape: {result.shape}")
        return result

    # ── PREDICT ──────────────────────────────────────────────────────────────

    def predict(self, preprocessed_df, batch_size=2048):
        df_aligned       = self._align(preprocessed_df)
        X_scaled         = self.scaler.transform(df_aligned)
        X_pred           = self.autoencoder.predict(X_scaled, batch_size=batch_size, verbose=0)
        raw_mse          = np.mean(np.power(X_scaled - X_pred, 2), axis=1)
        fraud_prediction = (raw_mse > self.ae_threshold).astype(int)
        return {
            'ae_score': np.log1p(raw_mse),
            'raw_mse': raw_mse,
            'fraud_prediction': fraud_prediction,
        }