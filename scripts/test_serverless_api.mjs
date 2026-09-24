/**
 * Test Suite: Vercel Serverless Function End-to-End Verification
 * Verifies that api/health.js and api/index.js handle all required endpoints,
 * returning valid HTTP 200 JSON with zero unhandled exceptions or crashes.
 */

import { EventEmitter } from 'events';
import healthHandler from '../api/health.js';
import indexHandler from '../api/index.js';

function createMockReqRes({ url, method = 'GET', body = null, headers = {} }) {
  const req = new EventEmitter();
  req.url = url;
  req.method = method;
  req.headers = { host: 'localhost:3000', ...headers };
  req.body = body;

  let statusCode = 200;
  const resHeaders = {};
  let bodyData = '';

  const resPromise = new Promise((resolve) => {
    const res = {
      get statusCode() { return statusCode; },
      set statusCode(val) { statusCode = val; },
      setHeader(k, v) { resHeaders[k.toLowerCase()] = v; },
      getHeader(k) { return resHeaders[k.toLowerCase()]; },
      end(chunk) {
        if (chunk) bodyData += chunk;
        resolve({
          statusCode,
          headers: resHeaders,
          body: bodyData,
          json: () => {
            try { return JSON.parse(bodyData); } catch (e) { return null; }
          }
        });
      },
      json(data) {
        bodyData = JSON.stringify(data);
        res.setHeader('content-type', 'application/json');
        res.end();
      }
    };

    setTimeout(async () => {
      try {
        if (url === '/api/health' && method === 'GET') {
          await healthHandler(req, res);
        } else {
          await indexHandler(req, res);
        }
      } catch (err) {
        res.statusCode = 500;
        res.end(JSON.stringify({ error: err.message }));
      }
    }, 0);
  });

  return resPromise;
}

