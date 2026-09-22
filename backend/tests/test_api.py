"""
AuditRegistry - Backend API Automated Test Suite
Tests: Health checks, Session creation, CSV data ingestion, 
       Double-entry reconciliation, AI Anomaly detection, 
       Benford's Law analysis, Canonical hashing, and Audit Certificates.
"""

import os
import sys
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from fastapi.testclient import TestClient
import main

client = TestClient(main.app)

def test_health_endpoints():
    res = client.get("/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "healthy"
    assert data["aiModel"] == "IsolationForest"

def test_database_health():
    res = client.get("/api/health/database")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "healthy"
    assert data["databaseReachable"] is True
    assert data["readTest"] == "PASS"
    assert data["writeTest"] == "PASS"
    assert data["cleanupTest"] == "PASS"

def test_system_settings():
    res = client.get("/api/system/settings")
    assert res.status_code == 200
    data = res.json()
    assert "aml_threshold" in data
    assert "contract_address" in data

def test_full_audit_lifecycle():
    # 1. Create Session
    session_res = client.post("/api/audit/sessions", json={
        "projectId": "test-fintech-protocol",
        "sessionName": "Automated Test Audit Session"
    })
    assert session_res.status_code == 200
    session_data = session_res.json()
    session_id = session_data["sessionId"]
    assert session_id is not None

    # 2. Ingest Balanced Transactions
    tx_payload = [
        {"transactionRef": "TX-TEST-01", "accountNumber": "ACC-100", "amount": 50000.0, "type": "CREDIT", "category": "Sales"},
        {"transactionRef": "TX-TEST-02", "accountNumber": "ACC-200", "amount": 35000.0, "type": "DEBIT", "category": "Payroll"},
        {"transactionRef": "TX-TEST-03", "accountNumber": "ACC-300", "amount": 15000.0, "type": "DEBIT", "category": "Equipment"},
        {"transactionRef": "TX-TEST-04", "accountNumber": "ACC-400", "amount": 9999.0, "type": "DEBIT", "category": "Advisory"}, # Potential structuring
        {"transactionRef": "TX-TEST-05", "accountNumber": "ACC-500", "amount": 9999.0, "type": "CREDIT", "category": "Consulting"}
    ]
    tx_res = client.post(f"/api/audit/sessions/{session_id}/transactions", json=tx_payload)
    assert tx_res.status_code == 200
    assert tx_res.json()["ingestedCount"] == 5

    # 3. Double-Entry Reconciliation
    rec_res = client.post(f"/api/audit/sessions/{session_id}/reconcile")
    assert rec_res.status_code == 200
    rec_data = rec_res.json()
    assert rec_data["totalDebit"] == 59999.0
    assert rec_data["totalCredit"] == 59999.0
    assert rec_data["difference"] == 0.0
    assert rec_data["isReconciled"] is True
    assert rec_data["status"] == "BALANCED"

    # 4. AI Anomaly Detection
    anom_res = client.post(f"/api/audit/sessions/{session_id}/anomalies")
    assert anom_res.status_code == 200
    anom_data = anom_res.json()
    assert anom_data["totalAnalyzed"] == 5
    assert anom_data["anomaliesDetected"] >= 1

    # 5. Benford's Law Analysis
    ben_res = client.post(f"/api/audit/sessions/{session_id}/benford")
    assert ben_res.status_code == 200
    ben_data = ben_res.json()
    assert ben_data["sampleSize"] == 5
    assert "observedDistribution" in ben_data

    # 6. Canonical Hash Computation
    hash_res = client.post(f"/api/audit/sessions/{session_id}/canonical-hash")
    assert hash_res.status_code == 200
    hash_data = hash_res.json()
    assert hash_data["canonicalHash"].startswith("0x")
    assert len(hash_data["canonicalHash"]) == 66

    # 7. Blockchain Receipt Recording
    bc_res = client.post("/api/blockchain/record", json={
        "sessionId": session_id,
        "dataHash": hash_data["canonicalHash"],
        "transactionHash": "0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef",
        "blockNumber": 5600123,
        "chainId": "11155111",
        "contractAddress": "0xd8b934580fcE35a11B58C6D73aDeE468a2833fa8",
        "walletAddress": "0x71C2B9284F0740E7A678e794358a9eD6a195B401",
        "status": "MINED"
    })
    assert bc_res.status_code == 200

    # 8. Certificate Generation
    cert_res = client.get(f"/api/audit/sessions/{session_id}/certificate")
    assert cert_res.status_code == 200
    cert_data = cert_res.json()
    assert cert_data["certificateNumber"].startswith("CERT-")
    assert cert_data["canonicalHash"] == hash_data["canonicalHash"]
    assert cert_data["reconciliation"]["isReconciled"] is True
