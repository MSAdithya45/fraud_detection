# src/pipeline/fraud_rules_engine.py

import pandas as pd
import numpy as np
import pickle
import warnings
from pathlib import Path

warnings.filterwarnings('ignore')

# ── resolve saved_models/ relative to this file ──────────────────────────────
_REPO_ROOT    = Path(__file__).resolve().parents[2]   # project_root/
SAVED_MODELS  = _REPO_ROOT / "saved_models"
SAVED_MODELS.mkdir(parents=True, exist_ok=True)


class RulesEngine:

    def __init__(self):
        self.card_avg_map        = None
        self.global_amt_mean     = None
        self.card_device_map     = None
        self.global_device_count = None
        self.email_stats         = None
        self.high_risk_domains   = None
        self.medium_risk_domains = None
        self.risky_products      = None
        self.c1_95               = None
        self.c2_95               = None
        self._raw_train_df       = None

    # ── FIT ──────────────────────────────────────────────────────────────────

    def fit(self, train_df, target_col='isFraud'):
        print(">> [RulesEngine] Fitting ...")
        df = train_df.copy()

        self._raw_train_df = df[
            [c for c in ['card1', 'DeviceInfo', 'TransactionDT'] if c in df.columns]
        ].copy()

        self.email_stats = (
            df.groupby('R_emaildomain')[target_col]
              .agg(['count', 'mean'])
        )
        self.high_risk_domains = self.email_stats[
            (self.email_stats['mean'] > 0.3) & (self.email_stats['count'] > 50)
        ].index
        self.medium_risk_domains = self.email_stats[
            (self.email_stats['mean'] > 0.15) & (self.email_stats['count'] > 100)
        ].index

        self.card_avg_map        = df.groupby('card1')['TransactionAmt'].mean()
        self.global_amt_mean     = df['TransactionAmt'].mean()
        self.card_device_map     = df.groupby('card1')['DeviceInfo'].nunique()
        self.global_device_count = df['DeviceInfo'].nunique()

        product_fraud       = df.groupby('ProductCD')[target_col].mean()
        self.risky_products = product_fraud[product_fraud > 0.1].index

        self.c1_95 = df['C1'].quantile(0.95)
        self.c2_95 = df['C2'].quantile(0.95)

        print(">> [RulesEngine] Fit complete.")
        return self

    # ── TRANSFORM ────────────────────────────────────────────────────────────

    def transform(self, incoming_df):
        df  = incoming_df.copy()
        new = {}

        # 1-2. amounts
        if 'TransactionAmt' in df.columns:
            new['rule_high_amount']      = (df['TransactionAmt'] > 200).astype(int)
            new['rule_very_high_amount'] = (df['TransactionAmt'] > 500).astype(int)
        else:
            new['rule_high_amount']      = 0
            new['rule_very_high_amount'] = 0

        # 3-4. hour / night
        if 'TransactionDT' in df.columns:
            hour = (df['TransactionDT'] // 3600) % 24
            new['hour']           = hour
            new['rule_night_txn'] = ((hour >= 0) & (hour <= 5)).astype(int)
        else:
            new['hour']           = np.nan
            new['rule_night_txn'] = 0

        # 5. mobile
        if 'DeviceType' in df.columns:
            new['rule_mobile'] = (df['DeviceType'] == 'mobile').astype(int)
        else:
            new['rule_mobile'] = 0

        # 6. suspicious device
        if 'DeviceInfo' in df.columns:
            new['rule_suspicious_device'] = df['DeviceInfo'].isna().astype(int)
        else:
            new['rule_suspicious_device'] = 1

        # 7-11. email
        if 'R_emaildomain' in df.columns:
            r_email = df['R_emaildomain']
            new['rule_missing_email'] = r_email.isna().astype(int)
            new['rule_email_high']    = r_email.isin(self.high_risk_domains).astype(int)
            new['rule_email_medium']  = r_email.isin(self.medium_risk_domains).astype(int)
            new['rule_email_score']   = (
                new['rule_email_high'] * 30 + new['rule_email_medium'] * 15
            )
            new['email_fraud_rate'] = (
                r_email.map(self.email_stats['mean'])
                       .fillna(self.email_stats['mean'].mean())
            )
        else:
            new['rule_missing_email'] = 1
            new['rule_email_high']    = 0
            new['rule_email_medium']  = 0
            new['rule_email_score']   = 0
            new['email_fraud_rate']   = float(self.email_stats['mean'].mean())

        # 12-13. card avg / amt ratio
        if 'card1' in df.columns:
            card_avg = df['card1'].map(self.card_avg_map).fillna(self.global_amt_mean)
        else:
            card_avg = pd.Series(self.global_amt_mean, index=df.index)

        new['card_avg_amt'] = card_avg
        if 'TransactionAmt' in df.columns:
            new['amt_ratio'] = (
                df['TransactionAmt'] / card_avg.replace(0, np.nan)
            ).fillna(1.0)
        else:
            new['amt_ratio'] = 1.0

        # 14-19. velocity
        vel = self._compute_velocity(incoming_df)
        new['txn_count_1hr']      = vel['txn_count_1hr'].values
        new['rule_high_velocity'] = vel['rule_high_velocity'].values
        new['card_txn_count_1hr'] = vel['card_txn_count_1hr'].values
        new['rule_card_velocity'] = vel['rule_card_velocity'].values
        new['txn_gap']            = vel['txn_gap'].values
        new['rule_fast_txn']      = vel['rule_fast_txn'].values

        # 20. addr missing
        a1 = df['addr1'].isna() if 'addr1' in df.columns else pd.Series(True,  index=df.index)
        a2 = df['addr2'].isna() if 'addr2' in df.columns else pd.Series(True,  index=df.index)
        new['rule_addr_missing'] = (a1 | a2).astype(int)

        # 21. high dist
        if 'dist1' in df.columns:
            new['rule_high_dist'] = (df['dist1'].fillna(0) > 50).astype(int)
        else:
            new['rule_high_dist'] = 0

        # 22. email mismatch
        if 'P_emaildomain' in df.columns and 'R_emaildomain' in df.columns:
            new['rule_email_mismatch'] = (
                df['P_emaildomain'] != df['R_emaildomain']
            ).astype(int)
        else:
            new['rule_email_mismatch'] = 0

        # 23-24. device change
        if 'card1' in df.columns:
            card_dev = df['card1'].map(self.card_device_map).fillna(self.global_device_count)
        else:
            card_dev = pd.Series(self.global_device_count, index=df.index)
        new['card_device_count'] = card_dev
        new['rule_device_change'] = (card_dev > 3).astype(int)

        # 25-26. id missing
        id_cols = [c for c in df.columns if c.lower().startswith('id_')]
        id_missing = df[id_cols].isna().sum(axis=1) if id_cols else pd.Series(0, index=df.index)
        new['id_missing_count'] = id_missing
        new['rule_id_missing']  = (id_missing > 10).astype(int)

        # 27. risky product
        if 'ProductCD' in df.columns:
            new['rule_risky_product'] = df['ProductCD'].isin(self.risky_products).astype(int)
        else:
            new['rule_risky_product'] = 0

        # 28-29. C1 / C2
        new['rule_high_C1'] = (df['C1'] > self.c1_95).astype(int) if 'C1' in df.columns else 0
        new['rule_high_C2'] = (df['C2'] > self.c2_95).astype(int) if 'C2' in df.columns else 0

        # 30-31. composite score
        weights = {
            'rule_high_amount': 10, 'rule_very_high_amount': 20,
            'rule_night_txn': 15,   'rule_mobile': 5,
            'rule_suspicious_device': 25, 'rule_missing_email': 10,
            'rule_high_velocity': 30,     'rule_card_velocity': 30,
            'rule_addr_missing': 10,      'rule_high_dist': 20,
            'rule_email_mismatch': 15,    'rule_device_change': 25,
            'rule_id_missing': 20,        'rule_risky_product': 15,
            'rule_fast_txn': 30,          'rule_high_C1': 10,
            'rule_high_C2': 10,
        }
        score = sum(
            pd.Series(new[col], index=df.index).fillna(0) * w
            for col, w in weights.items()
        )
        new['rule_score']      = score
        new['rule_score_norm'] = score / max(score.max(), 1)

        new_df = pd.DataFrame(new, index=df.index)
        result = pd.concat([df, new_df], axis=1)
        assert new_df.shape[1] == 31, f"Expected 31 new cols, got {new_df.shape[1]}"
        print(f">> [RulesEngine] transform done: {df.shape[1]} → {result.shape[1]} cols")
        return result

    # ── VELOCITY (internal) ──────────────────────────────────────────────────

    def _compute_velocity(self, incoming_df):
        vel_cols   = ['card1', 'DeviceInfo', 'TransactionDT']
        train_slim = self._raw_train_df[[c for c in vel_cols if c in self._raw_train_df.columns]].copy()
        inc_slim   = incoming_df[[c for c in vel_cols if c in incoming_df.columns]].copy()
        n_train    = len(train_slim)

        full       = pd.concat([train_slim, inc_slim], axis=0).reset_index(drop=True)
        full['_dt']= pd.to_datetime(full['TransactionDT'], unit='s')

        full = full.sort_values(['DeviceInfo', '_dt'])
        if 'DeviceInfo' in full.columns and full['DeviceInfo'].notna().any():
            full['txn_count_1hr'] = (
                full.groupby('DeviceInfo', group_keys=False)
                    .apply(lambda g: g.rolling('3600s', on='_dt')['_dt'].count(),
                           include_groups=False)
            )
        else:
            full['txn_count_1hr'] = 1
        full['rule_high_velocity'] = (full['txn_count_1hr'] > 5).astype(int)

        full = full.sort_values(['card1', '_dt'])
        if 'card1' in full.columns and full['card1'].notna().any():
            full['card_txn_count_1hr'] = (
                full.groupby('card1', group_keys=False)
                    .apply(lambda g: g.rolling('3600s', on='_dt')['_dt'].count(),
                           include_groups=False)
            )
        else:
            full['card_txn_count_1hr'] = 1
        full['rule_card_velocity'] = (full['card_txn_count_1hr'] > 5).astype(int)

        full = full.sort_values(['card1', '_dt'])
        if 'card1' in full.columns and full['card1'].notna().any():
            full['txn_gap'] = full.groupby('card1')['_dt'].diff().dt.total_seconds()
        else:
            full['txn_gap'] = np.nan

        max_gap = full['txn_gap'].max()
        full['txn_gap']       = full['txn_gap'].fillna(max_gap if pd.notna(max_gap) else 999999)
        full['rule_fast_txn'] = (full['txn_gap'] < 60).astype(int)

        result_cols = [
            'txn_count_1hr', 'rule_high_velocity',
            'card_txn_count_1hr', 'rule_card_velocity',
            'txn_gap', 'rule_fast_txn',
        ]
        out       = full.iloc[n_train:][result_cols].copy()
        out.index = incoming_df.index
        return out

    # ── SAVE / LOAD ──────────────────────────────────────────────────────────

    def save(self, filepath=None):
        path = Path(filepath) if filepath else SAVED_MODELS / "rules_engine.pkl"
        with open(path, 'wb') as f:
            pickle.dump(self, f)
        print(f">> [RulesEngine] Saved → {path}")

    @classmethod
    def load(cls, filepath=None):
        path = Path(filepath) if filepath else SAVED_MODELS / "rules_engine.pkl"
        with open(path, 'rb') as f:
            obj = pickle.load(f)
        print(f">> [RulesEngine] Loaded ← {path}")
        return obj