-- ============================================================
-- Drift refactor:
--   * rename + normalize the three drift/severity tables
--   * drop the legacy dynamic (pandas) tables
--   * wipe repurposed content
-- The raw/processed staging + history tables are created at runtime
-- by the Python app (pandas), so they are not created here.
-- ============================================================

-- ---- Rename the three drift tables (IF EXISTS = safe to re-run) ----
ALTER TABLE IF EXISTS "drift_analysis_log"       RENAME TO "drift_low_severity";
ALTER TABLE IF EXISTS "medium_severity_watchlist" RENAME TO "drift_medium_severity";
ALTER TABLE IF EXISTS "feedback_queue"            RENAME TO "drift_high_severity";

-- ---- Normalize columns so all three share one schema ----
-- LOW previously had `severity`; all three need `monitoring_status`.
ALTER TABLE IF EXISTS "drift_low_severity"    DROP COLUMN IF EXISTS "severity";
ALTER TABLE IF EXISTS "drift_low_severity"    ADD COLUMN IF NOT EXISTS "monitoring_status" VARCHAR(20) DEFAULT 'ACTIVE';
ALTER TABLE IF EXISTS "drift_medium_severity" ADD COLUMN IF NOT EXISTS "monitoring_status" VARCHAR(20) DEFAULT 'ACTIVE';
ALTER TABLE IF EXISTS "drift_high_severity"   ADD COLUMN IF NOT EXISTS "monitoring_status" VARCHAR(20) DEFAULT 'ACTIVE';
-- final_drift_score already exists on all three; ADD IF NOT EXISTS is a safety no-op.
ALTER TABLE IF EXISTS "drift_low_severity"    ADD COLUMN IF NOT EXISTS "final_drift_score" DOUBLE PRECISION;
ALTER TABLE IF EXISTS "drift_medium_severity" ADD COLUMN IF NOT EXISTS "final_drift_score" DOUBLE PRECISION;
ALTER TABLE IF EXISTS "drift_high_severity"   ADD COLUMN IF NOT EXISTS "final_drift_score" DOUBLE PRECISION;

-- ---- Wipe repurposed / stale content (keep the tables) ----
TRUNCATE TABLE "drift_low_severity", "drift_medium_severity", "drift_high_severity";
TRUNCATE TABLE "developer_explanations";
TRUNCATE TABLE "llm_explanations";

-- ---- Drop legacy dynamic tables (pandas-created, not Prisma-managed) ----
DROP TABLE IF EXISTS "data" CASCADE;
DROP TABLE IF EXISTS "new_transactions" CASCADE;
DROP TABLE IF EXISTS "raw_new_transactions" CASCADE;
DROP TABLE IF EXISTS "transaction_analysis" CASCADE;
DROP TABLE IF EXISTS "low_transactions_record" CASCADE;
DROP TABLE IF EXISTS "medium_transactions_record" CASCADE;
DROP TABLE IF EXISTS "high_transactions_record" CASCADE;
