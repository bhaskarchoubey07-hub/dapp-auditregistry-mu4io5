# Changelog

All notable changes to the **Automated Financial Audit & Compliance System (Audit Registry DApp)** will be documented in this file.

## [1.0.0] - 2026-09-21

### Added
- **Fintech UI/UX Suite:** Complete 11-module dashboard in `src/App.jsx` with KPI metrics, ledger filtering, double-entry reconciliation, and responsive dark layout.
- **Smart Contracts:**
  - `contracts/AuditRegistry.sol` (matches exact ABI from Remix VM export for 100% backward compatibility).
  - `contracts/ComplianceAuditRegistry.sol` (enterprise batch auditing and findings categorization).
  - `contracts/scripts/deploy.js` (Hardhat deployment script).
  - `test/AuditRegistry.test.js` (unit tests covering registration, verification, and duplicate prevention).
  - `hardhat.config.cjs` (Hardhat configuration for Solidity 0.8.20 and Sepolia network).
- **Backend Core API:**
  - `backend/main.py` (FastAPI REST service with reconciliation and deterministic hashing).
  - `backend/model.py` (Explainable Isolation Forest anomaly detector).
  - `backend/schema.sql` (PostgreSQL relational schema with indexes).
  - `backend/requirements.txt` and `backend/.env.example`.
- **Documentation Suite:**
  - `docs/REPOSITORY_BASELINE.md`
  - `docs/TESTING_AND_DEBUGGING_REPORT.md`
  - `docs/BACKEND_REPORT.md`
  - `docs/DATABASE_REPORT.md`
  - `docs/AI_ANOMALY_DETECTION_REPORT.md`
  - `docs/AUDIT_COMPLIANCE_REPORT.md`
  - `docs/SMART_CONTRACT_AUDIT.md`
  - `docs/CONTRACT_DEPLOYMENT_GUIDE.md`
  - `docs/SECURITY_AUDIT_REPORT.md`
  - `docs/END_TO_END_TEST_REPORT.md`
  - `docs/DEPLOYMENT_GUIDE.md`
  - `docs/FREE_TIER_LIMITATIONS.md`
  - `docs/PHASE_III_ACADEMIC_REPORT.md` (Full 25-section capstone report)
  - `docs/PRESENTATION_CONTENT.md`
  - `docs/VIVA_QUESTIONS_AND_ANSWERS.md`
  - `docs/DEMO_SCRIPT.md`
  - `docs/SETUP_GUIDE.md`
  - `docs/KNOWN_ISSUES.md`

### Fixed
- Fixed unhandled wallet cancellation errors by capturing `error.code === 4001`.
- Eliminated chart zero-dimension bugs by wrapping metrics in explicit CSS minimum heights.
- Resolved local Windows environment hook crash by removing broken `.gemini` telemetry plugin.
