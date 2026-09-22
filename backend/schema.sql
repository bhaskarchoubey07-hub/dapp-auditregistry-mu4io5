-- PostgreSQL Schema: Automated Financial Audit & Compliance System
-- Target Host: Neon Serverless / Supabase PostgreSQL

-- 1. Users and Auditor Roles
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username VARCHAR(64) UNIQUE NOT NULL,
    wallet_address VARCHAR(42) UNIQUE,
    role VARCHAR(32) DEFAULT 'AUDITOR' CHECK (role IN ('ADMIN', 'AUDITOR', 'COMPLIANCE_OFFICER', 'VIEWER')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 2. Audit Batches
CREATE TABLE IF NOT EXISTS audit_batches (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id VARCHAR(128) NOT NULL,
    title VARCHAR(255) NOT NULL,
    total_records INTEGER DEFAULT 0,
    total_volume NUMERIC(18, 2) DEFAULT 0.00,
    anomaly_count INTEGER DEFAULT 0,
    reconciliation_status VARCHAR(32) DEFAULT 'PENDING' CHECK (reconciliation_status IN ('PENDING', 'RECONCILED', 'DISCREPANCY_DETECTED')),
    compliance_status VARCHAR(32) DEFAULT 'UNDER_REVIEW' CHECK (compliance_status IN ('UNDER_REVIEW', 'APPROVED', 'FLAGGED', 'REJECTED')),
    deterministic_hash VARCHAR(66) UNIQUE,
    blockchain_tx_hash VARCHAR(66),
    anchored_at TIMESTAMP WITH TIME ZONE,
    anchored_by VARCHAR(42),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 3. Financial Transactions Ledger
CREATE TABLE IF NOT EXISTS transactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    batch_id UUID REFERENCES audit_batches(id) ON DELETE CASCADE,
    transaction_ref VARCHAR(64) NOT NULL,
    account_number VARCHAR(64) NOT NULL,
    amount NUMERIC(18, 2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'USD',
    type VARCHAR(10) NOT NULL CHECK (type IN ('DEBIT', 'CREDIT')),
    category VARCHAR(64) DEFAULT 'General',
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    is_anomaly BOOLEAN DEFAULT FALSE,
    anomaly_score REAL,
    anomaly_reason TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for high performance querying
CREATE INDEX IF NOT EXISTS idx_audit_batches_project ON audit_batches(project_id);
CREATE INDEX IF NOT EXISTS idx_audit_batches_hash ON audit_batches(deterministic_hash);
CREATE INDEX IF NOT EXISTS idx_transactions_batch_id ON transactions(batch_id);
CREATE INDEX IF NOT EXISTS idx_transactions_ref ON transactions(transaction_ref);
CREATE INDEX IF NOT EXISTS idx_transactions_account ON transactions(account_number);
