# FraudLens — Feedback Loop Strategy

> Filename note: kept as `feeback_loop_strategy.md` to match the existing file;
> the topic is the **feedback loop**.

The feedback loop turns live scoring + drift monitoring into a continuous
improvement cycle: surface the riskiest chunks, let analysts label/investigate
them, and feed verified data back into retraining.

---

## 1. The loop

```
        ┌──────────────────────────────────────────────────────────┐
        │                                                          │
        ▼                                                          │
  Score chunk ─▶ Drift analysis ─▶ Severity routing                │
  (30 txns)        (PSI+KS)         LOW / MED / HIGH                │
                                       │                            │
                     ┌─────────────────┼──────────────────┐        │
                     ▼                 ▼                  ▼         │
              drift_low_severity  drift_medium...   drift_high...   │
                     │                 │                  │         │
                     └──────────── analyst review ────────┘         │
                                       │                            │
                          download chunk dataset (ZIP)              │
                                       │                            │
                          label / correct outcomes                 │
                                       │                            │
                              retrain models  ──────────────────────┘
```

---

## 2. Severity tiers as a triage queue

| Tier | Meaning | Suggested action |
|------|---------|------------------|
| **LOW** | distribution close to training | monitor only; no action |
| **MEDIUM** | moderate shift / watchlist | periodic review; candidate for relabeling |
| **HIGH** | strong shift / likely emerging fraud pattern | prioritize investigation + retraining |

Each tier is a separate table, so analysts can work the **HIGH** queue first.

---

## 3. From flagged chunk to training data

Every drift row stores the chunk's `transaction_ids`. On the **Drift Analysis**
page, the per-row **Download** button calls
`GET /drift/{severity}/{id}/download`, which:

1. reads that row's `transaction_ids`,
2. pulls the matching rows from `raw_transactions_history` **and**
   `processed_transactions_history`,
3. returns a **ZIP** (`raw_<sev>_<id>.csv` + `processed_<sev>_<id>.csv`).

The **raw** CSV is what you relabel and feed into a retraining run; the
**processed** CSV preserves the exact features/scores the model saw, useful for
post-hoc analysis and reproducing the decision.

Full-history exports (`/history/raw`, `/history/processed`) provide the complete
labeled corpus over time.

---

## 4. Retraining outline

1. Export HIGH/MEDIUM chunks (or the full raw history).
2. Apply ground-truth labels (analyst decisions / chargeback outcomes).
3. Retrain the ensemble (XGBoost + AE + ISO) and refresh `saved_models/`.
4. Recompute drift baselines (`baseline/*.json`) from the new training
   distribution so drift is measured against the current model.
5. Redeploy the backend image.

---

## 5. Explainability supports the loop

- **SHAP** (`developer_explanations`) shows *why* each transaction scored as it
  did — analysts validate or dispute the drivers.
- **LLM** (`llm_explanations`, Gemini) narrates the decision for faster review.

Together these shorten the label-and-correct step, which is the bottleneck of any
fraud feedback loop.

---

## 6. Current status & next steps

- ✅ Severity routing + per-chunk capture + downloadable datasets.
- ✅ SHAP + LLM explanations per transaction.
- ⏳ Analyst labeling UI (currently done offline on the downloaded CSVs).
- ⏳ Automated retraining trigger from accumulated HIGH chunks.
- ⏳ Baseline auto-refresh after retraining.
