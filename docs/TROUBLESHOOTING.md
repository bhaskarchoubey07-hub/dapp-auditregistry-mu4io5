# Troubleshooting Guide & Operational Runbook

**Project:** AuditRegistry — Enterprise Financial Audit System  

---

## 1. Quick Diagnostic Checklist

Run the following commands to check the operational status of all components:

```bash
# 1. Run all automated tests (Solidity contracts + Python backend)
npm test

# 2. Check backend system health
curl http://localhost:8000/api/system/health

# 3. Check database health and reachability
curl http://localhost:8000/api/health/database

# 4. Verify frontend production build
npm run build
```

---

## 2. Common Scenarios & Resolutions

### A. MetaMask Not Detected
- **Cause:** User is running in a private window, incognito, or an unsupported browser without the MetaMask extension.
- **Resolution:** The UI features a zero-install **Built-In Auditor Wallet (Instant Demo Mode)** (`0x71C2B9284F0740E7A678e794358a9eD6a195B401`). Click "Connect Wallet" and choose the Built-In Auditor Wallet. All on-chain features, hash anchoring, and verifications will work immediately.

### B. Backend API Unavailable
- **Symptoms:** System settings or health monitor shows Backend as `OFFLINE`.
- **Resolution:** Start the FastAPI service:
  ```bash
  cd backend
  python -m uvicorn main:app --host 127.0.0.1 --port 8000
  ```

### C. Database Connection Fallback
- **Symptoms:** `SUPABASE_URL` / `DATABASE_URL` is unconfigured.
- **Resolution:** The database layer automatically falls back to an embedded SQLite database (`backend/auditregistry_local.db`) with an identical 11-table schema. To connect to Supabase PostgreSQL, add your `DATABASE_URL` to `backend/.env`.

### D. CSV Upload Validation Errors
- **Symptoms:** CSV upload displays "Could not detect Amount column".
- **Resolution:** Download the official sample template by clicking **"Download Sample CSV"** on the Ingestion tab. Ensure column headers include `transaction_id`, `account_number`, `amount`, and `type`.

### E. Wrong Network in MetaMask
- **Symptoms:** Verification or anchoring fails with chain mismatch.
- **Resolution:** Ensure MetaMask is switched to Sepolia (Chain ID `11155111`).
