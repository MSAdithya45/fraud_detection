-- ============================================================
-- DEPRECATED as the source of truth.
-- ============================================================
-- The canonical schema for these tables is now managed by Prisma:
--   prisma/schema.prisma  +  prisma/migrations/
-- Apply it with:  npx prisma migrate deploy
--
-- This file is kept only as a human-readable PostgreSQL reference
-- (ported from the original MySQL DDL). Table/column names unchanged.
-- The wide data tables (data, training_data, new_transactions,
-- transaction_analysis, raw_new_transactions, *_transactions_record)
-- are created at runtime by pandas and are intentionally not listed here.
-- ============================================================

CREATE TABLE IF NOT EXISTS drift_analysis_log (
    id SERIAL PRIMARY KEY,
    transaction_ids JSONB,
    final_drift_score DOUBLE PRECISION,
    iso_drift_score DOUBLE PRECISION,
    ae_drift_score DOUBLE PRECISION,
    rules_drift_score DOUBLE PRECISION,
    feature_drift_score DOUBLE PRECISION,
    severity VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS medium_severity_watchlist (
    id SERIAL PRIMARY KEY,
    transaction_ids JSONB,
    final_drift_score DOUBLE PRECISION,
    iso_drift_score DOUBLE PRECISION,
    ae_drift_score DOUBLE PRECISION,
    rules_drift_score DOUBLE PRECISION,
    feature_drift_score DOUBLE PRECISION,
    monitoring_status VARCHAR(20) DEFAULT 'ACTIVE',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS feedback_queue (
    id SERIAL PRIMARY KEY,
    transaction_ids JSONB,
    final_drift_score DOUBLE PRECISION,
    iso_drift_score DOUBLE PRECISION,
    ae_drift_score DOUBLE PRECISION,
    rules_drift_score DOUBLE PRECISION,
    feature_drift_score DOUBLE PRECISION,
    monitoring_status VARCHAR(20) DEFAULT 'ACTIVE',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS developer_explanations (
    id SERIAL PRIMARY KEY,
    transaction_id BIGINT,
    feature VARCHAR(255),
    impact DOUBLE PRECISION,
    absolute_impact DOUBLE PRECISION,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS llm_explanations (
    transaction_id BIGINT PRIMARY KEY,
    explanation TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
