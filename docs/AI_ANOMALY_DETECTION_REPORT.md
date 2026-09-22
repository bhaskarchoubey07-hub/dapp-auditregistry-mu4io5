# AI/ML Anomaly Detection Report

**Project:** Automated Financial Audit & Compliance System (Audit Registry DApp)  
**Algorithm:** Isolation Forest (Unsupervised Ensemble Tree-Based Partitioning)  
**Implementation:** Scikit-Learn / `backend/model.py`  

---

## 1. Algorithmic Rationale
In corporate financial auditing:
1. True anomalies (e.g., fraudulent transfers, accounting errors, unauthorized round-dollar wires) are extremely rare (<1% of volume).
2. Labeled datasets of financial fraud are proprietary, confidential, and subject to severe concept drift.
3. Supervised classifiers suffer from extreme class imbalance.

**Isolation Forest** addresses these challenges by isolating anomalies rather than profiling normal data points. Because anomalies have few similar points and distinct feature values, they are isolated closer to the root of randomized decision trees (shorter path lengths).

---

## 2. Feature Extraction & Engineering

| Feature | Type | Auditing Significance |
| :--- | :--- | :--- |
| `amount` | Continuous | Transaction magnitude in USD |
| `z_score` | Continuous | Statistical standard deviations from batch mean ($\frac{x - \mu}{\sigma}$) |
| `is_round` | Binary | Flags round numbers (e.g., $10,000.00, $5,000.00), which frequently indicate manual unauthorized overrides |
| `is_debit` | Binary | Distinguishes cash outflows from inflows |
| `exceeds_aml_limit` | Binary | Flags transactions $\ge \$10,000$ (Bank Secrecy Act / AML CTR threshold) |
| `potential_structuring` | Binary | Flags transactions between $\$9,000$ and $\$9,999$ designed to evade threshold reporting |

---

## 3. Explainability & Trust in Auditing
Rather than returning an opaque numeric score, the pipeline translates model metrics into clear audit findings:
- *"Exceeds $10,000 regulatory reporting threshold"*
- *"Suspicious amount pattern (possible structuring just below $10K)"*
- *"High statistical divergence from batch mean (Z-Score: +3.12)"*
- *"High-value round denomination"*
This empowers human auditors to review flagged records with actionable context.
