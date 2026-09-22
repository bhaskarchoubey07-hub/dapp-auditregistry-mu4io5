# Audit Registry DApp

A browser-based interface for registering and verifying audit-record hashes with an EVM wallet. The frontend contains no private keys, RPC URLs, seed phrases, or API secrets.

## Requirements

- Node.js 18.18+ (Node.js 20 LTS recommended)
- npm 9+
- A browser wallet connected to the network where the contract is deployed

> **Important:** Remix VM deployments are local to Remix and are not reachable from a Vercel-hosted site. Before deploying this frontend publicly, deploy the contract to a wallet-accessible network and set its address and numeric chain ID in Vercel.

## Local install and run

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd <YOUR_REPOSITORY_DIRECTORY>
cp .env.example .env
```

Edit `.env` with the deployed contract's public address and the wallet's expected numeric chain ID:

```dotenv
VITE_CONTRACT_ADDRESS=0xYOUR_DEPLOYED_AUDIT_REGISTRY_ADDRESS
VITE_EXPECTED_CHAIN_ID=11155111
```

Then install and start the development server:

```bash
npm install
npm run dev
```

## Production build

```bash
npm run build
npm run preview
```

The generated static site is in `dist/`.

## Deploy to Vercel

### Vercel CLI

```bash
npm install --global vercel
vercel login
vercel
vercel --prod
```

In the Vercel project dashboard, add these **Production** environment variables before the production deployment:

```text
VITE_CONTRACT_ADDRESS = 0xYOUR_DEPLOYED_AUDIT_REGISTRY_ADDRESS
VITE_EXPECTED_CHAIN_ID = YOUR_NUMERIC_CHAIN_ID
```

Redeploy after changing environment variables. Values prefixed with `VITE_` are intentionally bundled into the browser, so only use public configuration values.

### GitHub import

1. Push this repository to GitHub (do not commit `.env`).
2. In Vercel, select **Add New → Project** and import the repository.
3. Keep the detected build command `npm run build` and output directory `dist`.
4. Add the two environment variables above in Project Settings → Environment Variables.
5. Deploy.

`vercel.json` rewrites routes to `index.html` so future client-side routes do not produce Vercel 404 responses.

## Checks and current limitation

Run `npm run check` to perform the production build check. This repository has been prepared for GitHub and Vercel, but deployment and a production build have **not** been run from this environment.

The current contract configuration originates from Remix VM (`vm-osaka`). That environment is a build blocker for a public Vercel deployment because external wallet users cannot connect to Remix VM. A public-network contract deployment and its public address/chain ID are required.
