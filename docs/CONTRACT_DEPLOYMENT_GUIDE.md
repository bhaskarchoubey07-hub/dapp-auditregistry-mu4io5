# Contract Deployment Guide

**Target Network:** Ethereum Sepolia Testnet (Chain ID: `11155111`) / Local Hardhat Node (Chain ID: `31337`)  

---

## 1. Prerequisites
1. Node.js 18+ and npm installed.
2. A testnet wallet (e.g. MetaMask) funded with Sepolia ETH from a faucet:
   - [Google Cloud Web3 Sepolia Faucet](https://cloud.google.com/application/web3/faucet/ethereum/sepolia)
   - [Alchemy Sepolia Faucet](https://sepoliafaucet.com/)
3. An RPC endpoint URL from Infura or Alchemy (or public RPC: `https://rpc.sepolia.org`).

---

## 2. Deployment Instructions

### Local Development Network (Hardhat)
```bash
# Terminal 1: Launch local EVM node
npx hardhat node

# Terminal 2: Deploy contract to local node
npx hardhat run contracts/scripts/deploy.js --network localhost
```

### Public Testnet (Sepolia)
Set your environment variables:
```bash
export SEPOLIA_RPC_URL="https://rpc.sepolia.org"
export PRIVATE_KEY="your_testnet_account_private_key"
```

Execute deployment:
```bash
npx hardhat run contracts/scripts/deploy.js --network sepolia
```

Record the deployed contract address output:
```text
AuditRegistry deployed to: 0xYourDeployedContractAddress
```

Update your frontend `.env`:
```dotenv
VITE_CONTRACT_ADDRESS=0xYourDeployedContractAddress
VITE_EXPECTED_CHAIN_ID=11155111
```
