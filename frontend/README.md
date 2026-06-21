# FraudLens — Fraud Detection Dashboard

Professional React dashboard for the Fraud Detection / AML platform. Clean,
solid (non-glass) UI, monochromatic blue/white palette, light theme only.
Every figure is derived from **real backend data** — no mock/demo data.

## Stack
React 18 (JS) · Vite · Tailwind CSS · Framer Motion · Recharts · React Query · Axios · Lucide

## Run

```bash
cd frontend
npm install
cp .env.example .env        # set VITE_API_BASE_URL if backend isn't on :8000
npm run dev                 # http://localhost:5173
```

The backend must be running for live data:
```bash
# from fraud_detection/
uvicorn src.api.main:app --reload
```
CORS for `localhost:5173` is already enabled in `src/api/main.py`.

> There is no mock data. With the backend down or no transactions scored yet, the
> dashboard shows professional empty / error states. KPIs, the risk-score histogram,
> the risk breakdown, and SHAP feature-importance are all computed from the live
> `/transactions` and `/shap` responses.

## Structure
```
src/
 ├── components/
 │   ├── layout/      Sidebar, Topbar, AppLayout, nav config
 │   ├── dashboard/   KPI cards, AI insights, activity, quick actions, health
 │   ├── charts/      Fraud trend, risk donut, model performance (Recharts)
 │   ├── tables/      Sortable / searchable / paginated transactions table
 │   ├── actions/     API "Action Center" cards + CSV drag-drop upload
 │   └── ui/          GlassCard, Button, Badge, Input, Skeleton, AnimatedCounter
 ├── pages/           Dashboard, Transactions, Predictions, SHAP, LLM, Health, …
 ├── hooks/           React Query data hooks (derive KPIs/stats from real data)
 ├── services/        Axios client + typed API wrappers
 └── utils/           cn(), formatters
```

## Backend endpoints used
`GET /transactions` · `GET /transaction/{id}` · `GET /shap` · `GET /shap/{id}` ·
`GET /llm/{id}` · `POST /predict`

KPIs, risk distribution, the risk-score histogram, and SHAP feature-importance are
all computed in the browser from these responses. Metrics with no backend source
(time-series trend, model accuracy/precision/recall) were removed rather than faked.

## Build
```bash
npm run build      # outputs to dist/
npm run preview
```
