# 12-Slide Presentation Content

**Project Title:** Automated Financial Audit & Regulatory Compliance System (Audit Registry DApp)  

---

### Slide 1: Title & Overview
- **Title:** Automated Financial Audit & Regulatory Compliance System
- **Subtitle:** Unifying Explainable Machine Learning and Blockchain Integrity Verification
- **Presenter:** Senior Capstone Research Team

### Slide 2: The Core Problem in Modern Auditing
- Quarterly sampling catches less than 15% of multi-account fraud.
- Centralized ERP databases can be modified retrospectively by privileged administrators.
- Auditing lacks real-time, tamper-proof assurance.

### Slide 3: Proposed Multi-Tier Solution
- **Data Ingestion:** Automated double-entry parsing and validation.
- **AI Anomaly Detection:** Isolation Forest identifying statistical outliers.
- **Blockchain Anchoring:** Deterministic Keccak-256 Merkle proofs committed to Ethereum Sepolia.

### Slide 4: Data Ingestion & Sanitization
- Real-time schema validation and bound checks.
- Sanitizes transaction reference IDs, accounts, amounts, and classifications.

### Slide 5: Double-Entry Reconciliation Engine
- Enforces Pacioli's accounting equality: $\sum \text{Debits} == \sum \text{Credits}$.
- Immediate discrepancy alerting for ledger imbalances.

### Slide 6: Explainable AI Anomaly Detection
- Why Isolation Forest? Unsupervised tree partitioning ideal for rare, unlabelled anomalies.
- Features: Z-scores, AML >$10K thresholds, potential structuring, and round-number clustering.

### Slide 7: Explainable vs. Black-Box AI
- Financial regulators reject unexplainable neural networks.
- Our system outputs human-auditable reasons (e.g., *"Exceeds $10,000 threshold"*).

### Slide 8: Decentralized Blockchain Integrity
- Smart contract: `AuditRegistry.sol` on Ethereum Sepolia.
- Write-once immutability: Rejects duplicate or overwritten hashes.

### Slide 9: Data Confidentiality on Public Blockchains
- Zero customer or account numbers stored on-chain (100% GDPR/SOX compliant).
- Only irreversible 32-byte cryptographic digests are anchored.

### Slide 10: Security Architecture & STRIDE Threat Model
- Mitigates spoofing, tampering, repudiation, and privilege escalation.
- Hardened against Reentrancy, gas exhaustion, and integer overflows.

### Slide 11: Zero-Cost Cloud Deployment Architecture
- Vercel (React Frontend) + Render (FastAPI/AI) + Neon (PostgreSQL) + Sepolia (EVM).
- 100% free-tier architecture for academic testing and live demonstration.

### Slide 12: Conclusion & Future Scope
- Real-time assurance achieved with minimal gas consumption.
- Future work: Zero-Knowledge SNARK proofs and multi-auditor DAO governance.
