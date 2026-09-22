# Security Audit & Vulnerability Assessment

**Project:** AuditRegistry — Enterprise Financial Audit  
**Date:** 2026-09-22  
**Scope:** Full-Stack (Frontend, Backend API, Smart Contracts, Supabase PostgreSQL, CSV Ingestion)  

---

## 1. Vulnerability Assessment Matrix

| Vector | Risk | Mitigation Implemented | Status |
| :--- | :--- | :--- | :--- |
| **CSV Formula Injection** | Critical | Strips/prefixes leading characters (`=`, `+`, `-`, `@`, `\t`, `\r`) in parser and export pipelines. | **SECURE** |
| **Service Role Key Exposure** | High | `SUPABASE_SERVICE_ROLE_KEY` is confined strictly to `backend/.env`. Never exposed in `VITE_` variables. | **SECURE** |
| **Private Key Exposure** | Critical | Zero private keys in frontend bundles or Git. Signing managed via MetaMask or client demo wallet. | **SECURE** |
| **SQL Injection** | Critical | Parameterized queries used across all psycopg and SQLite database operations (`cur.execute(query, params)`). | **SECURE** |
| **Row Level Security (RLS)** | High | RLS enabled on all 11 Supabase tables in `backend/schema.sql`. Public `anon` limited to read policies. | **SECURE** |
| **Smart Contract Re-entrancy** | High | No external state-modifying calls in `AuditRegistry.sol`; state mutation precedes event emissions. | **SECURE** |
| **Duplicate Audit Records** | Medium | Smart contract reverts on duplicate record key (`keccak256(projectId, dataHash)`). | **SECURE** |
| **CORS Misconfiguration** | Medium | Explicitly allows origin whitelist with credential headers in `backend/main.py`. | **SECURE** |

---

## 2. Spreadsheet Formula Sanitization

When exporting or displaying user-supplied transactions, spreadsheet applications (Excel, Google Sheets, LibreOffice) can execute arbitrary commands if a cell begins with formula prefixes. 

Implemented defense (`backend/main.py` & `src/App.jsx`):
```python
def sanitize_cell(value: Any) -> str:
    val_str = str(value).strip()
    if val_str and val_str[0] in ('=', '+', '-', '@', '\t', '\r'):
        return "'" + val_str
    return val_str
```

---

## 3. Environment Variable Hygiene

- `.gitignore` strictly excludes `.env`, `.env.local`, `.env.*.local`.
- Startup diagnostics validate expected formats without writing secret contents to logs or stdout.
