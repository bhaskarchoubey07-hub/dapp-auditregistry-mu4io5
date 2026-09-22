# Local Setup & Execution Guide

---

## 1. Quick Start (Frontend)
```bash
# 1. Install dependencies
npm install

# 2. Start Vite local development server
npm run dev
```
Open your browser at `http://localhost:5173`.

---

## 2. Production Build
```bash
# Verify static production build
npm run build
npm run preview
```

---

## 3. Backend & AI Microservice
```bash
cd backend
python -m venv venv
# On Windows:
.\venv\Scripts\Activate.ps1
# On Linux/macOS:
source venv/bin/activate

pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

---

## 4. Smart Contracts (Hardhat)
```bash
# Run contract unit tests
npx hardhat test

# Deploy to Sepolia testnet
npx hardhat run contracts/scripts/deploy.js --network sepolia
```
