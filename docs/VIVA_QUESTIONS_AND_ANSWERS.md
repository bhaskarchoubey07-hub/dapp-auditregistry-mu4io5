# Comprehensive Viva Voce Questions & Answers

**Project:** Automated Financial Audit & Compliance System (Audit Registry DApp)  

---

### Q1: What is the main objective of this project?
**Answer:** The objective is to eliminate the retrospective, sample-based nature of financial auditing by providing real-time double-entry reconciliation, unsupervised machine learning anomaly detection, and decentralized cryptographic proof anchoring on an immutable Ethereum blockchain.

---

### Q2: Why did you choose Isolation Forest over supervised algorithms like Random Forest or XGBoost?
**Answer:** In genuine financial auditing, fraud and accounting errors are extremely rare (<1% of volume) and constantly change form. Supervised models require thousands of historical labeled fraud instances, which are proprietary and suffer from extreme class imbalance. Isolation Forest isolates outliers based purely on structural sparsity without needing historical labels.

---

### Q3: How do you prevent confidential financial data from being exposed on the public Ethereum blockchain?
**Answer:** We never store plaintext ledger entries on-chain. We generate a deterministic Keccak-256 / SHA-256 hash digest of the canonically sorted dataset. Only this 32-byte cryptographic digest is anchored on-chain. It is mathematically impossible to reconstruct the financial entries from this hash, ensuring full GDPR and corporate privacy compliance.

---

### Q4: What makes the on-chain hash tamper-evident?
**Answer:** Because cryptographic hash functions have the avalanche effect: changing a single digit or comma in any transaction completely alters the resulting 32-byte hash digest. If anyone modifies historical records, regenerating the hash will immediately mismatch the immutable hash stored on the Ethereum blockchain.

---

### Q5: How does the smart contract handle duplicate or overwritten audit records?
**Answer:** In `AuditRegistry.sol`, each record is indexed by `recordKey = keccak256(abi.encodePacked(projectId, dataHash))`. Before storing, the contract requires `!records[recordKey].exists`. If an attempt is made to overwrite an existing record, the transaction reverts with `"Audit record already registered"`.

---

### Q6: What is canonical JSON sorting and why is it required?
**Answer:** Different browsers, programming languages, and operating systems serialize JSON keys in arbitrary orders. To guarantee that the calculated hash is identical across Python, Node.js, and browser environments, all transaction keys and rows are sorted canonically before hashing.

---

### Q7: What are the free-tier limitations of your deployment stack?
**Answer:** 
1. Render free-tier web services sleep after 15 minutes of inactivity and take 50–90 seconds to wake up on the first request.
2. Neon PostgreSQL suspends compute after 5 minutes of inactivity (wakes in ~500ms).
3. Vercel Hobby tier caps function duration at 10 seconds.
4. Sepolia testnet requires free faucet ETH for gas.

---

### Q8: How does your UI prevent chart rendering dimension bugs?
**Answer:** In React charting libraries, flexible containers with zero height or unconstrained flex bounds throw negative dimension errors (`width(-1)`). We wrap all chart and metric components with explicit CSS minimum heights (e.g., `min-h-[300px]`) and guard rendering until transactions have loaded into state.

---

### Q9: How does the system detect AML structuring (smurfing)?
**Answer:** The Bank Secrecy Act requires Currency Transaction Reports (CTRs) for cash transactions $\ge \$10,000$. Fraudulent actors often split funds into amounts just below this threshold (e.g., $\$9,500$ or $\$9,999$). Our feature pipeline specifically flags transactions between $\$9,000$ and $\$9,999$ as potential structuring.

---

### Q10: What future improvements are planned?
**Answer:** Integrating Zero-Knowledge SNARK proofs (zk-SNARKs) to mathematically prove financial solvency and compliance without disclosing total volume numbers, and implementing multi-auditor DAO governance for firm accreditation.
