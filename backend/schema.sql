-- ==============================================================================
-- AuditRegistry: Enterprise Financial Audit & Compliance Database Schema
-- Target: Supabase PostgreSQL / Neon PostgreSQL 15+
-- Features: 3NF Normalization, UUID Keys, Foreign Keys, Check Constraints,
--           High-Performance Indexes, Row-Level Security (RLS), Backward Compatibility
-- ==============================================================================

-- Enable UUID extension if not already enabled
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ------------------------------------------------------------------------------
-- 1. USERS & ROLES
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username VARCHAR(64) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE,
    wallet_address VARCHAR(42) UNIQUE,
    role VARCHAR(32) DEFAULT 'AUDITOR' CHECK (role IN ('ADMIN', 'AUDITOR', 'COMPLIANCE_OFFICER', 'VIEWER')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- ------------------------------------------------------------------------------
-- 2. AUDIT SESSIONS
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS audit_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id VARCHAR(128) NOT NULL,
    session_name VARCHAR(255) NOT NULL,
    status VARCHAR(32) DEFAULT 'IN_PROGRESS' CHECK (status IN ('INITIALIZED', 'IN_PROGRESS', 'COMPLETED', 'ANCHORED', 'REJECTED')),
    total_records INTEGER DEFAULT 0 CHECK (total_records >= 0),
    total_volume NUMERIC(18, 2) DEFAULT 0.00 CHECK (total_volume >= 0),
    created_by UUID REFERENCES users(id) ON DELETE SET NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Backward compatibility view for legacy audit_batches queries
CREATE OR REPLACE VIEW audit_batches AS
SELECT 
    id,
    project_id,
    session_name AS title,
    total_records,
    total_volume,
    status,
    created_at,
    updated_at
FROM audit_sessions;

-- ------------------------------------------------------------------------------
-- 3. TRANSACTIONS LEDGER
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS transactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID NOT NULL REFERENCES audit_sessions(id) ON DELETE CASCADE,
    transaction_ref VARCHAR(64) NOT NULL,
    account_number VARCHAR(64) NOT NULL,
    amount NUMERIC(18, 2) NOT NULL CHECK (amount > 0),
    currency VARCHAR(3) DEFAULT 'USD',
    type VARCHAR(10) NOT NULL CHECK (type IN ('DEBIT', 'CREDIT')),
    category VARCHAR(64) DEFAULT 'General',
    description TEXT DEFAULT '',
    entry_date DATE NOT NULL DEFAULT CURRENT_DATE,
    raw_payload JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_session_tx_ref UNIQUE (session_id, transaction_ref)
);

-- ------------------------------------------------------------------------------
-- 4. DOUBLE-ENTRY RECONCILIATIONS
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS reconciliations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID UNIQUE NOT NULL REFERENCES audit_sessions(id) ON DELETE CASCADE,
    total_debit NUMERIC(18, 2) NOT NULL DEFAULT 0.00,
    total_credit NUMERIC(18, 2) NOT NULL DEFAULT 0.00,
    difference NUMERIC(18, 2) NOT NULL DEFAULT 0.00,
    is_reconciled BOOLEAN NOT NULL DEFAULT FALSE,
    status VARCHAR(32) DEFAULT 'UNBALANCED' CHECK (status IN ('BALANCED', 'UNBALANCED', 'DISCREPANCY_FLAGGED')),
    reconciled_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- ------------------------------------------------------------------------------
