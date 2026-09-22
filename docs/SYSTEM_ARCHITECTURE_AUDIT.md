# AuditRegistry — Enterprise Audit: System Architecture Audit

**Date:** 2026-09-22  
**Version:** 1.0.0-AUDIT  
**Lead Roles:** Full-Stack, Web3, AI/ML, Database, QA, DevOps Engineer  
**Status:** Phase 0 Inspection Complete  

---

## 1. Executive Summary & Current Architecture

AuditRegistry is an Enterprise Financial Audit & Compliance decentralized application (DApp) designed to ingest corporate accounting ledgers, execute double-entry reconciliation, run explainable AI anomaly detection (Isolation Forest), conduct Benford's Law forensic analysis, anchor deterministic canonical cryptographic Merkle hashes on EVM blockchains, and issue cryptographic audit certificates.

### High-Level Topology

```
┌─────────────────────────────────────────────────────────────┐
│                 React + Vite Frontend (UI)                  │
│  8 Modules: Executive Dashboard, CSV Ingestion, AI Anomaly, │
│  Benford Forensic, Blockchain Trail, Double-Entry Balance,  │
│  Export Certificate, System Settings                         │
└──────────────┬───────────────────────────────┬──────────────┘
               │ (Direct/REST)                 │ (EIP-1193 / BrowserProvider)
               ▼                               ▼
┌──────────────────────────────┐  ┌───────────────────────────┐
│     FastAPI Backend & AI     │  │   Ethereum / EVM Smart    │
│    Microservice (Port 8000)  │  │         Contract          │
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

## 2. Inventory of Existing Components & Status

### 2.1 Frontend (`src/`)
- **Technology:** React 18, Vite 5.4, Lucide React icons, Tailwind CSS (via CDN).
- **Core Files:**
  - `src/App.jsx`: Monolithic component (1,866 lines) containing all 8 tab views, state management, CSV parsing, Benford computation, local rule evaluation, and Dual-Mode Web3 provider.
  - `src/main.jsx`: Vite React root mounting.
  - `src/index.css`: Tailwind directives and theme base styles.
  - `index.html`: Tailwind CDN script and esm importmap.
- **Build Status:** Compiles cleanly (`npm run build` exits with code 0 in ~14.4s).

### 2.2 Backend & AI Service (`backend/`)
- **Technology:** Python 3.10+ (Running on Python 3.14 in local environment), FastAPI, Uvicorn, scikit-learn, pandas, pydantic.
- **Core Files:**
  - `backend/main.py`: FastAPI application with CORS middleware, `/health` endpoint, and `/api/audit/evaluate` endpoint.
  - `backend/model.py`: `FinancialAnomalyDetector` class wrapping `scikit-learn` `IsolationForest` (contamination=0.08) with explainable attribution rules (AML $10K limit, potential structuring $9,000–$9,999, Z-score divergence, round-number clustering).
  - `backend/schema.sql`: Initial PostgreSQL schema defining `users`, `audit_batches`, `transactions`.
  - `backend/requirements.txt`: Python package specifications.
- **Status:** Fast, functional, but isolated. Currently not integrated into the frontend workflow.

### 2.3 Smart Contracts (`contracts/`)
- **Technology:** Solidity ^0.8.20.
- **Core Files:**
  - `contracts/AuditRegistry.sol`: Canonical registry contract with `registerAuditRecord(string calldata projectId, bytes32 dataHash)` and `verifyAuditRecord(string calldata projectId, bytes32 dataHash)`.
  - `contracts/ComplianceAuditRegistry.sol`: Enterprise variant with role-based access control.
  - `contracts/scripts/deploy.js`: Hardhat deployment script.
  - `hardhat.config.cjs`: Hardhat configuration for Solidity 0.8.20 optimizer, Sepolia network, and local test network.
  - `test/AuditRegistry.test.js`: Hardhat test suite verifying registration, duplicate prevention, empty projectId revert, zero hash revert, and verification lookups.
- **Status:** Contract code is solid and backward-compatible with Remix VM and Sepolia.

---

## 3. What Already Works

1. **Frontend UI Rendering & Navigation:**
   - All 8 navigation tabs (`dashboard`, `ingestion`, `ai`, `benford`, `blockchain`, `reconciliation`, `reports`, `settings`) switch views cleanly without crashing.
2. **Dual-Mode Web3 Provider Architecture:**
   - Detects MetaMask browser extension via standard `window.ethereum` and EIP-6963.
   - Provides a zero-install **Built-In Auditor Wallet (Instant Demo Mode)** (`0x71C2B9284F0740E7A678e794358a9eD6a195B401`) if MetaMask is absent, preventing browser blockers.
   - Handles network switching to Sepolia (Chain ID `11155111`).
3. **Client-Side CSV Parsing:**
   - Ingests tabular CSVs, handles credit/debit detection, strips currency symbols, filters malformed rows, and generates import statistics.
4. **Benford's Law Calculation:**
   - Extracts leading digits (1–9), computes observed percentages, compares them to theoretical log10 frequencies, and detects statistical divergence.
5. **AI Model Logic (Standalone):**
   - `backend/model.py` provides working Isolation Forest training and transparent, explainable reason strings.
6. **Smart Contract ABI & Hardhat Suite:**
   - `AuditRegistry.sol` matches `dapp.config.json` ABI 100%.

---

## 4. What Is Incomplete & What Is Missing

### 4.1 Missing Integrations
1. **Frontend ↔ Backend Integration:**
   - The frontend currently performs calculations in client-side memory rather than calling `POST /api/audit/evaluate` on the FastAPI backend.
   - When the user uploads a CSV, it does not send the batch to the backend or persist it to the database.
2. **Backend ↔ Supabase PostgreSQL Integration:**
   - `backend/main.py` has no database connection logic, ORM/query builder, or Supabase client.
   - Data ingested through the API is not saved to PostgreSQL tables.
3. **Frontend ↔ Supabase Integration:**
   - Neither `@supabase/supabase-js` nor Supabase REST calls exist in `src/`.
   - The dashboard relies entirely on initial mock corporate constants or browser `localStorage`.
4. **End-to-End Real Data Flow:**
   - The requested pipeline (`Frontend → Backend/API → Supabase → AI/Audit Processing → Blockchain Hash Anchoring → Certificate`) is fractured into disconnected pieces.

### 4.2 Missing Database Tables (Evaluated against Phase 2 requirements)
The current `backend/schema.sql` only has:
- `users`
- `audit_batches`
- `transactions`

Required tables missing from schema:
- `audit_sessions` (or consolidating `audit_batches` to canonical audit sessions)
- `audit_records` (for cryptographic attestations and Merkle proofs)
- `anomalies` (granular AI anomaly tracking)
- `compliance_findings` (regulatory findings: AML, structuring, velocity)
- `reconciliations` (double-entry debit/credit delta calculations)
- `benford_results` (first-digit distribution metrics and goodness-of-fit stats)
- `blockchain_records` (on-chain transaction receipts, block numbers, gas used)
- `audit_certificates` (issued audit packages with signatures)
- `system_settings` (configurable risk thresholds, default network, active contract address)

### 4.3 Missing API Endpoints
The backend currently only exposes `/health` and `/api/audit/evaluate`. It lacks:
- `/api/health/database`: Safe database connectivity health check.
- `/api/audit/sessions`: Create, list, and fetch audit session state.
- `/api/audit/transactions`: Ingest, query, and filter transactions.
- `/api/audit/reconciliation`: Persist and retrieve double-entry balances.
- `/api/audit/anomalies`: Query explainable AI flags.
- `/api/audit/benford`: Compute and store Benford digit distribution.
- `/api/blockchain/record`: Store and retrieve on-chain anchoring receipts.
- `/api/audit/certificate`: Generate and verify downloadable audit certificates.
- `/api/system/settings`: Retrieve and update non-sensitive operational parameters.

### 4.4 Missing Environment Variables
- Root `.env.example` lacks:
  - `VITE_SUPABASE_URL`
  - `VITE_SUPABASE_ANON_KEY`
  - `VITE_API_URL`
  - `VITE_CHAIN_ID`
- Backend lacks:
  - `SUPABASE_URL`
  - `SUPABASE_SERVICE_ROLE_KEY`
  - `DATABASE_URL`
  - `AI_SERVICE_URL`
  - `BLOCKCHAIN_RPC_URL`
  - `JWT_SECRET`
- Missing environment validation utility on startup for both frontend and backend.

### 4.5 Package & Tooling Gaps
- `package.json` does not include:
  - `@supabase/supabase-js` (for frontend direct/fallback Supabase queries)
  - `hardhat` and `@nomicfoundation/hardhat-toolbox` in `devDependencies` (so `npx hardhat test` cannot run without prompt or global installation)
  - A PDF generation library or printable HTML stylesheet for generating official PDF certificates.

---

## 5. Security & Deployment Analysis

1. **Spreadsheet Formula Injection (CSV Injection):**
   - User-uploaded CSV fields are currently parsed without sanitizing leading characters (`=`, `+`, `-`, `@`), posing formula injection risks upon spreadsheet export.
2. **Secret Separation:**
   - No secrets are currently leaked in Git or frontend code.
   - We must strictly ensure that `SUPABASE_SERVICE_ROLE_KEY` and private keys are never referenced in frontend code or exposed via `VITE_` variables.
3. **Row Level Security (RLS):**
   - `schema.sql` does not enable PostgreSQL RLS or define security policies for anonymous vs authenticated auditor roles.
4. **Remix VM vs Sepolia Deployment:**
   - Default contract address in `dapp.config.json` points to Remix VM (`0xd8b934580fcE35a11B58C6D73aDeE468a2833fa8`), which cannot be queried by external public users without a public testnet deployment or fallback RPC.

---

## 6. Execution Roadmap & Prioritized Blockers

| Priority | Area | Blocker / Task | Resolution Strategy |
| :--- | :--- | :--- | :--- |
| **P0** | **Environment & Config** | Missing environment variables and validation utility | Update `.env.example`, implement strict runtime config validators for frontend and backend. |
| **P0** | **Database Schema** | Incomplete table structure in `schema.sql` | Expand `schema.sql` to include all 11 required tables, UUIDs, indexes, RLS policies, and document in `docs/SUPABASE_SETUP.md`. |
| **P0** | **Database Connection** | Backend cannot reach Supabase/PostgreSQL | Add connection pooling via `psycopg`/`SQLAlchemy` and Supabase client with safe `/api/health/database` endpoint. |
| **P1** | **Backend API Expansion** | Missing REST endpoints for real data flow | Implement full CRUD & processing endpoints in `backend/main.py`. |
| **P1** | **Frontend Data Wiring** | Frontend runs purely in local state | Wire `src/App.jsx` to API endpoints with automatic fallback to persistent Supabase and local cache. |
| **P1** | **Audit Certificate** | Only exports raw JSON; no formal PDF/report | Build formal printable/downloadable Audit Certificate with verified cryptographic hashes. |
| **P2** | **Hardhat Tooling** | `hardhat` missing from `package.json` | Add `hardhat` to devDependencies so automated smart contract tests run seamlessly. |
| **P2** | **Automated Tests** | Missing backend and end-to-end integration tests | Create pytest suite for backend API, AI model, and data integrity. |

---

*This audit document serves as the formal baseline for Phase 1 through Phase 20 execution.*
