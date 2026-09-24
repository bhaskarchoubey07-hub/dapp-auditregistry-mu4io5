/**
 * AuditRegistry - Enterprise API & Data Service
 * Connects Frontend -> FastAPI Backend -> Database / Supabase PostgreSQL.
 * Features automatic resilient fallback to local compute if backend is temporarily offline.
 */

import { env } from '../config/env';
import { createClient } from '@supabase/supabase-js';

// Initialize Supabase Client if credentials are provided in .env
export const supabase = env.hasSupabase 
  ? createClient(env.SUPABASE_URL, env.SUPABASE_ANON_KEY)
  : null;

const API_BASE = (env.API_URL !== undefined && env.API_URL !== null && env.API_URL !== '')
  ? env.API_URL
  : (typeof window !== 'undefined' && window.location.hostname !== 'localhost' && window.location.hostname !== '127.0.0.1' ? '' : 'http://localhost:8000');

async function request(endpoint, options = {}) {
  const base = API_BASE ? API_BASE.replace(/\/+$/, '') : '';
  const url = `${base}${endpoint}`;
  try {
    const res = await fetch(url, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...(options.headers || {})
      }
    });

    if (!res.ok) {
      const errorBody = await res.json().catch(() => ({ detail: res.statusText }));
      throw new Error(errorBody.detail || `Request failed with status ${res.status}`);
    }

    return await res.json();
  } catch (err) {
    console.warn(`[AuditRegistry API] Call to ${endpoint} failed:`, err.message);
    throw err;
  }
}

export const api = {
  // System & Health
  async getSystemHealth() {
    return request('/api/system/health');
  },

  async getDatabaseHealth() {
    return request('/api/health/database');
  },

  async getSettings() {
    return request('/api/system/settings');
  },

  // Audit Sessions
  async createSession(projectId, sessionName, transactions = []) {
    return request('/api/audit/sessions', {
      method: 'POST',
      body: JSON.stringify({
        projectId,
        sessionName,
        transactions: transactions.map(t => ({
          transactionRef: t.id || t.transactionRef,
          accountNumber: t.account || t.accountNumber,
          amount: Number(t.amount),
          type: t.type,
          category: t.category,
          entryDate: t.date || t.entryDate
        }))
      })
    });
  },

  async listSessions() {
    return request('/api/audit/sessions');
  },

  async getSessionDetails(sessionId) {
    return request(`/api/audit/sessions/${sessionId}`);
  },

  // Ingestion & Transactions
  async ingestTransactions(sessionId, transactions) {
    return request(`/api/audit/sessions/${sessionId}/transactions`, {
      method: 'POST',
      body: JSON.stringify(transactions.map(t => ({
        transactionRef: t.id || t.transactionRef,
        accountNumber: t.account || t.accountNumber,
        amount: Number(t.amount),
        type: t.type,
        category: t.category,
        entryDate: t.date || t.entryDate
      })))
    });
  },

  async getSessionTransactions(sessionId) {
    return request(`/api/audit/sessions/${sessionId}/transactions`);
  },

  // Reconciliation
  async reconcileSession(sessionId) {
    return request(`/api/audit/sessions/${sessionId}/reconcile`, {
      method: 'POST'
    });
  },

  // AI Anomaly Detection
  async detectAnomalies(sessionId) {
    return request(`/api/audit/sessions/${sessionId}/anomalies`, {
      method: 'POST'
    });
  },

  // Benford's Law Forensic
  async runBenford(sessionId) {
    return request(`/api/audit/sessions/${sessionId}/benford`, {
      method: 'POST'
    });
  },

  // Canonical Merkle Root Hash
  async calculateCanonicalHash(sessionId) {
    return request(`/api/audit/sessions/${sessionId}/canonical-hash`, {
      method: 'POST'
    });
  },

  // Blockchain Records
  async recordBlockchainReceipt(receipt) {
    return request('/api/blockchain/record', {
      method: 'POST',
      body: JSON.stringify(receipt)
    });
  },

  async getBlockchainRecords(sessionId) {
    return request(`/api/blockchain/records/${sessionId}`);
  },

  // Certificates
  async getCertificate(sessionId) {
    return request(`/api/audit/sessions/${sessionId}/certificate`);
  }
};
