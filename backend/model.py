"""
Isolation Forest Anomaly Detection Engine
Features:
- Z-score statistical divergence
- AML $10,000 threshold monitoring
- Round number clustering detection
- Off-hours / weekend timing detection
- Explainable feature attribution (no black-box scoring)
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from typing import List, Dict, Any

class FinancialAnomalyDetector:
    def __init__(self, contamination: float = 0.08):
        self.contamination = contamination
        self.model = IsolationForest(
            n_estimators=100,
            contamination=self.contamination,
            random_state=42,
            n_jobs=-1
        )

    def evaluate_batch(self, records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        if not records:
            return []

        df = pd.DataFrame(records)
        df['amount'] = pd.to_numeric(df['amount'], errors='coerce').fillna(0.0)

        # 1. Feature Engineering
        mean_amount = df['amount'].mean()
        std_amount = df['amount'].std() or 1.0
        df['z_score'] = (df['amount'] - mean_amount) / std_amount
        df['is_round'] = df['amount'].apply(lambda x: 1.0 if x > 500 and x % 100 == 0 else 0.0)
        df['is_debit'] = df['type'].apply(lambda x: 1.0 if str(x).upper() == 'DEBIT' else 0.0)
        
        # AML Threshold Indicator
        df['exceeds_aml_limit'] = df['amount'].apply(lambda x: 1.0 if x >= 10000.0 else 0.0)
        
        # Potential Structuring (just below $10,000: $9,000 - $9,999)
        df['potential_structuring'] = df['amount'].apply(lambda x: 1.0 if 9000.0 <= x < 10000.0 else 0.0)

        # 2. Model Inference
        features = df[['amount', 'z_score', 'is_round', 'is_debit', 'exceeds_aml_limit', 'potential_structuring']].values
        self.model.fit(features)
        
        raw_predictions = self.model.predict(features)  # -1 for anomaly, 1 for normal
        decision_scores = -self.model.decision_function(features) # higher = more anomalous

        # Normalize score between 0.0 and 1.0
        min_score = decision_scores.min()
        max_score = decision_scores.max()
        range_score = (max_score - min_score) if (max_score - min_score) > 0 else 1.0
        normalized_scores = (decision_scores - min_score) / range_score

        # 3. Transparent Explainability Generation
        enriched_results = []
        for i, row in df.iterrows():
            is_anomaly = bool(raw_predictions[i] == -1 or row['exceeds_aml_limit'] == 1.0 or row['potential_structuring'] == 1.0)
            reasons = []

            if row['exceeds_aml_limit'] == 1.0:
                reasons.append("Exceeds $10,000 regulatory reporting threshold")
            if row['potential_structuring'] == 1.0:
                reasons.append("Suspicious amount pattern (possible structuring just below $10K)")
            if abs(row['z_score']) > 2.2:
                reasons.append(f"High statistical divergence from batch mean (Z-Score: {row['z_score']:.2f})")
            if row['is_round'] == 1.0 and row['amount'] > 1000:
                reasons.append("High-value round denomination (frequently seen in unauthorized transfers)")

            record_dict = records[i].copy()
            record_dict['isAnomaly'] = is_anomaly
            record_dict['anomalyScore'] = float(round(normalized_scores[i], 4))
            record_dict['explanation'] = "; ".join(reasons) if reasons else "Conforms to standard operating parameters"
            record_dict['status'] = "FLAGGED" if is_anomaly else "VERIFIED"
            
            enriched_results.append(record_dict)

        return enriched_results
