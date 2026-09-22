# Financial Audit & Compliance Rules Report

**Project:** Automated Financial Audit & Compliance System (Audit Registry DApp)  

---

## 1. Compliance Rule Engine Specification

### Rule 1: Double-Entry Balancing Verification
- **Principle:** Every financial event must have balanced debit and credit entries ($\sum \text{Debits} == \sum \text{Credits}$).
- **Formula:** $\Delta = \left| \sum \text{Debits} - \sum \text{Credits} \right|$
- **Threshold:** Discrepancy $\Delta > 0.01$ USD triggers a **Critical Reconciliation Discrepancy**.
- **Auditor Action:** Batch cannot be finalized until reconciling journal entry is provided.

### Rule 2: Anti-Money Laundering (AML) Large-Transaction Monitoring
- **Regulatory Framework:** Bank Secrecy Act (BSA) Currency Transaction Report (CTR) threshold.
- **Trigger:** Any transaction with $\text{Amount} \ge \$10,000.00$.
- **Finding:** High Severity Flag: Requires proof of source of funds and executive sign-off.

### Rule 3: Anti-Structuring (Smurfing) Detection
- **Trigger:** Transactions originating from the same account with amounts between $\$9,000.00$ and $\$9,999.99$.
- **Finding:** High Severity Flag: Potential structuring to evade CTR reporting.

### Rule 4: Duplicate Record Detection
- **Exact Collision:** Repeated `transactionRef`.
- **Fuzzy Collision:** Same `accountNumber`, identical `amount`, within a 48-hour timestamp window.
- **Finding:** Medium Severity Flag: Potential duplicate billing or double-spend glitch.

---

## 2. Finding Review Lifecycle

```text
[DETECTED] ──> [UNDER REVIEW] ──> [RESOLVED / CLEARED]
                    │
                    └──> [ESCALATED / FLAGGED]
```

- **Open / Under Review:** Initial state when algorithm detects violation.
- **Resolved:** Auditor provides supporting documentation (e.g. valid invoice, counter-entry).
- **Flagged:** Escalated to compliance committee or executive board.
