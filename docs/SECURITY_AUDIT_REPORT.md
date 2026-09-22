# Cybersecurity Audit & Threat Model Report

**Project:** Automated Financial Audit & Compliance System (Audit Registry DApp)  
**Methodology:** OWASP Top 10 + Web3 Threat Matrix + STRIDE Model  

---

## 1. STRIDE Threat Model

| Threat Category | Target Component | Identified Risk | Implemented Countermeasure |
| :--- | :--- | :--- | :--- |
| **Spoofing** | Auditor Wallet | Malicious actor attempts to submit audits as another entity | Authenticated signing using MetaMask browser provider (`msg.sender` validation). |
| **Tampering** | Audit Dataset | Ingested financial records modified in memory before anchoring | Deterministic SHA-256 / Keccak-256 canonical hashing ensures any single-bit alteration breaks hash equivalence. |
| **Repudiation** | Audit Submission | Auditor claims they never performed or submitted an audit | Smart contract emits indexed `AuditRecordRegistered` event embedding `registeredBy` address and immutable block timestamp. |
| **Information Disclosure** | Public Ledger | Corporate financial statements exposed to competitors on public chain | Zero plain financial records stored on-chain; only one-way cryptographic hash digests are anchored. |
| **Denial of Service** | Web API / RPC | Flooding endpoint with invalid transaction arrays | Pydantic strict schema validation and rate limiting on FastAPI endpoints. |
| **Elevation of Privilege** | Smart Contract | Attacker overwrites previously registered audit record | Smart contract rejects duplicate registrations with explicit `AlreadyAnchored` / `exists` revert. |

---

## 2. Security Remediation Plan
1. **Never commit `.env`**: `.gitignore` contains `.env`, `.env.local`, and private key definitions.
2. **Strict Sanitization**: Input fields in frontend and backend are typed and bound to prevent SQL injection and XSS.
3. **CORS Hardening**: Production backend restricts CORS to whitelisted Vercel production domains.
