# FraudLens — Drift Detection Strategy

FraudLens watches for **data drift** — a shift in the live transaction
distribution away from what the models were trained on. Drift is evaluated per
**chunk** and routed to a severity tier that decides how the chunk is handled.

---

## 1. When drift runs

- Every scored transaction lands in `processed_transactions_staging`.
- When the buffer reaches **`DRIFT_BATCH_SIZE` (30)** rows
  (`src/model_pipeline/pipeline.py`), a drift analysis runs on that chunk.
- After analysis the chunk is flushed to history and the buffer is emptied, so
  each run covers a fresh 30-transaction window.

> 30 is a deliberately small window for testing/demos. Production would use a
> larger window (e.g. 500); change `DRIFT_BATCH_SIZE` in `pipeline.py`.

---

## 2. The four drift components

Each component compares the current chunk against a stored baseline
(`baseline/*.json`) using two statistics, averaged:

```
component_drift = (PSI + KS) / 2
```

- **PSI** (Population Stability Index) — bin-wise distribution change.
- **KS** (Kolmogorov–Smirnov) — max CDF distance (`scipy.stats.ks_2samp`).

| Component | Signal monitored | Baseline |
|-----------|------------------|----------|
| `rules_drift_score` | rule score | `baseline/rules_baseline.json` |
| `iso_drift_score` | isolation-forest score | `baseline/iso_baseline.json` |
| `ae_drift_score` | autoencoder score | `baseline/ae_baseline.json` |
| `feature_drift_score` | per-feature mean | `baseline/feature_baselines.json` |

---

## 3. Weighted final score

`src/drift_monitoring/drift_aggregate.py`:

```
final_drift_score = 0.33 * rules
                  + 0.15 * iso
                  + 0.07 * ae
                  + 0.45 * feature
```

Feature drift dominates (0.45) because broad feature movement is the strongest
indicator of population shift; rules add domain weight (0.33); the anomaly
scores contribute the rest.

---

## 4. Severity routing

`src/drift_monitoring/severity_router.py`:

| Severity | Condition | Table |
|----------|-----------|-------|
| **LOW** | `final_drift_score < 0.10` | `drift_low_severity` |
| **MEDIUM** | `0.10 ≤ score ≤ 0.5` | `drift_medium_severity` |
| **HIGH** | `score > 0.5` | `drift_high_severity` |

Each run writes **one row** to the matching table:
`transaction_ids` (the chunk's IDs, JSON), the five drift scores,
`monitoring_status`, `created_at`.

---

## 5. What analysts see

The **Drift Analysis** page:
- Tabs for Low / Medium / High, each listing chunk drift scores + timestamp
  (the raw `transaction_ids` list is hidden to keep it readable).
- Per-row **Download** → a ZIP of the chunk's raw + processed rows (pulled from
  the history tables by TransactionID) for offline investigation / relabeling.
- Top-level **Download full raw / preprocessed history** as CSV.

---

## 6. Notes & limitations

- Baselines are currently sampled with `np.random.normal(...)` per run (no fixed
  seed), so scores are **non-deterministic** across runs on identical data.
  Pin a seed or freeze baseline arrays for reproducibility.
- The MEDIUM band is inclusive at both ends (`< 0.10` LOW, `≤ 0.5` MEDIUM).
- Drift reads the chunk via `database/batch_loader.load_recent_transactions()`,
  which now points at `processed_transactions_staging`.
