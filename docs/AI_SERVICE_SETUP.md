# Explainable AI Anomaly Detection Engine

**Model File:** [`backend/model.py`](file:///c:/Users/bhask/OneDrive/Documents/dapp-auditregistry-mu4io5/backend/model.py)  
**Algorithm:** `IsolationForest` (`scikit-learn`) + Deterministic Heuristics  
**Default Contamination:** `0.08` (8%)  

---

## 1. Algorithmic Overview

Financial auditing demands **transparent, explainable AI** rather than opaque "black-box" scoring. The engine combines unsupervised machine learning (Isolation Forest) with financial compliance rules.

```
       Financial Transactions
                 │
                 ▼
      Feature Engineering
   ┌─────────────────────────────┐
   │ • Amount & Z-score          │
   │ • High-value round numbers  │
   │ • AML $10,000 threshold     │
   │ • Structuring ($9,000-$9,999│
   └─────────────┬───────────────┘
                 │
                 ▼
       Isolation Forest Model
                 │
                 ▼
   Explainable Reason Generation
   (Outputs score, risk level & plain-English reasons)
```

---

## 2. Feature Attribution & Explainability

For every transaction, the detector outputs:
1. **Anomaly Score:** Normalized float between `0.0` and `1.0`.
2. **Risk Category:** `LOW`, `MEDIUM`, `HIGH`, `CRITICAL`.
3. **Transparent Reason String:** Explicit plain-English explanation of rule triggers:
   - *"Exceeds $10,000 regulatory reporting threshold"*
   - *"Suspicious amount pattern (possible structuring just below $10K)"*
   - *"High statistical divergence from batch mean (Z-Score > 2.2σ)"*
   - *"High-value round denomination (frequently seen in unauthorized transfers)"*

---

## 3. Compliance & Terminology Disclosures

To prevent misleading claims of infallible fraud detection, the engine adheres to strict auditing standards:
- AI outputs are classified as **"Anomaly Indicators"** or **"Potentially Unusual Transactions"**.
- Findings are never labeled as conclusive proof of fraud; final disposition is reserved for statutory human auditors.
