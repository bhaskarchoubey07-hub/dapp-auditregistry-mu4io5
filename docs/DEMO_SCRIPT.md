# 5-Minute Demonstration Script

---

### Step 1: System Introduction (0:00 – 1:00)
- **Action:** Open the web application in browser (`http://localhost:5173` or Vercel URL).
- **Narration:** *"Welcome to the Automated Financial Audit & Compliance System. In modern corporate environments, auditing is typically retrospective and vulnerable to post-period tampering. Today, I will demonstrate how our system combines automated reconciliation, explainable AI anomaly detection, and decentralized blockchain verification on Ethereum Sepolia."*

---

### Step 2: Dashboard & Ledger Walkthrough (1:00 – 2:00)
- **Action:** Highlight the KPI cards on the Executive Dashboard.
- **Narration:** *"On the dashboard, we see total audited volume, verified records, flagged anomalies, and our calculated audit risk index. Looking at our ledger, transactions are continuously evaluated against compliance policies."*

---

### Step 3: Anomaly Detection Review (2:00 – 3:00)
- **Action:** Click **AI Anomaly Detection** tab on the sidebar.
- **Narration:** *"In this view, we inspect transactions flagged by our Isolation Forest pipeline. For example, transaction TX-1004 was flagged with a 0.94 anomaly score because the amount of $9,999 indicates potential AML structuring just below the $10,000 regulatory threshold. Notice that our model provides clear, human-understandable explanations rather than an uninterpretable black box."*

---

### Step 4: Blockchain Anchoring via MetaMask (3:00 – 4:00)
- **Action:** Navigate to **Blockchain Audit Trail** tab and click **Anchor Proof on Sepolia**.
- **Narration:** *"Once the audit batch is reviewed, the system deterministically calculates a canonical Keccak-256 hash. When I click 'Anchor Proof', MetaMask opens, prompting the auditor to sign the transaction. The cryptographic hash is permanently and immutably written to our smart contract."*

---

### Step 5: Independent Verification & Conclusion (4:00 – 5:00)
- **Action:** In the Verify Record card, click **Verify Attestation**. Show the success badge with block timestamp and auditor address.
- **Narration:** *"Any external stakeholder, bank, or regulatory auditor can independently verify this audit hash on-chain. As you can see, the smart contract confirms the attestation and returns the block timestamp and auditor address. This guarantees mathematical tamper-evidence without disclosing sensitive corporate data. Thank you."*
