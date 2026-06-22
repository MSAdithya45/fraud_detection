-- Initial migration: stable hand-defined tables (ported MySQL -> PostgreSQL).
-- Table/column names are unchanged from the original database/schema.sql.

-- CreateTable
CREATE TABLE "drift_analysis_log" (
    "id" SERIAL NOT NULL,
    "transaction_ids" JSONB,
    "final_drift_score" DOUBLE PRECISION,
    "iso_drift_score" DOUBLE PRECISION,
    "ae_drift_score" DOUBLE PRECISION,
    "rules_drift_score" DOUBLE PRECISION,
    "feature_drift_score" DOUBLE PRECISION,
    "severity" VARCHAR(20),
    "created_at" TIMESTAMP(6) DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "drift_analysis_log_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "medium_severity_watchlist" (
    "id" SERIAL NOT NULL,
    "transaction_ids" JSONB,
    "final_drift_score" DOUBLE PRECISION,
    "iso_drift_score" DOUBLE PRECISION,
    "ae_drift_score" DOUBLE PRECISION,
    "rules_drift_score" DOUBLE PRECISION,
    "feature_drift_score" DOUBLE PRECISION,
    "monitoring_status" VARCHAR(20) DEFAULT 'ACTIVE',
    "created_at" TIMESTAMP(6) DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "medium_severity_watchlist_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "feedback_queue" (
    "id" SERIAL NOT NULL,
    "transaction_ids" JSONB,
    "final_drift_score" DOUBLE PRECISION,
    "iso_drift_score" DOUBLE PRECISION,
    "ae_drift_score" DOUBLE PRECISION,
    "rules_drift_score" DOUBLE PRECISION,
    "feature_drift_score" DOUBLE PRECISION,
    "monitoring_status" VARCHAR(20) DEFAULT 'ACTIVE',
    "created_at" TIMESTAMP(6) DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "feedback_queue_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "developer_explanations" (
    "id" SERIAL NOT NULL,
    "transaction_id" BIGINT,
    "feature" VARCHAR(255),
    "impact" DOUBLE PRECISION,
    "absolute_impact" DOUBLE PRECISION,
    "created_at" TIMESTAMP(6) DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "developer_explanations_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "llm_explanations" (
    "transaction_id" BIGINT NOT NULL,
    "explanation" TEXT,
    "created_at" TIMESTAMP(6) DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "llm_explanations_pkey" PRIMARY KEY ("transaction_id")
);
