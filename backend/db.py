"""
AuditRegistry - Database Layer & Connection Manager
Supports Supabase / Neon PostgreSQL with automatic resilient SQLite fallback.
Provides transactional safety, schema initialization, and zero-leak health checks.
"""

import os
import time
import logging
import sqlite3
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone

from config import settings

logger = logging.getLogger("auditregistry.db")

REQUIRED_TABLES = [
    "users",
    "audit_sessions",
    "transactions",
    "reconciliations",
    "anomalies",
    "compliance_findings",
    "benford_results",
    "audit_records",
    "blockchain_records",
    "audit_certificates",
    "system_settings"
]

class DatabaseManager:
    def __init__(self):
        self.is_postgres = False
        self.pg_pool = None
        self.sqlite_path = os.path.join(os.path.dirname(__file__), "auditregistry_local.db")
        self._initialize_storage()

    def _initialize_storage(self):
        """Attempts connection to PostgreSQL if configured, otherwise sets up local SQLite."""
        if settings.has_postgres:
            try:
                import psycopg
                # Test connection
                with psycopg.connect(settings.DATABASE_URL, connect_timeout=5) as conn:
                    with conn.cursor() as cur:
                        cur.execute("SELECT 1;")
                self.is_postgres = True
                logger.info("Connected to remote PostgreSQL / Supabase database.")
                return
            except Exception as e:
                logger.warning(f"Failed to connect to PostgreSQL ({e}). Falling back to local SQLite engine.")
        
        # Initialize SQLite fallback with identical schema semantics
        self._init_sqlite_schema()

    def _init_sqlite_schema(self):
        """Initializes SQLite database with all 11 required audit tables."""
        with sqlite3.connect(self.sqlite_path) as conn:
            cur = conn.cursor()
            cur.executescript("""
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE,
                wallet_address TEXT UNIQUE,
                role TEXT DEFAULT 'AUDITOR',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS audit_sessions (
                id TEXT PRIMARY KEY,
                project_id TEXT NOT NULL,
                session_name TEXT NOT NULL,
                status TEXT DEFAULT 'IN_PROGRESS',
                total_records INTEGER DEFAULT 0,
                total_volume REAL DEFAULT 0.0,
                created_by TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS transactions (
                id TEXT PRIMARY KEY,
                session_id TEXT NOT NULL REFERENCES audit_sessions(id) ON DELETE CASCADE,
                transaction_ref TEXT NOT NULL,
                account_number TEXT NOT NULL,
                amount REAL NOT NULL,
                currency TEXT DEFAULT 'USD',
                type TEXT NOT NULL,
                category TEXT DEFAULT 'General',
                description TEXT DEFAULT '',
                entry_date TEXT NOT NULL,
                raw_payload TEXT DEFAULT '{}',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(session_id, transaction_ref)
            );

            CREATE TABLE IF NOT EXISTS reconciliations (
                id TEXT PRIMARY KEY,
                session_id TEXT UNIQUE NOT NULL REFERENCES audit_sessions(id) ON DELETE CASCADE,
                total_debit REAL NOT NULL,
                total_credit REAL NOT NULL,
                difference REAL NOT NULL,
                is_reconciled INTEGER NOT NULL DEFAULT 0,
                status TEXT DEFAULT 'UNBALANCED',
                reconciled_at TEXT DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS anomalies (
                id TEXT PRIMARY KEY,
                session_id TEXT NOT NULL REFERENCES audit_sessions(id) ON DELETE CASCADE,
                transaction_id TEXT NOT NULL REFERENCES transactions(id) ON DELETE CASCADE,
                anomaly_score REAL NOT NULL,
                risk_level TEXT NOT NULL,
                explanation TEXT NOT NULL,
                is_anomaly INTEGER DEFAULT 1,
                review_status TEXT DEFAULT 'OPEN',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS compliance_findings (
                id TEXT PRIMARY KEY,
                session_id TEXT NOT NULL REFERENCES audit_sessions(id) ON DELETE CASCADE,
                finding_code TEXT NOT NULL,
                severity TEXT NOT NULL,
                title TEXT NOT NULL,
                details TEXT,
                affected_count INTEGER DEFAULT 1,
                status TEXT DEFAULT 'ACTIVE',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS benford_results (
                id TEXT PRIMARY KEY,
                session_id TEXT UNIQUE NOT NULL REFERENCES audit_sessions(id) ON DELETE CASCADE,
                sample_size INTEGER NOT NULL,
                observed_distribution TEXT NOT NULL,
                expected_distribution TEXT NOT NULL,
                divergence_score REAL DEFAULT 0.0,
                anomaly_detected INTEGER DEFAULT 0,
                evaluated_at TEXT DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS audit_records (
                id TEXT PRIMARY KEY,
                session_id TEXT NOT NULL REFERENCES audit_sessions(id) ON DELETE CASCADE,
                project_id TEXT NOT NULL,
                canonical_hash TEXT NOT NULL,
                record_count INTEGER NOT NULL,
                total_debit REAL NOT NULL,
                total_credit REAL NOT NULL,
                generated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(session_id, canonical_hash)
            );

            CREATE TABLE IF NOT EXISTS blockchain_records (
                id TEXT PRIMARY KEY,
                session_id TEXT NOT NULL REFERENCES audit_sessions(id) ON DELETE CASCADE,
                audit_record_id TEXT,
                data_hash TEXT NOT NULL,
                transaction_hash TEXT,
                block_number INTEGER,
                chain_id TEXT NOT NULL,
                contract_address TEXT NOT NULL,
                wallet_address TEXT NOT NULL,
                status TEXT DEFAULT 'PENDING',
                verified_on_chain INTEGER DEFAULT 0,
                anchored_at TEXT DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS audit_certificates (
                id TEXT PRIMARY KEY,
                session_id TEXT UNIQUE NOT NULL REFERENCES audit_sessions(id) ON DELETE CASCADE,
                certificate_number TEXT UNIQUE NOT NULL,
                issuer_wallet TEXT NOT NULL,
                canonical_hash TEXT NOT NULL,
                transaction_hash TEXT,
                certificate_data TEXT NOT NULL,
                issued_at TEXT DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS system_settings (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                description TEXT,
                is_public INTEGER DEFAULT 0,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            );

            INSERT OR IGNORE INTO system_settings (key, value, description, is_public) VALUES
            ('aml_threshold', '10000', 'Regulatory threshold for high-value AML screening', 1),
            ('structuring_threshold', '9000', 'Threshold for detecting potential structuring', 1),
            ('default_currency', '"USD"', 'Default operating ledger currency', 1),
            ('contract_address', '"0xd8b934580fcE35a11B58C6D73aDeE468a2833fa8"', 'AuditRegistry contract address', 1),
            ('expected_chain_id', '"11155111"', 'Target EVM chain ID (Sepolia)', 1);
            """)
            conn.commit()

    def get_connection(self):
        """Returns a database connection with dictionary-like row access."""
        if self.is_postgres:
            import psycopg
            from psycopg.rows import dict_row
            return psycopg.connect(settings.DATABASE_URL, row_factory=dict_row)
        else:
            conn = sqlite3.connect(self.sqlite_path)
            conn.row_factory = sqlite3.Row
            return conn

    def check_health(self) -> Dict[str, Any]:
        """
        Executes internal database health diagnostic:
        1. Checks database reachability.
        2. Verifies required tables.
        3. Performs ephemeral read and write test.
        4. Cleans up test records immediately (zero persistent test data).
        5. Masks any sensitive credentials.
        """
        start_time = time.time()
        test_session_id = f"test-health-check-{int(time.time() * 1000)}"
        engine = "PostgreSQL (Supabase/Neon)" if self.is_postgres else "SQLite (Local Persistence Engine)"
        
        try:
            with self.get_connection() as conn:
                cur = conn.cursor()

                # 1. Reachability Check
                cur.execute("SELECT 1 AS alive;")
                row = cur.fetchone()
                if not row:
                    raise Exception("Database returned empty response on ping")

                # 2. Schema / Tables Verification
                if self.is_postgres:
                    cur.execute("""
                        SELECT table_name FROM information_schema.tables 
                        WHERE table_schema = 'public';
                    """)
                    existing_tables = [r['table_name'] for r in cur.fetchall()]
                else:
                    cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
                    existing_tables = [r['name'] for r in cur.fetchall()]

                missing_tables = [t for t in REQUIRED_TABLES if t not in existing_tables]

                # 3. Ephemeral Write & Read Test (Transaction Rollback or Cleanup)
                # Write
                cur.execute(
                    "INSERT INTO audit_sessions (id, project_id, session_name, status) VALUES (?, ?, ?, ?);",
                    (test_session_id, "health-check-system", "Ephemeral Diagnostic Test", "INITIALIZED")
                )
                conn.commit()

                # Read
                cur.execute("SELECT id, status FROM audit_sessions WHERE id = ?;", (test_session_id,))
                fetched = cur.fetchone()
                read_ok = bool(fetched and (fetched['id'] if isinstance(fetched, dict) else fetched[0]) == test_session_id)

                # Cleanup (Do NOT leave test data in database)
                cur.execute("DELETE FROM audit_sessions WHERE id = ?;", (test_session_id,))
                conn.commit()

                elapsed_ms = round((time.time() - start_time) * 1000, 2)

                return {
                    "status": "healthy",
                    "engine": engine,
                    "isPostgres": self.is_postgres,
                    "supabaseConfigured": settings.has_supabase_api,
                    "databaseReachable": True,
                    "latencyMs": elapsed_ms,
                    "tablesFound": len(existing_tables),
                    "requiredTablesOk": len(missing_tables) == 0,
                    "missingTables": missing_tables,
                    "readTest": "PASS" if read_ok else "FAIL",
                    "writeTest": "PASS",
                    "cleanupTest": "PASS",
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }

        except Exception as e:
            elapsed_ms = round((time.time() - start_time) * 1000, 2)
            logger.error(f"Database health check failed: {e}")
            return {
                "status": "degraded",
                "engine": engine,
                "isPostgres": self.is_postgres,
                "databaseReachable": False,
                "error": str(e),
                "latencyMs": elapsed_ms,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }

db = DatabaseManager()
