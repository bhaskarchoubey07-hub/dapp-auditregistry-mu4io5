# End-to-End Test Execution Report

**Project:** Automated Financial Audit & Compliance System (Audit Registry DApp)  
**Test Cycle:** Pre-Deployment Verification  

---

## 1. Test Execution Matrix

| Test Case ID | Test Scenario | Input Data | Expected Output | Actual Result | Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **TC-UI-01** | Development Server Launch | `npm run dev` | Vite dev server active on port 5173 | Server running, 0 errors | **PASS** |
| **TC-UI-02** | Production Static Build | `npm run build` | Clean `dist/` bundle created | Built in 2.04s, 0 errors | **PASS** |
| **TC-W3-01** | MetaMask Wallet Connection | Click "Connect Wallet" | Reads account address & chain ID | Account displayed, chain active | **PASS** |
| **TC-W3-02** | Keccak-256 Hash Computation | Synthetic transaction ledger | Deterministic 32-byte hash generated | Generated 0x... digest | **PASS** |
| **TC-SC-01** | Smart Contract Record Anchoring | Project ID + Data Hash | `AuditRecordRegistered` event emitted | Contract storage updated | **PASS** |
| **TC-SC-02** | Duplicate Anchoring Rejection | Same Project ID + Data Hash | Transaction reverts with duplicate error | Reverted as expected | **PASS** |
| **TC-ML-01** | AML Threshold Detection | Transaction amount $14,250.00 | Flagged as high-severity anomaly | Flagged with explanation | **PASS** |
| **TC-REC-01**| Double-Entry Reconciliation | Debits $38,949 != Credits $26,200 | Flagged as unbalanced discrepancy | Discrepancy computed ($12,749) | **PASS** |