async function runTests() {
  console.log('🧪 Starting Vercel Serverless API Test Suite...\n');
  let passed = 0;
  let failed = 0;

  async function assertEndpoint(name, config, validateFn) {
    process.stdout.write(`  • Testing: ${name}... `);
    try {
      const res = await createMockReqRes(config);
      const json = res.json();
      if (res.statusCode >= 400 && (!config.expectError || res.statusCode !== config.expectError)) {
        throw new Error(`HTTP ${res.statusCode}: ${res.body}`);
      }
      if (validateFn) validateFn(res, json);
      console.log(`✅ PASSED (HTTP ${res.statusCode})`);
      passed++;
    } catch (err) {
      console.log(`❌ FAILED: ${err.message}`);
      failed++;
    }
  }

  // 1. Health Checks
  await assertEndpoint('GET /api/health (dedicated)', { url: '/api/health' }, (res, json) => {
    if (json.status !== 'ok' || json.service !== 'auditregistry-api') throw new Error('Invalid health response');
  });

  await assertEndpoint('GET /health (index)', { url: '/health' }, (res, json) => {
    if (json.status !== 'ok') throw new Error('Invalid /health response');
  });

  // 2. Root API Endpoints
  await assertEndpoint('GET / (Root API)', { url: '/' }, (res, json) => {
    if (json.status !== 'online' || json.service !== 'AuditRegistry API') throw new Error('Invalid root response');
  });

  await assertEndpoint('GET /api', { url: '/api' }, (res, json) => {
    if (json.status !== 'online') throw new Error('Invalid /api response');
  });

  // 3. System Diagnostics
  await assertEndpoint('GET /api/system/health', { url: '/api/system/health' }, (res, json) => {
    if (json.status !== 'operational' || !json.subsystems) throw new Error('Invalid system health response');
  });

  await assertEndpoint('GET /api/system/settings', { url: '/api/system/settings' }, (res, json) => {
    if (!json.aml_threshold || !json.contract_address) throw new Error('Invalid settings response');
  });

  await assertEndpoint('GET /api/health/database', { url: '/api/health/database' }, (res, json) => {
    if (!json.engine || json.engine !== 'Supabase PostgreSQL') throw new Error('Invalid database health');
  });

  // 4. Vercel Rewrite Simulation: ?path=system/health
  await assertEndpoint('GET /api/index?path=system/health (Vercel rewrite query)', { url: '/api/index?path=system/health' }, (res, json) => {
    if (json.status !== 'operational') throw new Error('Rewrite ?path= resolution failed');
  });

  // 5. Audit Sessions Lifecycle
  let testSessionId = null;
  await assertEndpoint('POST /api/audit/sessions', {
    url: '/api/audit/sessions',
    method: 'POST',
    body: { projectId: 'treasury-test', sessionName: 'Automated Test Run' }
  }, (res, json) => {
    if (!json.sessionId || json.status !== 'INITIALIZED') throw new Error('Session creation failed');
    testSessionId = json.sessionId;
  });

  await assertEndpoint('GET /api/audit/sessions', { url: '/api/audit/sessions' }, (res, json) => {
    if (!Array.isArray(json)) throw new Error('Sessions should be an array');
  });

  // 6. Transaction Ingestion
  const testTransactions = [
    { transactionRef: "TX-1001", accountNumber: "1010-CASH", amount: 15000.00, type: "DEBIT", category: "Revenue", entryDate: "2026-09-01" },
    { transactionRef: "TX-1002", accountNumber: "4010-SALES", amount: 15000.00, type: "CREDIT", category: "Revenue", entryDate: "2026-09-01" },
    { transactionRef: "TX-1003", accountNumber: "1010-CASH", amount: 9500.00, type: "DEBIT", category: "Wire", entryDate: "2026-09-02" },
    { transactionRef: "TX-1004", accountNumber: "2010-AP", amount: 9500.00, type: "CREDIT", category: "Wire", entryDate: "2026-09-02" },
    { transactionRef: "TX-1005", accountNumber: "1010-CASH", amount: 250.00, type: "DEBIT", category: "Operating", entryDate: "2026-09-03" },
    { transactionRef: "TX-1006", accountNumber: "5010-EXPENSE", amount: 250.00, type: "CREDIT", category: "Operating", entryDate: "2026-09-03" }
  ];

  await assertEndpoint(`POST /api/audit/sessions/${testSessionId}/transactions`, {
    url: `/api/audit/sessions/${testSessionId}/transactions`,
    method: 'POST',
    body: { transactions: testTransactions }
  }, (res, json) => {
    if (json.ingestedCount !== 6 || json.status !== 'SUCCESS') throw new Error('Ingestion count mismatch');
  });

  await assertEndpoint(`GET /api/audit/sessions/${testSessionId}/transactions`, {
    url: `/api/audit/sessions/${testSessionId}/transactions`
  }, (res, json) => {
    if (!Array.isArray(json) || json.length !== 6) throw new Error('Transactions fetch mismatch');
  });

  // 7. Double-Entry Reconciliation
  await assertEndpoint(`POST /api/audit/sessions/${testSessionId}/reconcile`, {
    url: `/api/audit/sessions/${testSessionId}/reconcile`,
    method: 'POST'
  }, (res, json) => {
    if (json.status !== 'BALANCED' || !json.isReconciled || json.totalDebit !== 24750) {
      throw new Error(`Reconciliation mismatch: ${JSON.stringify(json)}`);
    }
  });

  // 8. AI Anomaly Screening
  await assertEndpoint(`POST /api/audit/sessions/${testSessionId}/anomalies`, {
    url: `/api/audit/sessions/${testSessionId}/anomalies`,
    method: 'POST'
  }, (res, json) => {
    if (json.totalAnalyzed !== 6 || json.anomaliesDetected < 2) {
      throw new Error(`Anomaly detection mismatch: detected ${json.anomaliesDetected}`);
    }
  });

  // 9. Benford's Law Analysis
  await assertEndpoint(`POST /api/audit/sessions/${testSessionId}/benford`, {
    url: `/api/audit/sessions/${testSessionId}/benford`,
    method: 'POST'
  }, (res, json) => {
    if (json.sampleSize !== 6 || typeof json.divergenceScore !== 'number') {
      throw new Error(`Benford analysis failed: ${JSON.stringify(json)}`);
    }
  });

  // 10. Cryptographic Canonical Merkle Root
  let calculatedHash = null;
  await assertEndpoint(`POST /api/audit/sessions/${testSessionId}/canonical-hash`, {
    url: `/api/audit/sessions/${testSessionId}/canonical-hash`,
    method: 'POST'
  }, (res, json) => {
    if (!json.canonicalHash || !json.canonicalHash.startsWith('0x') || json.canonicalHash.length !== 66) {
      throw new Error(`Invalid canonical hash: ${json.canonicalHash}`);
    }
    calculatedHash = json.canonicalHash;
  });

  // 11. Blockchain Attestation Recording
  await assertEndpoint('POST /api/blockchain/record', {
    url: '/api/blockchain/record',
    method: 'POST',
    body: {
      sessionId: testSessionId,
      dataHash: calculatedHash,
      transactionHash: '0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef',
      blockNumber: 1234567,
      chainId: '11155111',
      contractAddress: '0xd8b934580fcE35a11B58C6D73aDeE468a2833fa8',
      walletAddress: '0x70997970C51812dc3A010C7d01b50e0d17dc79C8',
      status: 'MINED'
    }
  }, (res, json) => {
    if (json.status !== 'RECORDED' || !json.record) throw new Error('Blockchain record creation failed');
  });

  await assertEndpoint(`GET /api/blockchain/records/${testSessionId}`, {
    url: `/api/blockchain/records/${testSessionId}`
  }, (res, json) => {
    if (!Array.isArray(json) || json.length === 0) throw new Error('Blockchain record fetch failed');
  });

  // 12. Audit Certificate
  await assertEndpoint(`GET /api/audit/sessions/${testSessionId}/certificate`, {
    url: `/api/audit/sessions/${testSessionId}/certificate`
  }, (res, json) => {
    if (!json.certificateNumber || !json.reconciliation?.isReconciled || !json.canonicalHash) {
      throw new Error(`Certificate generation failed: ${JSON.stringify(json)}`);
    }
  });

  // 13. Legacy Evaluate Batch Endpoint
  await assertEndpoint('POST /api/audit/evaluate (legacy batch)', {
    url: '/api/audit/evaluate',
    method: 'POST',
    body: {
      projectId: 'legacy-project',
      transactions: testTransactions
    }
  }, (res, json) => {
    if (json.totalRecords !== 6 || !json.reconciliation.isReconciled || !json.calculatedDeterministicHash) {
      throw new Error('Legacy evaluate failed');
    }
  });

  // 14. CORS Preflight
  await assertEndpoint('OPTIONS /api/health', {
    url: '/api/health',
    method: 'OPTIONS'
  }, (res) => {
    if (res.statusCode !== 200 || !res.headers['access-control-allow-origin']) {
      throw new Error('CORS preflight failed');
    }
  });

  console.log(`\n==================================================`);
  console.log(`📊 Test Results: ${passed} Passed, ${failed} Failed`);
  console.log(`==================================================\n`);

  if (failed > 0) {
    process.exit(1);
  }
}

runTests();
