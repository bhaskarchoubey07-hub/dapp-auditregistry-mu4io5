# AuditRegistry Enterprise REST API Documentation

**Version:** 2.0.0  
**Host:** `http://localhost:8000` (Local) / Production URL  
**Base Path:** `/api`  
**Security:** CORS enabled, Input sanitization against spreadsheet formula injection, zero secret exposure.

---

## 1. System & Health Endpoints

### `GET /health`
Basic microservice uptime and model status.
- **Response `200 OK`:**
  ```json
  {
    "status": "healthy",
    "service": "AuditRegistry-Enterprise-Backend",
    "version": "2.0.0",
    "aiModel": "IsolationForest",
    "contaminationRate": 0.08,
    "timestamp": "2026-09-22T13:00:00Z"
  }
  ```

### `GET /api/health/database`
Internal database reachability, table structure, and ephemeral read/write test (cleans up immediately).
- **Response `200 OK`:**
  ```json
  {
    "status": "healthy",
    "engine": "SQLite (Local Persistence Engine) / PostgreSQL (Supabase/Neon)",
    "databaseReachable": true,
    "latencyMs": 14.5,
    "tablesFound": 11,
    "requiredTablesOk": true,
    "readTest": "PASS",
    "writeTest": "PASS",
    "cleanupTest": "PASS"
  }
  ```

### `GET /api/system/health`
Holistic telemetry across Frontend, Backend, Database, AI Microservice, and Blockchain.
- **Response `200 OK`:**
  ```json
  {
    "status": "operational",
    "subsystems": {
      "frontend": { "status": "ONLINE", "url": "http://localhost:5173" },
      "backend": { "status": "ONLINE", "port": 8000 },
      "database": { "status": "ONLINE", "engine": "PostgreSQL", "tablesConfigured": 11 },
      "aiService": { "status": "ONLINE", "model": "IsolationForest" },
      "blockchain": { "status": "ONLINE", "targetChainId": 11155111, "contract": "0xd8b934580fcE35a11B58C6D73aDeE468a2833fa8" }
    }
  }
  ```

### `GET /api/system/settings`
Returns non-sensitive public configuration (thresholds, currency, default contract).

---

## 2. Audit Session Endpoints

### `POST /api/audit/sessions`
Creates an audit session for an organization or protocol.
- **Request Body:**
  ```json
  {
    "projectId": "corporate-treasury-2026-q3",
    "sessionName": "Q3 Statutory Ledger Audit",
    "transactions": []
  }
  ```
- **Response `200 OK`:**
  ```json
  {
    "sessionId": "4f9b8c2d-...",
    "projectId": "corporate-treasury-2026-q3",
    "sessionName": "Q3 Statutory Ledger Audit",
    "status": "INITIALIZED",
    "createdAt": "2026-09-22T13:05:00Z"
  }
  ```

### `GET /api/audit/sessions`
Returns all audit sessions with aggregated volume and reconciliation summaries.

### `GET /api/audit/sessions/{session_id}`
Returns granular session details, counts, and linked records.

---

## 3. Transaction Ingestion & Ledgers

### `POST /api/audit/sessions/{session_id}/transactions`
Ingests batches of transactions into a session. Sanitizes text against formula injection.
- **Request Body:**
  ```json
  [
    {
      "transactionRef": "TX-9001",
      "accountNumber": "ACC-101",
      "amount": 150000.00,
      "type": "CREDIT",
      "category": "Sales Revenue",
      "entryDate": "2026-09-01"
    }
  ]
  ```

### `GET /api/audit/sessions/{session_id}/transactions`
Retrieves all transactions and attached AI anomaly scores for an audit session.

---

## 4. Financial Audit & AI Processing

### `POST /api/audit/sessions/{session_id}/reconcile`
Computes double-entry debit/credit reconciliation and persists results to `reconciliations`.
- **Response `200 OK`:**
  ```json
  {
    "sessionId": "4f9b8c2d-...",
    "totalDebit": 59999.00,
    "totalCredit": 59999.00,
    "difference": 0.00,
    "isReconciled": true,
    "status": "BALANCED"
  }
  ```

### `POST /api/audit/sessions/{session_id}/anomalies`
Runs explainable Isolation Forest scoring.
- **Response `200 OK`:**
  ```json
  {
    "sessionId": "4f9b8c2d-...",
    "totalAnalyzed": 50,
    "anomaliesDetected": 4,
    "results": [
      {
        "transactionRef": "TX-2004",
        "isAnomaly": true,
        "anomalyScore": 0.94,
        "explanation": "Potential structuring (just below $10,000 threshold)"
      }
    ]
  }
  ```

### `POST /api/audit/sessions/{session_id}/benford`
Calculates first-digit logarithmic distribution and returns deviation metrics.

### `POST /api/audit/sessions/{session_id}/canonical-hash`
Generates deterministic canonical SHA-256 Merkle root hash for blockchain anchoring.

---

## 5. Blockchain Attestation & Certificates

### `POST /api/blockchain/record`
Records on-chain transaction receipt after MetaMask broadcast.
- **Request Body:**
  ```json
  {
    "sessionId": "4f9b8c2d-...",
    "dataHash": "0x4a91b2...",
    "transactionHash": "0x5c89a...",
    "blockNumber": 5892301,
    "chainId": "11155111",
    "contractAddress": "0xd8b934580fcE35a11B58C6D73aDeE468a2833fa8",
    "walletAddress": "0x71C2B9284F0740E7A678e794358a9eD6a195B401"
  }
  ```

### `GET /api/audit/sessions/{session_id}/certificate`
Generates authoritative cryptographic audit certificate payload with full audit metadata.
