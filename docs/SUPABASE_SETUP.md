# Supabase PostgreSQL Setup & Configuration Guide

**Project:** AuditRegistry — Enterprise Financial Audit & Compliance System  
**Database:** PostgreSQL 15+ (Hosted on Supabase / Neon Serverless)  
**Schema:** [`backend/schema.sql`](file:///c:/Users/bhask/OneDrive/Documents/dapp-auditregistry-mu4io5/backend/schema.sql)  

---

## 1. Create Supabase Project

1. Navigate to [Supabase](https://supabase.com/) and sign in with your GitHub or developer account.
2. Click **New Project** in your organization dashboard.
3. Provide project details:
   - **Name:** `auditregistry-enterprise`
   - **Database Password:** Generate a secure password (save this securely).
   - **Region:** Choose a region nearest your deployment or users (e.g., `us-east-1` or `eu-central-1`).
4. Click **Create new project** and wait ~2 minutes for PostgreSQL provisioning.

---

## 2. Find Project URL

1. In your Supabase project dashboard, open the left sidebar and navigate to **Project Settings** (gear icon) → **API**.
2. Locate the **Project URL** under "Project Configuration".
   - Example format: `https://xyzcompany.supabase.co`

---

## 3. Find Anon / Public Key

1. Under **Project Settings** → **API** → **Project API keys**.
2. Find the key labeled **`anon` `public`**.
3. Copy this key. It is safe for browser usage because table access is governed by Row Level Security (RLS) policies.

---

## 4. Find Service-Role Key

1. Under **Project Settings** → **API** → **Project API keys**.
2. Find the key labeled **`service_role` `secret`**.
3. **SECURITY MANDATE:**
   - NEVER commit this key to Git.
   - NEVER put this key in `.env` files prefixed with `VITE_`.
   - Store it ONLY in the server-side `backend/.env` file.

---

## 5. Configure Environment Variables

### Frontend Configuration (`.env`)
In the root directory, ensure `.env` contains:
```dotenv
VITE_SUPABASE_URL=https://xyzcompany.supabase.co
VITE_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
VITE_API_URL=http://localhost:8000
VITE_CONTRACT_ADDRESS=0xd8b934580fcE35a11B58C6D73aDeE468a2833fa8
VITE_EXPECTED_CHAIN_ID=11155111
VITE_CHAIN_ID=11155111
```

### Backend Configuration (`backend/.env`)
In `backend/.env`, set:
```dotenv
DATABASE_URL=postgresql://postgres:[YOUR-PASSWORD]@db.xyzcompany.supabase.co:5432/postgres?sslmode=require
SUPABASE_URL=https://xyzcompany.supabase.co
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
PORT=8000
FRONTEND_URL=http://localhost:5173
```

---

## 6. Run Schema Migrations

1. In your Supabase dashboard, click **SQL Editor** from the left navigation.
2. Click **+ New Query**.
3. Open [`backend/schema.sql`](file:///c:/Users/bhask/OneDrive/Documents/dapp-auditregistry-mu4io5/backend/schema.sql), copy the entire SQL script, and paste it into the editor.
4. Click **Run** (or press `Ctrl+Enter`).
5. Verify output:
   - Tables created: `users`, `audit_sessions`, `transactions`, `reconciliations`, `anomalies`, `compliance_findings`, `benford_results`, `audit_records`, `blockchain_records`, `audit_certificates`, `system_settings`.
   - Indexes and constraints applied.

---

## 7. Configure Row Level Security (RLS)

The `backend/schema.sql` script automatically enables RLS on all 11 tables:
- **Public Read:** Enabled for non-sensitive data via the `anon` key (`system_settings`, `audit_sessions`, `transactions`, `reconciliations`, `anomalies`, `benford_results`, `blockchain_records`, `audit_certificates`).
- **Service Role Write:** Enabled exclusively for the backend service role or direct connection pool.
- Audit actors cannot overwrite or tamper with immutable historical audit sessions.

---

## 8. Verify Connection

Test backend health and database connectivity by running:
```bash
curl http://localhost:8000/api/health/database
```
Expected response:
```json
{
  "status": "healthy",
  "database": "connected",
  "tables": 11,
  "timestamp": "2026-09-22T12:45:00Z"
}
```

---

## 9. Test Database Functionality

The backend includes a self-contained read/write/rollback diagnostic test:
```bash
python -m pytest backend/tests/test_db.py
```
This test:
1. Opens a temporary transaction.
2. Writes an ephemeral audit session.
3. Inserts sample transactions and computes reconciliation.
4. Reads back the records.
5. Immediately rolls back so no orphan records remain in production.

---

## 10. Troubleshooting

| Issue | Likely Cause | Solution |
| :--- | :--- | :--- |
| `connection refused (port 5432)` | Firewall or IPv6 resolution failure | Use Supabase connection pooling address on port `6543` or append `?sslmode=require`. |
| `permission denied for table` | RLS policy blocking query | Confirm your request includes the `apikey` / `Authorization: Bearer <ANON_KEY>` header. |
| `Key ... is not present in table "audit_sessions"` | Foreign key violation | Always create the parent `audit_sessions` entry before adding child transactions or anomaly records. |
| `Failed to fetch` in frontend | Backend offline or CORS issue | Ensure `backend/main.py` is running on `http://localhost:8000` with `FRONTEND_URL=http://localhost:5173`. |
