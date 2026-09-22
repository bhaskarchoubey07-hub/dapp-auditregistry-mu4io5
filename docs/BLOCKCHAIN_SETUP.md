# Blockchain Architecture & MetaMask Integration Guide

**Contract Name:** `AuditRegistry`  
**Solidity Version:** `^0.8.20`  
**Contract Source:** [`contracts/AuditRegistry.sol`](file:///c:/Users/bhask/OneDrive/Documents/dapp-auditregistry-mu4io5/contracts/AuditRegistry.sol)  
**Configuration:** [`hardhat.config.cjs`](file:///c:/Users/bhask/OneDrive/Documents/dapp-auditregistry-mu4io5/hardhat.config.cjs)  

---

## 1. Smart Contract Architecture

The `AuditRegistry` contract provides an immutable, decentralized attestation anchor for cryptographic audit summaries:

```solidity
contract AuditRegistry {
    address public owner;

    struct AuditRecord {
        bytes32 dataHash;
        uint256 timestamp;
        address registeredBy;
        bool exists;
    }

    mapping(bytes32 => AuditRecord) private records;

    event AuditRecordRegistered(
        bytes32 indexed recordKey,
        string indexed projectId,
        bytes32 dataHash,
        uint256 timestamp,
        address indexed registeredBy
    );
...
```

### Core Functions
1. `registerAuditRecord(string calldata projectId, bytes32 dataHash)`:
   - Validates non-empty `projectId` and non-zero `dataHash`.
   - Computes unique record key: `keccak256(abi.encodePacked(projectId, dataHash))`.
   - Reverts if record already exists (tamper-proofing).
   - Records block timestamp and sender address.
   - Emits `AuditRecordRegistered` event.
2. `verifyAuditRecord(string calldata projectId, bytes32 dataHash)`:
   - Returns `(bool isVerified, uint256 timestamp, address registeredBy)`.

---

## 2. Compiling & Testing Smart Contracts

Run the automated contract test suite:
```bash
npm run test:contracts
```
Executes 6 unit tests covering deployment ownership, valid registration, duplicate prevention, empty inputs, zero hashes, and unverified queries.

---

## 3. Deploying to Ethereum Sepolia Testnet

1. Obtain testnet ETH from a Sepolia faucet (e.g., Google Cloud Web3 Faucet or Alchemy Faucet).
2. Configure `backend/.env` with your deployment private key and RPC:
   ```dotenv
   BLOCKCHAIN_RPC_URL=https://rpc.sepolia.org
   PRIVATE_KEY=your-deployer-private-key
   ```
3. Run deployment script:
   ```bash
   npx hardhat run contracts/scripts/deploy.js --network sepolia
   ```
4. Copy the deployed contract address and set it in `.env`:
   ```dotenv
   VITE_CONTRACT_ADDRESS=0xYourDeployedAddressHere
   VITE_EXPECTED_CHAIN_ID=11155111
   ```

---

## 4. Dual-Mode Web3 Provider Architecture

The frontend (`src/App.jsx`) implements a dual-mode Web3 provider to ensure seamless execution in both production and demo settings:

| Mode | Provider | Use Case |
| :--- | :--- | :--- |
| **MetaMask Live** | EIP-1193 / `window.ethereum` | Live testnet/mainnet transactions signed by auditor browser extension. |
| **Built-In Auditor Wallet** | In-Browser Keypair (`0x71C2B...44Ce`) | Zero-install instant demonstrations and automated test runs. |

### 3-Way Cryptographic Verification
When verifying an audit attestation, the system enforces a strict 3-way consensus:
1. **Database Hash:** Retrieved from Supabase `audit_records`.
2. **Recalculated Hash:** Generated deterministically from the current transaction ledger.
3. **On-Chain Contract Hash:** Read directly from the `AuditRegistry.sol` smart contract via `verifyAuditRecord`.

Only when all three hashes match identically does the interface award the **`VERIFIED ON-CHAIN`** seal.
