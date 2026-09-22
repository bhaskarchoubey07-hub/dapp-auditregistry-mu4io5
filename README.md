# AuditRegistry — Enterprise Financial Audit & Compliance DApp

AuditRegistry is an Enterprise Financial Audit & Compliance platform combining **Real-World CSV Ingestion**, **Double-Entry Balance Verification**, **Explainable AI Anomaly Detection (Isolation Forest)**, **Benford's Law Forensic Analysis**, **EVM Blockchain Hash Anchoring**, and **Cryptographic Audit Certificate Generation**.

---

## 🏛️ System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                 React + Vite Frontend (UI)                  │
│  8 Modules: Executive Dashboard, CSV Ingestion, AI Anomaly, │
│  Benford Forensic, Blockchain Trail, Double-Entry Balance,  │
│  Export Certificate, System Settings                         │
└──────────────┬───────────────────────────────┬──────────────┘
               │ (REST API)                    │ (EIP-1193 / MetaMask)
               ▼                               ▼
┌──────────────────────────────┐  ┌───────────────────────────┐
│     FastAPI Backend & AI     │  │   Ethereum Smart Contract │
│    Microservice (Port 8000)  │  │         (Sepolia)         │
│  - Isolation Forest Anomaly  │  │  - AuditRegistry.sol      │
│  - Deterministic Hasher      │  │  - registerAuditRecord    │
│  - Accounting Reconciler     │  │  - verifyAuditRecord      │
└──────────────┬───────────────┘  └───────────────────────────┘
               │
               ▼
┌──────────────────────────────┐
│  Supabase PostgreSQL DB      │
│  - Normalized Audit Sessions │
│  - Transactions, Anomalies   │
│  - Attestations, Findings    │
└──────────────────────────────┘
```

---

## 🚀 Quick Start

### 1. Prerequisites
- Node.js 18+ (Node.js 20 LTS recommended)
- Python 3.10+

### 2. Installation
```bash
# Clone repository
git clone https://github.com/bhaskarchoubey07-hub/dapp-auditregistry-mu4io5.git
cd dapp-auditregistry-mu4io5

# Install Node dependencies
npm install

# Install Python requirements
pip install -r backend/requirements.txt
```

### 3. Configure Environment Variables
Copy the provided templates:
```bash
cp .env.example .env
cp backend/.env.example backend/.env
```

### 4. Run Development Servers
In Terminal 1 (Frontend):
```bash
npm run dev
# Running on http://localhost:5173
```

In Terminal 2 (Backend API):
```bash
cd backend
python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload
# Running on http://localhost:8000
```

---

## 🧪 Automated Testing

Run the entire unified test suite (Smart Contracts + Python Backend):
```bash
npm test
```

Or run individual suites:
```bash
# Hardhat Solidity Tests (6 passing)
npm run test:contracts

# Backend Pytest Suite (4 passing)
npm run test:backend

# Production Frontend Build
npm run build
```

---

## 📋 Features & Capabilities

1. **Executive Fintech Dashboard:** Real-time volume tracking, double-entry reconciliation status, risk index, and searchable ledger.
2. **Upload Real Data (CSV):** Autodetects columns, handles missing values, flags duplicates, sanitizes against spreadsheet formula injection, and provides a preview modal before committing.
3. **Double-Entry Balance Engine:** Calculates Total Debits vs Total Credits and enforces Pacioli's accounting identity.
4. **AI Anomaly Detection:** Transparent Isolation Forest model with plain-English rule attribution (AML \$10K limit, \$9,000–\$9,999 structuring, Z-score divergence, round numbers).
5. **Benford's Law Forensic Screening:** Compares observed leading-digit frequencies with theoretical log10 distribution to flag ledger irregularities.
6. **Blockchain Audit Trail:** Computes deterministic SHA-256 Merkle roots and anchors them on-chain with 3-way consensus verification.
7. **Official Audit Certificate Exporter:** Generates official printable audit certificates with digital timestamps and JSON verification packages.
8. **System Settings & Health:** Real-time telemetry monitoring Frontend, Backend, Supabase, AI Model, and Blockchain.

---

## 📚 Documentation Directory

- [`docs/SYSTEM_ARCHITECTURE_AUDIT.md`](docs/SYSTEM_ARCHITECTURE_AUDIT.md): Comprehensive Phase 0 architectural audit.
- [`docs/SUPABASE_SETUP.md`](docs/SUPABASE_SETUP.md): PostgreSQL schema, migration, and RLS guide.
- [`docs/API_DOCUMENTATION.md`](docs/API_DOCUMENTATION.md): Complete REST API endpoint reference.
- [`docs/BLOCKCHAIN_SETUP.md`](docs/BLOCKCHAIN_SETUP.md): Smart contract deployment, MetaMask setup, and verification.
- [`docs/AI_SERVICE_SETUP.md`](docs/AI_SERVICE_SETUP.md): Explainable Isolation Forest engine details.
- [`docs/SECURITY_AUDIT.md`](docs/SECURITY_AUDIT.md): Full-stack security assessment and formula injection defense.
- [`docs/FINAL_SYSTEM_TEST_REPORT.md`](docs/FINAL_SYSTEM_TEST_REPORT.md): Feature-by-feature test evidence matrix.
- [`docs/TROUBLESHOOTING.md`](docs/TROUBLESHOOTING.md): Operational runbook and troubleshooting steps.

---

## 🔒 Security Principles

- **Zero Secret Exposure:** `SUPABASE_SERVICE_ROLE_KEY` and private keys are never committed or exposed to the client bundle.
- **Formula Injection Immunity:** All ingested CSV values starting with `=`, `+`, `-`, `@` are neutralized.
- **Parameterized SQL:** All database transactions use strict parameter binding to eliminate SQL injection risks.
- **Row Level Security (RLS):** Enabled across all 11 database tables.
