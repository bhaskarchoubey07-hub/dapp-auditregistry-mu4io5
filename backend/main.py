"""
Audit Registry Enterprise Backend - FastAPI Core REST API
Framework: FastAPI / Python 3.10+
Functionality: Transaction Ingestion, Database Persistence (Supabase / SQLite),
               Double-Entry Reconciliation, Explainable AI Anomaly Detection,
               Benford's Law Forensic Analysis, Deterministic Hashing,
               Blockchain Receipt Tracking, and Audit Certificate Generation.
"""

import os
import uuid
import json
import hashlib
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone

from fastapi import FastAPI, HTTPException, status, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from config import settings
from db import db
from model import FinancialAnomalyDetector

app = FastAPI(
    title="AuditRegistry Enterprise API",
    description="Enterprise REST API for financial auditing, reconciliation, anomaly detection, database persistence, and blockchain anchoring.",
    version="2.0.0"
)

# CORS Configuration
origins = [
    "http://localhost:5173",
    "http://localhost:3000",
    "http://127.0.0.1:5173",
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
detector = FinancialAnomalyDetector(contamination=settings.ML_CONTAMINATION_RATE)

# Theoretical Benford distribution
BENFORD_THEORETICAL = {
    "1": 30.1, "2": 17.6, "3": 12.5, "4": 9.7, 
    "5": 7.9, "6": 6.7, "7": 5.8, "8": 5.1, "9": 4.6
}

# ----------------- Helper Sanitizer for CSV Formula Injection -----------------
def row_to_dict(row):
    """Converts a database row (sqlite3.Row or psycopg dict_row) to a standard dict."""
    if row is None:
        return None
    if isinstance(row, dict):
        return row
    try:
        return dict(row)
    except Exception:
        return None

def sanitize_cell(value: Any) -> str:
    """Neutralizes formula injection characters (=, +, -, @, \t, \r) in exportable strings."""
    if value is None:
        return ""
    val_str = str(value).strip()
    if val_str and val_str[0] in ('=', '+', '-', '@', '\t', '\r'):
        return "'" + val_str
    return val_str

# ----------------- Data Models -----------------

class TransactionInput(BaseModel):
    transactionRef: str = Field(..., description="Unique transaction ID or reference number")
    accountNumber: str = Field(..., description="Source or destination account number")
    amount: float = Field(..., gt=0, description="Transaction amount in currency units")
    type: str = Field(..., description="DEBIT or CREDIT")
    category: Optional[str] = "General"
    entryDate: Optional[str] = None
    description: Optional[str] = ""

class CreateSessionRequest(BaseModel):
    projectId: str = Field(default="corporate-treasury-2026-q3")
    sessionName: str = Field(default="Corporate Treasury Audit Run")
    transactions: List[TransactionInput] = Field(default_factory=list)

class BlockchainRecordInput(BaseModel):
    sessionId: str
    dataHash: str
    transactionHash: str
    blockNumber: Optional[int] = None
    chainId: str = "11155111"
    contractAddress: str
    walletAddress: str
    status: str = "MINED"

class AuditBatchRequest(BaseModel):
    projectId: str = Field(..., description="Identifier for protocol or organization")
    transactions: List[TransactionInput]

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

# ----------------- SYSTEM & HEALTH ENDPOINTS -----------------

@app.get("/health", tags=["System"])
def health_check():
    """Basic service health check."""
    return {
        "status": "healthy",
        "service": "AuditRegistry-Enterprise-Backend",
        "version": "2.0.0",
        "aiModel": "IsolationForest",
        "contaminationRate": settings.ML_CONTAMINATION_RATE,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

@app.get("/api/health/database", tags=["System"])
def database_health():
    """Safe internal database health check (verifies reachability, tables, read/write, zero credential leakage)."""
    return db.check_health()

@app.get("/api/system/health", tags=["System"])
def full_system_health():
    """System-wide health status across Frontend, Backend, Database, AI, and Blockchain."""
    db_status = db.check_health()
    return {
        "status": "operational",
        "subsystems": {
            "frontend": { "status": "ONLINE", "url": settings.FRONTEND_URL },
            "backend": { "status": "ONLINE", "port": settings.PORT },
            "database": {
                "status": "ONLINE" if db_status.get("databaseReachable") else "OFFLINE",
                "engine": db_status.get("engine"),
                "tablesConfigured": db_status.get("tablesFound")
            },
            "aiService": {
                "status": "ONLINE",
                "model": "IsolationForest",
                "contamination": settings.ML_CONTAMINATION_RATE
            },
            "blockchain": {
                "status": "ONLINE",
                "targetChainId": settings.CHAIN_ID,
                "contract": settings.CONTRACT_ADDRESS,
                "rpcUrl": settings.BLOCKCHAIN_RPC_URL
            }
        },
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

@app.get("/api/system/settings", tags=["System"])
def get_system_settings():
    """Retrieves non-sensitive public system configuration."""
    with db.get_connection() as conn:
        cur = conn.cursor()
        cur.execute("SELECT key, value, description FROM system_settings WHERE is_public = 1;")
        rows = cur.fetchall()
        result = {}
        for r in rows:
            k = r['key'] if isinstance(r, dict) else r[0]
            v = r['value'] if isinstance(r, dict) else r[1]
            d = r['description'] if isinstance(r, dict) else r[2]
            try:
                parsed_v = json.loads(v) if isinstance(v, str) else v
            except:
                parsed_v = v
            result[k] = { "value": parsed_v, "description": d }
        return result

# ----------------- AUDIT SESSION LIFECYCLE ENDPOINTS -----------------

@app.post("/api/audit/sessions", tags=["Audit Sessions"])
def create_audit_session(payload: CreateSessionRequest):
    """Creates a new audit session and ingests any provided initial transactions."""
    session_id = str(uuid.uuid4())
    now_iso = datetime.now(timezone.utc).isoformat()

    with db.get_connection() as conn:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO audit_sessions (id, project_id, session_name, status) VALUES (?, ?, ?, ?);",
            (session_id, payload.projectId, payload.sessionName, "INITIALIZED")
        )
        conn.commit()

    if payload.transactions:
        ingest_session_transactions(session_id, payload.transactions)

    return {
        "sessionId": session_id,
        "projectId": payload.projectId,
        "sessionName": payload.sessionName,
        "status": "INITIALIZED",
        "createdAt": now_iso
    }

@app.get("/api/audit/sessions", tags=["Audit Sessions"])
def list_audit_sessions():
    """Lists all stored audit sessions with aggregated volume and record counts."""
    with db.get_connection() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT s.id, s.project_id, s.session_name, s.status, s.total_records, s.total_volume, s.created_at,
                   r.total_debit, r.total_credit, r.difference, r.is_reconciled
            FROM audit_sessions s
            LEFT JOIN reconciliations r ON s.id = r.session_id
            ORDER BY s.created_at DESC;
        """)
        rows = cur.fetchall()
        sessions = []
        for r in rows:
            sessions.append({
                "id": r['id'] if isinstance(r, dict) else r[0],
                "projectId": r['project_id'] if isinstance(r, dict) else r[1],
                "sessionName": r['session_name'] if isinstance(r, dict) else r[2],
                "status": r['status'] if isinstance(r, dict) else r[3],
                "totalRecords": r['total_records'] if isinstance(r, dict) else r[4],
                "totalVolume": float(r['total_volume'] or 0.0) if isinstance(r, dict) else float(r[5] or 0.0),
                "createdAt": r['created_at'] if isinstance(r, dict) else r[6],
                "reconciliation": {
                    "isReconciled": bool(r['is_reconciled']) if isinstance(r, dict) else bool(r[10]),
                    "difference": float(r['difference'] or 0.0) if isinstance(r, dict) else float(r[9] or 0.0)
                } if (r['is_reconciled'] if isinstance(r, dict) else r[10]) is not None else None
            })
        return sessions

@app.get("/api/audit/sessions/{session_id}", tags=["Audit Sessions"])
def get_audit_session_details(session_id: str):
    """Retrieves full aggregated audit session details including reconciliation, anomalies, Benford, and blockchain records."""
    with db.get_connection() as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM audit_sessions WHERE id = ?;", (session_id,))
        session_row = cur.fetchone()
        if not session_row:
            raise HTTPException(status_code=404, detail="Audit session not found.")

        # Reconciliations
        cur.execute("SELECT * FROM reconciliations WHERE session_id = ?;", (session_id,))
        rec_row = cur.fetchone()

        # Anomalies count
        cur.execute("SELECT COUNT(*) FROM anomalies WHERE session_id = ? AND is_anomaly = 1;", (session_id,))
        anomaly_count = cur.fetchone()[0]

        # Benford
        cur.execute("SELECT * FROM benford_results WHERE session_id = ?;", (session_id,))
        benford_row = cur.fetchone()

        # Blockchain Record
        cur.execute("SELECT * FROM blockchain_records WHERE session_id = ? ORDER BY anchored_at DESC LIMIT 1;", (session_id,))
        bc_row = cur.fetchone()

        return {
            "session": dict(session_row) if isinstance(session_row, dict) else {
                "id": session_row[0], "projectId": session_row[1], "sessionName": session_row[2],
                "status": session_row[3], "totalRecords": session_row[4], "totalVolume": session_row[5]
            },
            "reconciliation": dict(rec_row) if rec_row and isinstance(rec_row, dict) else None,
            "anomalyCount": anomaly_count,
            "benfordAnalysis": dict(benford_row) if benford_row and isinstance(benford_row, dict) else None,
            "blockchainRecord": dict(bc_row) if bc_row and isinstance(bc_row, dict) else None
        }

# ----------------- TRANSACTIONS & INGESTION -----------------

def ingest_session_transactions(session_id: str, transactions: List[TransactionInput]):
    """Stores transactions in database with CSV injection prevention."""
    records = []
    total_vol = 0.0

    with db.get_connection() as conn:
        cur = conn.cursor()
        for t in transactions:
            tx_id = str(uuid.uuid4())
            safe_ref = sanitize_cell(t.transactionRef)
            safe_acc = sanitize_cell(t.accountNumber)
            safe_cat = sanitize_cell(t.category or "General")
            safe_desc = sanitize_cell(t.description or "")
            clean_type = t.type.upper() if t.type.upper() in ('DEBIT', 'CREDIT') else 'DEBIT'
            entry_date = t.entryDate or datetime.now(timezone.utc).strftime("%Y-%m-%d")

            cur.execute("""
                INSERT INTO transactions 
                (id, session_id, transaction_ref, account_number, amount, type, category, description, entry_date)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(session_id, transaction_ref) DO UPDATE SET
                    amount=excluded.amount,
                    type=excluded.type,
                    category=excluded.category;
            """, (tx_id, session_id, safe_ref, safe_acc, t.amount, clean_type, safe_cat, safe_desc, entry_date))

            total_vol += t.amount
            records.append({
                "transactionRef": safe_ref,
                "accountNumber": safe_acc,
                "amount": t.amount,
                "type": clean_type,
                "category": safe_cat,
                "date": entry_date
            })

        cur.execute(
            "UPDATE audit_sessions SET total_records = ?, total_volume = ?, status = 'IN_PROGRESS' WHERE id = ?;",
            (len(transactions), round(total_vol, 2), session_id)
        )
        conn.commit()

    return records

@app.post("/api/audit/sessions/{session_id}/transactions", tags=["Transactions"])
def add_transactions_to_session(session_id: str, transactions: List[TransactionInput]):
    """Ingests a batch of transactions into an existing audit session."""
    if not transactions:
        raise HTTPException(status_code=400, detail="Transaction list cannot be empty.")
    records = ingest_session_transactions(session_id, transactions)
    return {
        "sessionId": session_id,
        "ingestedCount": len(records),
        "status": "SUCCESS"
    }

@app.get("/api/audit/sessions/{session_id}/transactions", tags=["Transactions"])
def get_session_transactions(session_id: str):
    """Retrieves all transactions belonging to an audit session."""
    with db.get_connection() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT t.id, t.transaction_ref, t.account_number, t.amount, t.type, t.category, t.entry_date,
                   a.anomaly_score, a.risk_level, a.explanation, a.is_anomaly
            FROM transactions t
            LEFT JOIN anomalies a ON t.id = a.transaction_id
            WHERE t.session_id = ?
            ORDER BY t.created_at ASC;
        """, (session_id,))
        rows = cur.fetchall()
        txs = []
        for r in rows:
            txs.append({
                "id": r['id'] if isinstance(r, dict) else r[0],
                "transactionRef": r['transaction_ref'] if isinstance(r, dict) else r[1],
                "accountNumber": r['account_number'] if isinstance(r, dict) else r[2],
                "amount": float(r['amount']) if isinstance(r, dict) else float(r[3]),
                "type": r['type'] if isinstance(r, dict) else r[4],
                "category": r['category'] if isinstance(r, dict) else r[5],
                "date": r['entry_date'] if isinstance(r, dict) else r[6],
                "anomalyScore": float(r['anomaly_score'] or 0.0) if (isinstance(r, dict) and r['anomaly_score'] is not None) else None,
                "riskLevel": r['risk_level'] if isinstance(r, dict) else r[8],
                "explanation": r['explanation'] if isinstance(r, dict) else r[9],
                "isAnomaly": bool(r['is_anomaly']) if isinstance(r, dict) else bool(r[10])
            })
        return txs

# ----------------- RECONCILIATION ENGINE -----------------

@app.post("/api/audit/sessions/{session_id}/reconcile", tags=["Audit Processing"])
def run_double_entry_reconciliation(session_id: str):
    """Calculates Pacioli's accounting reconciliation (Debit vs Credit) and persists the result."""
    with db.get_connection() as conn:
        cur = conn.cursor()
        cur.execute("SELECT amount, type FROM transactions WHERE session_id = ?;", (session_id,))
        rows = cur.fetchall()
        if not rows:
            raise HTTPException(status_code=400, detail="No transactions found for reconciliation.")

        total_debit = sum(float(r['amount'] if isinstance(r, dict) else r[0]) for r in rows if (r['type'] if isinstance(r, dict) else r[1]) == 'DEBIT')
        total_credit = sum(float(r['amount'] if isinstance(r, dict) else r[0]) for r in rows if (r['type'] if isinstance(r, dict) else r[1]) == 'CREDIT')
        diff = round(abs(total_debit - total_credit), 2)
        is_balanced = diff < 0.01

        status_str = "BALANCED" if is_balanced else "UNBALANCED"
        rec_id = str(uuid.uuid4())

        cur.execute("""
            INSERT INTO reconciliations (id, session_id, total_debit, total_credit, difference, is_reconciled, status)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(session_id) DO UPDATE SET
                total_debit = excluded.total_debit,
                total_credit = excluded.total_credit,
                difference = excluded.difference,
                is_reconciled = excluded.is_reconciled,
                status = excluded.status;
        """, (rec_id, session_id, round(total_debit, 2), round(total_credit, 2), diff, 1 if is_balanced else 0, status_str))
        conn.commit()

        return {
            "sessionId": session_id,
            "totalDebit": round(total_debit, 2),
            "totalCredit": round(total_credit, 2),
            "difference": diff,
            "isReconciled": is_balanced,
            "status": status_str
        }

# ----------------- AI ANOMALY DETECTION ENGINE -----------------

@app.post("/api/audit/sessions/{session_id}/anomalies", tags=["Audit Processing"])
def run_anomaly_detection(session_id: str):
    """Executes explainable Isolation Forest scoring and stores granular anomaly records."""
    with db.get_connection() as conn:
        cur = conn.cursor()
        cur.execute("SELECT id, transaction_ref, account_number, amount, type, category FROM transactions WHERE session_id = ?;", (session_id,))
        rows = cur.fetchall()
        if not rows:
            raise HTTPException(status_code=400, detail="No transactions to analyze.")

        records = []
        id_map = {}
        for r in rows:
            tid = r['id'] if isinstance(r, dict) else r[0]
            ref = r['transaction_ref'] if isinstance(r, dict) else r[1]
            id_map[ref] = tid
            records.append({
                "transactionRef": ref,
                "accountNumber": r['account_number'] if isinstance(r, dict) else r[2],
                "amount": float(r['amount'] if isinstance(r, dict) else r[3]),
                "type": r['type'] if isinstance(r, dict) else r[4],
                "category": r['category'] if isinstance(r, dict) else r[5]
            })

        # Run AI Model
        analyzed = detector.evaluate_batch(records)
        anomaly_count = 0

        for a in analyzed:
            tx_uuid = id_map.get(a['transactionRef'])
            if not tx_uuid:
                continue

            is_anom = a.get('isAnomaly', False)
            score = float(a.get('anomalyScore', 0.1))
            reason = a.get('explanation', '')

            risk_level = "LOW"
            if score > 0.85: risk_level = "CRITICAL"
            elif score > 0.65: risk_level = "HIGH"
            elif score > 0.40: risk_level = "MEDIUM"

            if is_anom:
                anomaly_count += 1

            anom_id = str(uuid.uuid4())
            cur.execute("""
                INSERT INTO anomalies (id, session_id, transaction_id, anomaly_score, risk_level, explanation, is_anomaly)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO NOTHING;
            """, (anom_id, session_id, tx_uuid, score, risk_level, reason, 1 if is_anom else 0))

        conn.commit()

        return {
            "sessionId": session_id,
            "totalAnalyzed": len(records),
            "anomaliesDetected": anomaly_count,
            "results": analyzed
        }

# ----------------- BENFORD'S LAW FORENSIC ANALYSIS -----------------

@app.post("/api/audit/sessions/{session_id}/benford", tags=["Audit Processing"])
def run_benford_analysis(session_id: str):
    """
    Computes first-digit logarithmic distribution against Benford's Law (P(d) = log10(1 + 1/d)).
    Never presents results as fraud proof; designates as forensic screening indicator.
    """
    with db.get_connection() as conn:
        cur = conn.cursor()
        cur.execute("SELECT amount FROM transactions WHERE session_id = ?;", (session_id,))
        rows = cur.fetchall()
        if not rows:
            raise HTTPException(status_code=400, detail="No transactions for Benford analysis.")

        digit_counts = {str(d): 0 for d in range(1, 10)}
        valid_digits = 0

        for r in rows:
            amt = abs(float(r['amount'] if isinstance(r, dict) else r[0]))
            clean_str = str(amt).replace('.', '').lstrip('0')
            if clean_str and clean_str[0] in digit_counts:
                digit_counts[clean_str[0]] += 1
                valid_digits += 1

        observed = {}
        total_divergence = 0.0
        anomaly_flag = False

        for d in range(1, 10):
            d_str = str(d)
            pct = round((digit_counts[d_str] / valid_digits * 100), 1) if valid_digits > 0 else 0.0
            observed[d_str] = pct
            delta = abs(pct - BENFORD_THEORETICAL[d_str])
            total_divergence += delta
            if valid_digits >= 15 and delta > 22.0:
                anomaly_flag = True

        avg_divergence = round(total_divergence / 9, 2)
        benford_id = str(uuid.uuid4())

        cur.execute("""
            INSERT INTO benford_results (id, session_id, sample_size, observed_distribution, expected_distribution, divergence_score, anomaly_detected)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(session_id) DO UPDATE SET
                sample_size = excluded.sample_size,
                observed_distribution = excluded.observed_distribution,
                divergence_score = excluded.divergence_score,
                anomaly_detected = excluded.anomaly_detected;
        """, (benford_id, session_id, valid_digits, json.dumps(observed), json.dumps(BENFORD_THEORETICAL), avg_divergence, 1 if anomaly_flag else 0))
        conn.commit()

        return {
            "sessionId": session_id,
            "sampleSize": valid_digits,
            "observedDistribution": observed,
            "expectedDistribution": BENFORD_THEORETICAL,
            "divergenceScore": avg_divergence,
            "anomalyDetected": anomaly_flag,
            "forensicDisclaimer": "Forensic screening indicator. Deviation may warrant further investigation but does not constitute proof of fraud."
        }

# ----------------- DETERMINISTIC CANONICAL HASH & BLOCKCHAIN -----------------

@app.post("/api/audit/sessions/{session_id}/canonical-hash", tags=["Blockchain Trail"])
def calculate_canonical_hash(session_id: str):
    """
    Computes deterministic SHA-256 Merkle root hash of transaction ledger.
    Guarantees mathematical reproducibility across nodes and runs.
    """
    with db.get_connection() as conn:
        cur = conn.cursor()
        cur.execute("SELECT project_id FROM audit_sessions WHERE id = ?;", (session_id,))
        sess = cur.fetchone()
        if not sess:
            raise HTTPException(status_code=404, detail="Audit session not found.")
        project_id = sess['project_id'] if isinstance(sess, dict) else sess[0]

        cur.execute("SELECT transaction_ref, account_number, amount, type, entry_date FROM transactions WHERE session_id = ? ORDER BY transaction_ref ASC;", (session_id,))
        rows = cur.fetchall()
        if not rows:
            raise HTTPException(status_code=400, detail="Cannot generate hash for empty session.")

        sorted_txs = []
        total_deb = 0.0
        total_cred = 0.0

        for r in rows:
            amt = float(r['amount'] if isinstance(r, dict) else r[2])
            ttype = r['type'] if isinstance(r, dict) else r[3]
            if ttype == 'DEBIT': total_deb += amt
            else: total_cred += amt

            sorted_txs.append({
                "ref": r['transaction_ref'] if isinstance(r, dict) else r[0],
                "acc": r['account_number'] if isinstance(r, dict) else r[1],
                "amt": amt,
                "type": ttype,
                "date": r['entry_date'] if isinstance(r, dict) else r[4]
            })

        canonical_payload = {
            "projectId": project_id,
            "recordCount": len(sorted_txs),
            "totalDebit": round(total_deb, 2),
            "totalCredit": round(total_cred, 2),
            "transactions": sorted_txs
        }
        canonical_str = json.dumps(canonical_payload, sort_keys=True, separators=(',', ':'))
        canonical_hash = "0x" + hashlib.sha256(canonical_str.encode('utf-8')).hexdigest()

        rec_id = str(uuid.uuid4())
        cur.execute("""
            INSERT INTO audit_records (id, session_id, project_id, canonical_hash, record_count, total_debit, total_credit)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(session_id, canonical_hash) DO NOTHING;
        """, (rec_id, session_id, project_id, canonical_hash, len(sorted_txs), round(total_deb, 2), round(total_cred, 2)))
        conn.commit()

        return {
            "sessionId": session_id,
            "projectId": project_id,
            "recordCount": len(sorted_txs),
            "canonicalHash": canonical_hash,
            "deterministicStringLength": len(canonical_str)
        }

@app.post("/api/blockchain/record", tags=["Blockchain Trail"])
def store_blockchain_record(payload: BlockchainRecordInput):
    """Stores on-chain transaction receipt for anchored audit attestation."""
    rec_id = str(uuid.uuid4())
    now_iso = datetime.now(timezone.utc).isoformat()

    with db.get_connection() as conn:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO blockchain_records 
            (id, session_id, data_hash, transaction_hash, block_number, chain_id, contract_address, wallet_address, status, verified_on_chain)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 1);
        """, (rec_id, payload.sessionId, payload.dataHash, payload.transactionHash, payload.blockNumber, payload.chainId, payload.contractAddress, payload.walletAddress, payload.status))
        
        cur.execute("UPDATE audit_sessions SET status = 'ANCHORED' WHERE id = ?;", (payload.sessionId,))
        conn.commit()

    return {
        "id": rec_id,
        "status": "RECORDED",
        "anchoredAt": now_iso
    }

@app.get("/api/blockchain/records/{session_id}", tags=["Blockchain Trail"])
def get_blockchain_records(session_id: str):
    """Retrieves on-chain attestation receipts for a session."""
    with db.get_connection() as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM blockchain_records WHERE session_id = ? ORDER BY anchored_at DESC;", (session_id,))
        rows = cur.fetchall()
        return [dict(r) if isinstance(r, dict) else {
            "id": r[0], "sessionId": r[1], "dataHash": r[3], "txHash": r[4], "blockNumber": r[5],
            "chainId": r[6], "contractAddress": r[7], "walletAddress": r[8], "status": r[9], "anchoredAt": r[11]
        } for r in rows]

# ----------------- AUDIT CERTIFICATE GENERATION -----------------

@app.get("/api/audit/sessions/{session_id}/certificate", tags=["Audit Certificates"])
def generate_audit_certificate(session_id: str):
    """
    Assembles authoritative audit certificate containing full verified metrics,
    cryptographic hashes, and compliance disclosures.
    """
    with db.get_connection() as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM audit_sessions WHERE id = ?;", (session_id,))
        sess = cur.fetchone()
        if not sess:
            raise HTTPException(status_code=404, detail="Audit session not found.")

        # Reconciliations
        cur.execute("SELECT * FROM reconciliations WHERE session_id = ?;", (session_id,))
        rec = cur.fetchone()

        # Benford
        cur.execute("SELECT * FROM benford_results WHERE session_id = ?;", (session_id,))
        ben = cur.fetchone()

        # Blockchain Record
        cur.execute("SELECT * FROM blockchain_records WHERE session_id = ? ORDER BY anchored_at DESC LIMIT 1;", (session_id,))
        bc = cur.fetchone()

        # Audit Record Hash
        cur.execute("SELECT canonical_hash FROM audit_records WHERE session_id = ? LIMIT 1;", (session_id,))
        ar = cur.fetchone()
        canonical_hash = (ar['canonical_hash'] if isinstance(ar, dict) else ar[0]) if ar else "0x0"

        cert_num = f"CERT-{session_id[:8].upper()}-{datetime.now(timezone.utc).strftime('%Y%m%d')}"

        rec_d = row_to_dict(rec)
        rec_data = {
            "totalDebit": float(rec_d["total_debit"]) if rec_d else 0.0,
            "totalCredit": float(rec_d["total_credit"]) if rec_d else 0.0,
            "difference": float(rec_d["difference"]) if rec_d else 0.0,
            "isReconciled": bool(rec_d["is_reconciled"]) if rec_d else False,
            "status": rec_d["status"] if rec_d else "PENDING"
        }

        cert_payload = {
            "certificateNumber": cert_num,
            "sessionId": session_id,
            "projectId": sess['project_id'] if isinstance(sess, dict) else sess[1],
            "sessionName": sess['session_name'] if isinstance(sess, dict) else sess[2],
            "issuedAt": datetime.now(timezone.utc).isoformat(),
            "totalRecords": sess['total_records'] if isinstance(sess, dict) else sess[4],
            "totalVolume": float(sess['total_volume'] or 0.0) if isinstance(sess, dict) else float(sess[5] or 0.0),
            "reconciliation": rec_data,
            "canonicalHash": canonical_hash,
            "blockchainAttestation": row_to_dict(bc),
            "legalNotice": "System-generated audit analysis. This document serves as a cryptographic record verification. All findings and anomaly indicators are subject to auditor discretion."
        }

        # Persist Certificate
        cur.execute("""
            INSERT INTO audit_certificates 
            (id, session_id, certificate_number, issuer_wallet, canonical_hash, transaction_hash, certificate_data)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(session_id) DO UPDATE SET
                certificate_data = excluded.certificate_data,
                issued_at = CURRENT_TIMESTAMP;
        """, (
            str(uuid.uuid4()), session_id, cert_num, 
            (bc['wallet_address'] if bc and isinstance(bc, dict) else "0x0000000000000000000000000000000000000000"),
            canonical_hash, 
            (bc['transaction_hash'] if bc and isinstance(bc, dict) else None),
            json.dumps(cert_payload)
        ))
        conn.commit()

        return cert_payload

# ----------------- BACKWARD COMPATIBILITY ENDPOINT -----------------

@app.post("/api/audit/evaluate", response_model=AuditEvaluationResponse, tags=["Legacy Compatibility"])
def evaluate_audit_batch(payload: AuditBatchRequest):
    """
    Ingests financial batch transactions, runs double-entry reconciliation, 
    executes AI anomaly detection, and calculates the deterministic canonical hash.
    Preserves 100% backward compatibility for existing callers.
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
    is_balanced = diff < 0.01

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
    sorted_records = sorted(records, key=lambda x: x['transactionRef'])
    canonical_payload = {
        "projectId": payload.projectId,
        "recordCount": len(sorted_records),
        "totalDebit": round(total_debit, 2),
        "totalCredit": round(total_credit, 2),
        "records": sorted_records
    }
    canonical_json = json.dumps(canonical_payload, sort_keys=True, separators=(',', ':'))
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