-- 5. AI ANOMALIES (Isolation Forest & Rule Inference)
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS anomalies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID NOT NULL REFERENCES audit_sessions(id) ON DELETE CASCADE,
    transaction_id UUID NOT NULL REFERENCES transactions(id) ON DELETE CASCADE,
    anomaly_score REAL NOT NULL CHECK (anomaly_score >= 0.0 AND anomaly_score <= 1.0),
    risk_level VARCHAR(16) NOT NULL CHECK (risk_level IN ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL')),
    explanation TEXT NOT NULL,
    is_anomaly BOOLEAN DEFAULT TRUE,
    review_status VARCHAR(16) DEFAULT 'OPEN' CHECK (review_status IN ('OPEN', 'REVIEWED', 'CLEARED', 'CONFIRMED')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- ------------------------------------------------------------------------------
-- 6. COMPLIANCE FINDINGS
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS compliance_findings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID NOT NULL REFERENCES audit_sessions(id) ON DELETE CASCADE,
    finding_code VARCHAR(32) NOT NULL, -- e.g. AML-10K, STRUCTURING-9K, DUPLICATE-REF
    severity VARCHAR(16) NOT NULL CHECK (severity IN ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL')),
    title VARCHAR(255) NOT NULL,
    details TEXT,
    affected_count INTEGER DEFAULT 1,
    status VARCHAR(32) DEFAULT 'ACTIVE' CHECK (status IN ('ACTIVE', 'RESOLVED', 'DISMISSED')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- ------------------------------------------------------------------------------
-- 7. BENFORD LAW FORENSIC RESULTS
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS benford_results (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID UNIQUE NOT NULL REFERENCES audit_sessions(id) ON DELETE CASCADE,
    sample_size INTEGER NOT NULL CHECK (sample_size >= 0),
    observed_distribution JSONB NOT NULL, -- e.g. {"1": 31.2, "2": 17.1, ...}
    expected_distribution JSONB NOT NULL, -- standard Benford log10 curve
    divergence_score REAL DEFAULT 0.0,
    anomaly_detected BOOLEAN DEFAULT FALSE,
    evaluated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- ------------------------------------------------------------------------------
-- 8. AUDIT RECORDS (Canonical Cryptographic Dataset Records)
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS audit_records (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID NOT NULL REFERENCES audit_sessions(id) ON DELETE CASCADE,
    project_id VARCHAR(128) NOT NULL,
    canonical_hash VARCHAR(66) NOT NULL, -- 0x + 64 hex chars
    record_count INTEGER NOT NULL,
    total_debit NUMERIC(18, 2) NOT NULL,
    total_credit NUMERIC(18, 2) NOT NULL,
    generated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_session_hash UNIQUE (session_id, canonical_hash)
);

-- ------------------------------------------------------------------------------
-- 9. BLOCKCHAIN RECORDS (On-Chain Attestation Receipts)
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS blockchain_records (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID NOT NULL REFERENCES audit_sessions(id) ON DELETE CASCADE,
    audit_record_id UUID REFERENCES audit_records(id) ON DELETE SET NULL,
    data_hash VARCHAR(66) NOT NULL,
    transaction_hash VARCHAR(66),
    block_number BIGINT,
    chain_id VARCHAR(32) NOT NULL,
    contract_address VARCHAR(42) NOT NULL,
    wallet_address VARCHAR(42) NOT NULL,
    status VARCHAR(32) DEFAULT 'PENDING' CHECK (status IN ('PENDING', 'MINED', 'CONFIRMED', 'FAILED')),
    verified_on_chain BOOLEAN DEFAULT FALSE,
    anchored_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- ------------------------------------------------------------------------------
-- 10. AUDIT CERTIFICATES
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS audit_certificates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID UNIQUE NOT NULL REFERENCES audit_sessions(id) ON DELETE CASCADE,
    certificate_number VARCHAR(64) UNIQUE NOT NULL,
    issuer_wallet VARCHAR(42) NOT NULL,
    canonical_hash VARCHAR(66) NOT NULL,
    transaction_hash VARCHAR(66),
    certificate_data JSONB NOT NULL,
    issued_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- ------------------------------------------------------------------------------
-- 11. SYSTEM SETTINGS
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS system_settings (
    key VARCHAR(64) PRIMARY KEY,
    value JSONB NOT NULL,
    description TEXT,
    is_public BOOLEAN DEFAULT FALSE,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Populate default non-sensitive system settings
INSERT INTO system_settings (key, value, description, is_public)
VALUES
    ('aml_threshold', '10000'::jsonb, 'Regulatory threshold for high-value AML screening', TRUE),
    ('structuring_threshold', '9000'::jsonb, 'Threshold for detecting potential structuring', TRUE),
    ('default_currency', '"USD"'::jsonb, 'Default operating ledger currency', TRUE),
    ('contract_address', '"0xd8b934580fcE35a11B58C6D73aDeE468a2833fa8"'::jsonb, 'AuditRegistry smart contract address', TRUE),
    ('expected_chain_id', '"11155111"'::jsonb, 'Target EVM chain ID (Sepolia)', TRUE)
ON CONFLICT (key) DO NOTHING;

-- ------------------------------------------------------------------------------
-- INDEXES FOR HIGH-PERFORMANCE QUERYING
-- ------------------------------------------------------------------------------
CREATE INDEX IF NOT EXISTS idx_audit_sessions_project ON audit_sessions(project_id);
CREATE INDEX IF NOT EXISTS idx_transactions_session ON transactions(session_id);
CREATE INDEX IF NOT EXISTS idx_transactions_ref ON transactions(transaction_ref);
CREATE INDEX IF NOT EXISTS idx_transactions_account ON transactions(account_number);
CREATE INDEX IF NOT EXISTS idx_anomalies_session ON anomalies(session_id);
CREATE INDEX IF NOT EXISTS idx_anomalies_tx ON anomalies(transaction_id);
CREATE INDEX IF NOT EXISTS idx_compliance_session ON compliance_findings(session_id);
CREATE INDEX IF NOT EXISTS idx_audit_records_hash ON audit_records(canonical_hash);
CREATE INDEX IF NOT EXISTS idx_blockchain_records_hash ON blockchain_records(data_hash);
CREATE INDEX IF NOT EXISTS idx_blockchain_records_tx ON blockchain_records(transaction_hash);
CREATE INDEX IF NOT EXISTS idx_certificates_number ON audit_certificates(certificate_number);

-- ------------------------------------------------------------------------------
-- ROW LEVEL SECURITY (RLS) POLICIES
-- ------------------------------------------------------------------------------
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE audit_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE transactions ENABLE ROW LEVEL SECURITY;
ALTER TABLE reconciliations ENABLE ROW LEVEL SECURITY;
ALTER TABLE anomalies ENABLE ROW LEVEL SECURITY;
ALTER TABLE compliance_findings ENABLE ROW LEVEL SECURITY;
ALTER TABLE benford_results ENABLE ROW LEVEL SECURITY;
ALTER TABLE audit_records ENABLE ROW LEVEL SECURITY;
ALTER TABLE blockchain_records ENABLE ROW LEVEL SECURITY;
ALTER TABLE audit_certificates ENABLE ROW LEVEL SECURITY;
ALTER TABLE system_settings ENABLE ROW LEVEL SECURITY;

-- Public Read Policies (for browser client anon key)
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE policyname = 'Public Read System Settings') THEN
        CREATE POLICY "Public Read System Settings" ON system_settings FOR SELECT USING (is_public = TRUE);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE policyname = 'Public Read Audit Sessions') THEN
        CREATE POLICY "Public Read Audit Sessions" ON audit_sessions FOR SELECT USING (TRUE);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE policyname = 'Public Read Transactions') THEN
        CREATE POLICY "Public Read Transactions" ON transactions FOR SELECT USING (TRUE);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE policyname = 'Public Read Reconciliations') THEN
        CREATE POLICY "Public Read Reconciliations" ON reconciliations FOR SELECT USING (TRUE);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE policyname = 'Public Read Anomalies') THEN
        CREATE POLICY "Public Read Anomalies" ON anomalies FOR SELECT USING (TRUE);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE policyname = 'Public Read Benford') THEN
        CREATE POLICY "Public Read Benford" ON benford_results FOR SELECT USING (TRUE);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE policyname = 'Public Read Blockchain Records') THEN
        CREATE POLICY "Public Read Blockchain Records" ON blockchain_records FOR SELECT USING (TRUE);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE policyname = 'Public Read Certificates') THEN
        CREATE POLICY "Public Read Certificates" ON audit_certificates FOR SELECT USING (TRUE);
    END IF;
END $$;

-- Service Role Full Access Policies (Backend has full access via SERVICE_ROLE_KEY or direct DB)
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE policyname = 'Service Role Full Access Sessions') THEN
        CREATE POLICY "Service Role Full Access Sessions" ON audit_sessions FOR ALL USING (TRUE) WITH CHECK (TRUE);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE policyname = 'Service Role Full Access Transactions') THEN
        CREATE POLICY "Service Role Full Access Transactions" ON transactions FOR ALL USING (TRUE) WITH CHECK (TRUE);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE policyname = 'Service Role Full Access Reconciliations') THEN
        CREATE POLICY "Service Role Full Access Reconciliations" ON reconciliations FOR ALL USING (TRUE) WITH CHECK (TRUE);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE policyname = 'Service Role Full Access Anomalies') THEN
        CREATE POLICY "Service Role Full Access Anomalies" ON anomalies FOR ALL USING (TRUE) WITH CHECK (TRUE);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE policyname = 'Service Role Full Access Blockchain') THEN
        CREATE POLICY "Service Role Full Access Blockchain" ON blockchain_records FOR ALL USING (TRUE) WITH CHECK (TRUE);
    END IF;
END $$;
