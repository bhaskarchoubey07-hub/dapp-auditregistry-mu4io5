"""
Audit Registry DApp - Backend & AI Microservice
Framework: FastAPI / Python 3.10+
Functionality: Transaction Ingestion, Double-Entry Reconciliation, 
               Compliance Validation, Isolation Forest Anomaly Detection, 
               Deterministic Hashing for Blockchain Anchoring.
"""

import os
import hashlib
import json
from typing import List, Optional, Dict, Any
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from model import FinancialAnomalyDetector

app = FastAPI(
    title="Automated Financial Audit & Compliance API",
    description="Enterprise REST API for financial auditing, reconciliation, anomaly detection, and blockchain anchoring.",
    version="1.0.0"
)

# CORS Configuration
origins = [
    "http://localhost:5173",
    "http://localhost:3000",
    "https://*.vercel.app",
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize explainable AI anomaly detector
detector = FinancialAnomalyDetector(contamination=0.08)

# ----------------- Data Models -----------------

class TransactionItem(BaseModel):
    transactionRef: str = Field(..., description="Unique transaction ID or reference number")
    accountNumber: str = Field(..., description="Source or destination account number")
    amount: float = Field(..., gt=0, description="Transaction amount in currency units")
    type: str = Field(..., description="DEBIT or CREDIT")
    category: Optional[str] = "General"
    timestamp: Optional[str] = None
    description: Optional[str] = ""

class AuditBatchRequest(BaseModel):
    projectId: str = Field(..., description="Identifier for protocol or organization")
    transactions: List[TransactionItem]

class ReconciliationReport(BaseModel):
    totalInflow: float
    totalOutflow: float
    balanceDifference: float
    isReconciled: bool
    status: str

class AuditEvaluationResponse(BaseModel):
    projectId: str
    totalRecords: int
    totalVolume: float
    reconciliation: ReconciliationReport
    anomaliesFound: int
    calculatedDeterministicHash: str
    transactions: List[Dict[str, Any]]

# ----------------- Endpoints -----------------

@app.get("/health", tags=["System"])
def health_check():
    """Health check endpoint used by Render / Uptime monitors."""
    return {
        "status": "healthy",
        "service": "AuditRegistry-Core-Backend",
        "mlModel": "IsolationForest",
        "version": "1.0.0"
    }

@app.post("/api/audit/evaluate", response_model=AuditEvaluationResponse, tags=["Audit"])
def evaluate_audit_batch(payload: AuditBatchRequest):
    """
    Ingests financial batch transactions, runs double-entry reconciliation, 
    executes AI anomaly detection, and calculates the deterministic canonical hash.
    """
    if not payload.transactions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Transaction batch cannot be empty."
        )

    records = [t.model_dump() for t in payload.transactions]

    # 1. Financial Reconciliation Calculation
    total_debit = sum(r['amount'] for r in records if r['type'].upper() == 'DEBIT')
    total_credit = sum(r['amount'] for r in records if r['type'].upper() == 'CREDIT')
    diff = round(abs(total_debit - total_credit), 2)
    is_balanced = diff < 0.01  # Cent tolerance

    reconciliation = ReconciliationReport(
        totalInflow=round(total_credit, 2),
        totalOutflow=round(total_debit, 2),
        balanceDifference=diff,
        isReconciled=is_balanced,
        status="RECONCILED" if is_balanced else "DISCREPANCY_DETECTED"
    )

    # 2. AI Anomaly Detection Pipeline
    analyzed_records = detector.evaluate_batch(records)
    anomaly_count = sum(1 for r in analyzed_records if r.get('isAnomaly', False))

    # 3. Deterministic Canonical Hash Generation
    # Sort deterministically by transactionRef to ensure mathematical reproducibility
    sorted_records = sorted(records, key=lambda x: x['transactionRef'])
    canonical_payload = {
        "projectId": payload.projectId,
        "recordCount": len(sorted_records),
        "totalDebit": round(total_debit, 2),
        "totalCredit": round(total_credit, 2),
        "records": sorted_records
    }
    canonical_json = json.dumps(canonical_payload, sort_keys=True, separators=(',', ':'))
    # Use Keccak-256 equivalent or SHA-256 digest
    deterministic_hash = "0x" + hashlib.sha256(canonical_json.encode('utf-8')).hexdigest()

    total_volume = round(sum(r['amount'] for r in records), 2)

    return AuditEvaluationResponse(
        projectId=payload.projectId,
        totalRecords=len(records),
        totalVolume=total_volume,
        reconciliation=reconciliation,
        anomaliesFound=anomaly_count,
        calculatedDeterministicHash=deterministic_hash,
        transactions=analyzed_records
    )

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False)
