# FraudLens

**AI-powered financial fraud detection & AML platform** — an ensemble scoring
engine with explainable AI, continuous drift monitoring, and an analyst
dashboard.

FraudLens scores transactions with a rules + autoencoder + isolation-forest +
XGBoost ensemble, explains every decision with SHAP and an LLM, watches for data
drift, and routes risky batches into a feedback loop for investigation and
retraining.

---

## Features

- **Ensemble scoring** — rules engine → autoencoder → isolation forest → XGBoost.
- **Explainability** — per-transaction SHAP attributions + on-demand Gemini
  natural-language explanations.
- **Streaming predictions** — upload a CSV and watch each transaction score live
  (NDJSON stream; no request timeouts).
- **Drift monitoring** — PSI + KS per 30-transaction chunk, weighted into a final
  score and routed to Low / Medium / High severity tiers.
- **Feedback loop** — download the raw + processed data behind any flagged chunk
  for relabeling and retraining.
- **Analyst dashboard** — KPIs, risk breakdown, SHAP importance, transactions,
  drift analysis, and history exports.

---

## Tech stack

| Area | Stack |
|------|-------|
| Backend | FastAPI, SQLAlchemy + pandas, Python 3.11 |
| ML | XGBoost, TensorFlow/Keras (autoencoder), scikit-learn (isolation forest), SHAP |
| LLM | Google Gemini API |
| Database | Supabase (PostgreSQL); Prisma for schema/migrations |
| Frontend | React 18 (JS), Vite, Tailwind CSS, Framer Motion, Recharts, React Query |
| Deployment | Docker (multi-stage backend + nginx frontend), docker-compose |

> Scope: the ensemble is rules + AE + ISO + XGB. RAG and LSTM/RNN are
> intentionally out of scope; the LLM layer is direct Gemini explanations.

---

## Quick start

### 1. Database (Supabase + Prisma)
```bash
cd fraud_detection
npm install
npx prisma migrate deploy
```
Add `DATABASE_URL`, `DIRECT_URL`, `GEMINI_API_KEY` to `.env` (see `.env.example`).

### 2. Backend
```bash
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn src.api.main:app --host 127.0.0.1 --port 8000     # no --reload for batches
```
Swagger: http://localhost:8000/docs

### 3. Frontend
```bash
cd frontend
npm install
npm run dev        # http://localhost:5173
```

### Or run everything with Docker
```bash
cd fraud_detection
docker compose up --build
# frontend → http://localhost:8080   backend → http://localhost:8000
```

---

## API

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/predict` | Score a CSV; streams per-transaction NDJSON + drift notices |
| GET | `/transactions`, `/transaction/{id}` | Scored transactions (history ∪ staging) |
| GET | `/shap`, `/shap/{id}` | SHAP feature attributions |
| GET | `/llm/{id}` | Gemini explanation for a transaction |
| GET | `/drift/{severity}` | Drift records (low / medium / high) |
| GET | `/drift/{severity}/{id}/download` | ZIP of the chunk's raw + processed rows |
| GET | `/history/raw`, `/history/processed` | Full history as CSV |

---

## Project structure

```
fraud_detection/
├── src/
│   ├── api/                FastAPI app (main, routes, pipeline_loader)
│   ├── model_pipeline/     FraudPipeline + rules / preprocess / AE / ISO
│   ├── explainability/     SHAP explainer + store
│   ├── drift_monitoring/   PSI/KS components, aggregate, severity router
│   └── llm/                Gemini client, prompt builder, explanation service
├── database/               SQLAlchemy access (connection, staging, flush, severity)
├── prisma/                 schema.prisma + migrations
├── saved_models/           trained artifacts
├── baseline/               drift baselines
├── frontend/               React dashboard (FraudLens)
├── docs/                   documentation
├── Dockerfile              backend image (multi-stage)
└── docker-compose.yml      backend + frontend
```

---

## Documentation

| Doc | Contents |
|-----|----------|
| [docs/architecture.md](docs/architecture.md) | System architecture, components, data flow |
| [docs/database_design.md](docs/database_design.md) | Tables, staging→history, constraints, Prisma |
| [docs/drift_detection_strategy.md](docs/drift_detection_strategy.md) | PSI/KS, weights, severity routing |
| [docs/feeback_loop_strategy.md](docs/feeback_loop_strategy.md) | Severity triage, retraining loop |
| [docs/deployment_guide.md](docs/deployment_guide.md) | Local + Docker deployment |
| [docs/docker.md](docs/docker.md) | Docker build / push / run reference |
| [docs/supabase_migration.md](docs/supabase_migration.md) | MySQL → Supabase migration notes |

---

## Operational notes

- Run the backend **without `--reload`** when processing batches (reload drops
  the streaming connection).
- Each transaction is unique by `TransactionID`; staging and history enforce a
  `UNIQUE` index and the flush de-duplicates across chunks.
- Drift runs every **30** transactions (`DRIFT_BATCH_SIZE` in `pipeline.py`).
- Never run `prisma migrate reset` / `db push` — they drop the pandas tables.
