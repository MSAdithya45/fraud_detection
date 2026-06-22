# FraudLens — Database Design

The database is **Supabase (PostgreSQL)**. **Prisma** owns the schema for the
stable hand-defined tables (migrations); the wide, dynamic tables are created at
runtime by the Python app (pandas). The runtime never uses Prisma Client — all
access is SQLAlchemy + pandas via `database/connection.py` (`get_engine()`).

---

## 1. Table inventory

### Dynamic tables (created at runtime by pandas — NOT in Prisma)

| Table | Purpose | Schema source |
|-------|---------|---------------|
| `raw_transactions_staging` | incoming raw rows for the current chunk (no `isFraud`) | first `/predict` CSV |
| `processed_transactions_staging` | scored rows for the current chunk (features + AE/ISO + prediction/probability/label) | first processed record |
| `raw_transactions_history` | all committed raw rows | `LIKE raw_transactions_staging` |
| `processed_transactions_history` | all committed scored rows (dashboard source) | `LIKE processed_transactions_staging` |

### Prisma-managed tables (`prisma/schema.prisma`)

| Table | Key columns |
|-------|-------------|
| `drift_low_severity` | `id`, `transaction_ids` (JSONB), `iso/ae/rules/feature/final_drift_score`, `monitoring_status`, `created_at` |
| `drift_medium_severity` | same schema |
| `drift_high_severity` | same schema |
| `developer_explanations` | `id`, `transaction_id`, `feature`, `impact`, `absolute_impact`, `created_at` |
| `llm_explanations` | `transaction_id` (PK), `explanation`, `created_at` |

The three drift tables share one normalized schema (one row = one analysed chunk).

---

## 2. Staging → history lifecycle

```
/predict row ─▶ raw_staging + processed_staging   (chunk accumulates)
                         │
        processed_staging count ≥ 30
                         │
                 run drift + severity
                         │
        write 1 row to drift_{severity}
                         │
   raw_staging  ─▶ raw_history     (skip TransactionIDs already present)
   processed_staging ─▶ processed_history
                         │
              TRUNCATE both staging tables
```

- The **staging** tables hold at most one chunk (~30 rows).
- The **history** tables are the permanent record and the dashboard's source
  (read as `history ∪ staging` so in-flight rows show immediately).
- Flush copies with a `NOT EXISTS` guard, so history never gains duplicate
  TransactionIDs across chunks.

---

## 3. Uniqueness constraints

Every transaction is identified by `"TransactionID"` (case-sensitive — pandas
preserves the IEEE-CIS column casing, so it is always double-quoted in SQL).

- All four dynamic tables get a **`UNIQUE` index on `"TransactionID"`**
  (`<table>_txid_unique`), applied automatically on table creation by
  `ensure_unique_transaction_id()` in `database/connection.py`.
- Inserting a duplicate within a chunk fails fast → that row is reported as
  `failed` in the `/predict` stream (it is not stored), keeping raw and
  processed staging in lockstep.
- Cross-chunk duplicates are skipped by the flush's `NOT EXISTS` clause.

### One-time clean-up for existing data

If a table already contains duplicates (e.g. from earlier runs), the unique
index can't be created until they're removed. Run once in the Supabase SQL
editor:

```sql
DO $$
DECLARE t text;
BEGIN
  FOREACH t IN ARRAY ARRAY[
    'raw_transactions_staging','processed_transactions_staging',
    'raw_transactions_history','processed_transactions_history'
  ] LOOP
    IF to_regclass(t) IS NOT NULL THEN
      EXECUTE format(
        'DELETE FROM %I a USING %I b WHERE a.ctid < b.ctid AND a.%I = b.%I',
        t, t, 'TransactionID', 'TransactionID');
      EXECUTE format(
        'CREATE UNIQUE INDEX IF NOT EXISTS %I ON %I (%I)',
        t || '_txid_unique', t, 'TransactionID');
    END IF;
  END LOOP;
END $$;
```

---

## 4. Prisma rules

- **Source of record** for the 5 stable tables; migrations live in
  `prisma/migrations/`. Apply with `npx prisma migrate deploy`.
- **Never** run `prisma migrate reset` or `prisma db push` — they drop the
  dynamic (pandas) tables. Deploy-only.
- The Python connection layer strips Prisma-only query params (`pgbouncer`,
  `connection_limit`, …) from `DATABASE_URL` before psycopg2 sees it, and sets
  `client_encoding=utf8` for the Supabase pooler.

### Connection

- `DATABASE_URL` → Supabase **Session Pooler** (port 5432) — used by the app
  *and* as Prisma's `url`. Keeps prepared statements (needed by pandas).
- `DIRECT_URL` → direct connection — used by Prisma migrations only.
