# Free-Tier Cloud Deployment Guide

**Architecture:** Vercel (Frontend) + Render (FastAPI Backend) + Neon (PostgreSQL) + Ethereum Sepolia (Blockchain)  

---

## 1. Frontend Deployment (Vercel)
1. Push this repository to GitHub.
2. In Vercel, select **Add New Project** and import the repository.
3. Keep default settings:
   - Framework Preset: **Vite**
   - Build Command: `npm run build`
   - Output Directory: `dist`
4. Add Environment Variables in Project Settings:
   - `VITE_CONTRACT_ADDRESS`: Deployed AuditRegistry address on Sepolia
   - `VITE_EXPECTED_CHAIN_ID`: `11155111`
5. Click **Deploy**.

---

## 2. Backend Deployment (Render)
1. In Render, select **New Web Service** and link your GitHub repository.
2. Configure runtime parameters:
   - Root Directory: `backend`
   - Environment: `Python 3`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
3. Add Environment Variables:
   - `DATABASE_URL`: Your Neon PostgreSQL connection string (`?sslmode=require`)
   - `PORT`: `10000` (or leave default for Render auto-injection)

---

## 3. Database Deployment (Neon Serverless Postgres)
1. Sign up at [neon.tech](https://neon.tech) and create a project named `auditregistry`.
2. Open the SQL Editor and execute `backend/schema.sql`.
3. Copy the pooled connection string into your Render backend environment variables.
