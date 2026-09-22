# Database Architecture Report

**Project:** Automated Financial Audit & Compliance System (Audit Registry DApp)  
**Database Engine:** PostgreSQL 15+ (Hosted on Neon Serverless / Supabase)  
**Schema File:** `backend/schema.sql`  

---

## 1. Schema Normalization & Design

The relational schema implements 3NF normalization across 3 primary entities:

### 1.1 `users` Table
Stores authenticated system actors and role-based permissions:
- `id` (UUID, Primary Key)
- `username` (VARCHAR(64), Unique)
- `wallet_address` (VARCHAR(42), Unique Ethereum Address)
- `role` (VARCHAR(32), Constraints: `ADMIN`, `AUDITOR`, `COMPLIANCE_OFFICER`, `VIEWER`)
- `created_at` (TIMESTAMP WITH TIME ZONE)

### 1.2 `audit_batches` Table
Represents a finalized audit run covering an ingested transaction ledger:
- `id` (UUID, Primary Key)
- `project_id` (VARCHAR(128))
- `title` (VARCHAR(255))
- `total_records` (INTEGER)
- `total_volume` (NUMERIC(18, 2))
- `anomaly_count` (INTEGER)
- `reconciliation_status` (VARCHAR(32), Constraints: `PENDING`, `RECONCILED`, `DISCREPANCY_DETECTED`)
- `compliance_status` (VARCHAR(32), Constraints: `UNDER_REVIEW`, `APPROVED`, `FLAGGED`, `REJECTED`)
- `deterministic_hash` (VARCHAR(66), Unique 32-byte hex string)
- `blockchain_tx_hash` (VARCHAR(66), Etherscan reference)
- `anchored_at` (TIMESTAMP WITH TIME ZONE)
- `anchored_by` (VARCHAR(42), Wallet address)

### 1.3 `transactions` Table
Stores granular double-entry transaction records linked to an audit batch:
- `id` (UUID, Primary Key)
- `batch_id` (UUID, Foreign Key referencing `audit_batches(id)` ON DELETE CASCADE)
- `transaction_ref` (VARCHAR(64), Indexed)
- `account_number` (VARCHAR(64), Indexed)
- `amount` (NUMERIC(18, 2))
- `currency` (VARCHAR(3), Default: 'USD')
- `type` (VARCHAR(10), Constraints: `DEBIT`, `CREDIT`)
- `category` (VARCHAR(64))
- `timestamp` (TIMESTAMP WITH TIME ZONE)
- `is_anomaly` (BOOLEAN)
- `anomaly_score` (REAL)
- `anomaly_reason` (TEXT)

---

## 2. Connection Pooling & SSL Settings
When deploying to Neon:
- Connect using `?sslmode=require`.
- Utilize the Neon pooled connection string on port `6543` to support high concurrency and mitigate connection limits.
