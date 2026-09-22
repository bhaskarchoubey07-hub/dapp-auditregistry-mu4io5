# Free-Tier Service Constraints & Risks

---

## 1. Render Free Tier
- **Inactivity Sleep:** Services spin down after 15 minutes of idle time.
- **Cold-Start Wakeup:** Takes 50 to 90 seconds for the first HTTP request.
- **Monthly Usage Allowance:** 750 free instance hours shared across all web services on the account.

## 2. Neon Serverless Postgres
- **Compute Suspension:** Suspends compute endpoints after 5 minutes of inactivity (resumes in ~500ms).
- **Storage Limit:** 0.5 GB maximum table storage.
- **Connection Limits:** Always use the pooled connection string on port `6543`.

## 3. Vercel Hobby Tier
- **Bandwidth:** 100 GB per month.
- **Function Execution:** Maximum 10-second timeout on serverless functions.
- **Client Bundling:** Only public environment variables prefixed with `VITE_` are exposed in browser bundles.

## 4. Sepolia Testnet
- **Faucet Rate Limits:** Faucets throttle requests to 0.5 - 1.0 test ETH per day.
- **RPC Availability:** Public RPC nodes (`rpc.sepolia.org`) can intermittently experience rate-limiting; use dedicated free API keys from Infura or Alchemy in production.
