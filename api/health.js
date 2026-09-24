/**
 * AuditRegistry - Dedicated High-Availability Health Check Handler
 * Vercel Serverless Function: GET /api/health
 */

export default function handler(req, res) {
  // CORS Configuration
  const origin = req.headers.origin || '*';
  res.setHeader('Access-Control-Allow-Origin', origin);
  res.setHeader('Access-Control-Allow-Methods', 'GET, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization, X-Requested-With');
  res.setHeader('Access-Control-Allow-Credentials', 'true');

  if (req.method === 'OPTIONS') {
    res.statusCode = 200;
    return res.end();
  }

  res.statusCode = 200;
  res.setHeader('Content-Type', 'application/json');
  res.end(JSON.stringify({
    status: "ok",
    service: "auditregistry-api",
    environment: process.env.VERCEL_ENV || "production",
    timestamp: new Date().toISOString()
  }));
}
