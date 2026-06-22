# FraudLens — System Architecture

FraudLens is an AI-powered financial fraud-detection and AML platform. It scores
transactions with an ensemble of models, explains every prediction (SHAP +
LLM), continuously monitors for data drift, and gives analysts an investigation
dashboard.

---

## 1. High-level architecture

```
                        ┌───────────────────────────────────────────┐
                        │              React Frontend                │
                        │  (Vite + Tailwind, served by nginx)        │
                        │  Dashboard · Predictions · SHAP · LLM ·     │
                        │  Drift Analysis · Transactions             │
                        └───────────────────┬───────────────────────┘
                                            │ HTTPS / JSON (CORS)
                                            ▼
                        ┌───────────────────────────────────────────┐
                        │              FastAPI Backend               │
                        │                                            │
                        │  /predict (stream)  /transactions  /shap   │
                        │  /llm/{id}  /drift/*  /history/*           │
                        │                                            │
                        │  ┌──────────────── Pipeline ────────────┐  │
                        │  │ Rules → Preprocess → AE → ISO → XGB   │  │
                        │  │ → SHAP → (drift @ 30) → severity      │  │
                        │  └───────────────────────────────────────┘ │
                        └──────────┬─────────────────────┬───────────┘
                                   │                      │
                                   ▼                      ▼
                     ┌──────────────────────┐   ┌────────────────────┐
                     │  Supabase PostgreSQL  │   │   Gemini API       │
                     │  staging / history /  │   │ (LLM explanations) │
                     │  drift / SHAP / LLM   │   └────────────────────┘
                     └──────────────────────┘
```

---

## 2. Components

| Layer | Tech | Responsibility |
|-------|------|----------------|
| Frontend | React 18, Vite, Tailwind, Framer Motion, Recharts, React Query | Analyst dashboard, CSV upload, drift/SHAP/LLM views |
| API | FastAPI (uvicorn) | Inference orchestration, streaming, data access, downloads |
| ML pipeline | XGBoost, Keras autoencoder, Isolation Forest, rules engine, SHAP | Scoring + explainability |
| Drift monitoring | PSI + KS vs baselines | Detect distribution shift per chunk |
| LLM | Google Gemini API | Natural-language fraud explanations |
| Database | Supabase (PostgreSQL) | Staging/history, drift logs, SHAP, LLM cache |
| Schema/migrations | Prisma | Source-of-record for the stable tables |

---

## 3. The ensemble

A single transaction flows through five stages, each adding signal:

1. **Rules engine** — domain fraud rules (velocity, new country/merchant, night
   activity, VPN, etc.); appends rule columns (434 → 465).
2. **Preprocessing** — drops categorical/ID columns, encodes/scales (→ 613).
3. **Autoencoder (AE)** — reconstruction error → `ae_score` (anomaly signal).
4. **Isolation Forest (ISO)** — `iso_score` (anomaly signal; sign-corrected on merge).
5. **XGBoost** — consumes the aligned feature set (incl. AE/ISO scores) and
   outputs `prediction`, `probability`, `label`.

**SHAP** (TreeExplainer over the XGBoost model) produces the top-10 feature
attributions per transaction. **Gemini** turns the transaction + SHAP into a
human-readable explanation on demand.

> RAG and LSTM/RNN are intentionally **not** part of this system — the LLM layer
> is direct Gemini-API explanation, not retrieval-augmented.

---

## 4. Inference flow (per `/predict` row)

```
raw row ──(drop isFraud)──▶ raw_transactions_staging
   │
   ├─ rules ─ preprocess ─ AE ─ ISO ─ merge ─ drop_low ─ align ─ XGB ─ SHAP
   │                                                                 │
   │                                                    developer_explanations
   ▼
processed row ─────────────▶ processed_transactions_staging   (count++)
                                          │
                          count ≥ 30 ?  ──┴── yes ─▶ drift → severity
                                                       │        │
                                              drift_{low|med|high}_severity
                                                       │
                                       flush staging ─▶ history (dedup), empty staging
```

`/predict` **streams** one NDJSON line per transaction (plus drift notices and a
final "done"), so the UI shows live progress and long batches never time out.

See [drift_detection_strategy.md](drift_detection_strategy.md) and
[database_design.md](database_design.md) for the staging→history mechanics.

---

## 5. Request → table map

| Endpoint | Reads / writes |
|----------|----------------|
| `POST /predict` | writes raw+processed staging, `developer_explanations`; triggers drift/flush |
| `GET /transactions`, `/transaction/{id}` | processed history ∪ staging |
| `GET /shap`, `/shap/{id}` | `developer_explanations` |
| `GET /llm/{id}` | reads processed + SHAP, writes `llm_explanations` (Gemini) |
| `GET /drift/{severity}` | `drift_{low,medium,high}_severity` |
| `GET /drift/{severity}/{id}/download` | history rows for the chunk → ZIP |
| `GET /history/{raw,processed}` | full history table → CSV |

---

## 6. Folder structure (backend)

```
fraud_detection/
├── src/
│   ├── api/                FastAPI app (main, routes, pipeline_loader)
│   ├── model_pipeline/     FraudPipeline + rules/preprocess/AE/ISO modules
│   ├── explainability/     SHAP explainer + store
│   ├── drift_monitoring/   PSI/KS drift components + aggregate + severity router
│   └── llm/                Gemini client, prompt builder, explanation service
├── database/               SQLAlchemy access: connection, staging, flush, severity
├── prisma/                 schema.prisma + migrations (stable tables)
├── saved_models/           trained artifacts (XGB, AE .keras, ISO, scalers)
├── baseline/               drift baselines (iso/ae/rules/feature JSON)
├── frontend/               React dashboard
└── docs/                   this documentation
```
