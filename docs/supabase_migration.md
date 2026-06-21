# Supabase + Prisma Migration Guide

This project was migrated from a **local MySQL** database (SQLAlchemy +
`mysql.connector`) to **Supabase (PostgreSQL)**.

- **Runtime data access** stays in Python: SQLAlchemy + pandas, re-pointed at
  Supabase via a single central engine (`database/connection.py`).
- **Prisma** is introduced as the **schema-of-record and migration tool only**
  (it manages the stable hand-defined tables). The Python app does **not** use
  Prisma Client.

Table names, column names, relations, and business logic are unchanged.

---

## What Prisma manages (and what it must not touch)

Prisma owns only the 5 stable tables (`prisma/schema.prisma`):
`drift_analysis_log`, `medium_severity_watchlist`, `feedback_queue`,
`developer_explanations`, `llm_explanations`.

The wide tables created at runtime by pandas `to_sql` are **deliberately not**
in the Prisma schema: `data`, `training_data`, `new_transactions`,
`transaction_analysis`, `raw_new_transactions`, `low_transactions_record`,
`medium_transactions_record`, `high_transactions_record`.

> ⚠️ **Never run `prisma migrate reset` or `prisma db push`.** Both will drop
> tables Prisma does not know about — i.e. your data tables. Use
> **`prisma migrate deploy`** only. To author *new* migrations later, point
> `prisma migrate dev` at a separate local/shadow Postgres, then `deploy` the
> generated migration to Supabase.

---

## Environment variables

Set these in `.env` (see `.env.example`):

| Variable | Used by | Supabase source |
|----------|---------|-----------------|
| `DATABASE_URL` | Python app (SQLAlchemy) **and** Prisma `url` | **Session Pooler**, port 5432 (`...pooler.supabase.com`) |
| `DIRECT_URL` | Prisma migrations only | **Direct connection**, port 5432 (`db.<ref>.supabase.co`) |
| `GEMINI_API_KEY` | LLM explanations | — |

Use the **Session Pooler** for `DATABASE_URL` (IPv4 + keeps prepared
statements, which pandas `to_sql`/`read_sql` need). Avoid the Transaction
Pooler (port 6543) for the Python app — it breaks prepared statements.

---

## One-time Supabase setup

1. Create a Supabase project (Dashboard → New project). Save the DB password.
2. Dashboard → **Connect**: copy the **Session pooler** URI into `DATABASE_URL`
   and the **Direct connection** URI into `DIRECT_URL` (append
   `?sslmode=require` to both). Fill the password in.
3. Apply the schema with Prisma (creates the 5 stable tables):
   ```bash
   npm install
   npx prisma migrate deploy
   ```
4. Install Python deps (psycopg2 replaces the MySQL driver):
   ```bash
   pip install -r requirements.txt
   ```
5. Load the datasets into Supabase (recreates the wide tables on Postgres):
   ```bash
   python database/raw_data.py          # creates `data`
   python database/upload_dataset.py    # creates `training_data`
   ```
6. Run the app:
   ```bash
   uvicorn src.api.main:app --reload
   # dashboard:
   streamlit run dashboards/shap_dashboard.py
   ```

---

## Prisma commands (only the ones this project needs)

```bash
npx prisma migrate deploy   # apply migrations to Supabase (normal path)
npx prisma migrate status   # check which migrations are applied
npx prisma studio           # browse the 5 managed tables (optional)
```

`prisma generate` is not required (no Prisma Client at runtime).

---

## MySQL → PostgreSQL changes made

| Area | Change | Why |
|------|--------|-----|
| `database/connection.py` (new) | Single `get_engine()` factory reading `DATABASE_URL`, with pooling | One place for Supabase connection settings |
| All `database/*.py`, `shap_monitor.py`, `shap_dashboard.py` | `mysql+mysqlconnector://root:...` → `get_engine()` | Use Supabase Postgres |
| `database/db.py` | `mysql.connector` → `psycopg2` | Postgres driver |
| Raw SQL referencing `TransactionID` | Quoted as `"TransactionID"` | Postgres folds unquoted identifiers to lowercase; pandas `to_sql` preserves the mixed case, so the column is case-sensitive |
| `database/schema.sql` types (`AUTO_INCREMENT`, `LONGTEXT`, `JSON`) | Ported to Postgres (`SERIAL`, `TEXT`, `JSONB`) in `prisma/migrations` | Postgres syntax |
| `transaction_ids` (`JSON` → `JSONB`) | Modelled as Prisma `Json` | `json.dumps(...)` strings are coerced into `jsonb` by psycopg2; behavior preserved |

---

## Verification checklist

- [ ] `npx prisma migrate status` shows the `init` migration applied.
- [ ] The 5 tables exist in Supabase (Table Editor / `prisma studio`).
- [ ] `python database/raw_data.py` loads `data` without error.
- [ ] `POST /predict` with a CSV inserts into `raw_new_transactions` and
      `transaction_analysis`, and SHAP rows into `developer_explanations`.
- [ ] `GET /transactions` and `GET /transaction/{id}` return rows.
- [ ] `GET /shap/{id}` returns feature impacts.
- [ ] `GET /llm/{id}` generates an explanation and writes `llm_explanations`.
- [ ] After ~500 predictions, drift logging writes to `drift_analysis_log` /
      `medium_severity_watchlist` / `feedback_queue` per severity.
- [ ] Streamlit dashboard loads SHAP data from Supabase.
