# Backend Architecture Report

**Project:** Automated Financial Audit & Compliance System (Audit Registry DApp)  
**Component:** Backend Core REST API  
**Framework:** Python FastAPI / Uvicorn  

---

## 1. Architecture Overview
The backend service (`backend/main.py`) provides high-performance, asynchronous REST API endpoints for:
- Ingestion and schema sanitization of financial transactions.
- Automated double-entry financial reconciliation.
- Integration with the Isolation Forest AI anomaly detector.
- Deterministic canonical JSON serialization and cryptographic hash computation for on-chain anchoring.

---

## 2. API Endpoints Specification

| Method | Endpoint | Description | Request Body | Response Payload |
| :--- | :--- | :--- | :--- | :--- |
| `GET` | `/health` | Service uptime and model health | None | `{"status": "healthy", "service": "AuditRegistry-Core-Backend", ...}` |
| `POST` | `/api/audit/evaluate` | Executes reconciliation, ML scoring, and hash calculation | `AuditBatchRequest` (List of transactions, projectId) | `AuditEvaluationResponse` (Metrics, reconciliation status, anomaly count, deterministic hash) |

---

## 3. Deterministic Hash Generation Algorithm
To ensure mathematical reproducibility across distributed systems:
1. All transactions in the batch are sorted deterministically by their unique `transactionRef`.
2. The payload is serialized into canonical JSON with sorted keys and no extraneous whitespace:
   `json.dumps(canonical_payload, sort_keys=True, separators=(',', ':'))`
3. A SHA-256 / Keccak-256 digest is generated over the UTF-8 bytes of this canonical string.
4. The resulting 32-byte hexadecimal string is passed to the smart contract for anchoring.
