# Known Issues & Workarounds

---

### 1. Remix VM Contracts are Unreachable from External Wallets
- **Issue:** The original contract address (`0xd8b934580fcE35a11B58C6D73aDeE468a2833fa8`) was deployed to Remix VM (`vm-osaka`), which exists only inside Remix IDE memory.
- **Workaround:** Deploy `contracts/AuditRegistry.sol` to Ethereum Sepolia testnet or a local Hardhat node (`http://127.0.0.1:8545`) and update `VITE_CONTRACT_ADDRESS` and `VITE_EXPECTED_CHAIN_ID` in `.env`.

### 2. Render Free-Tier Cold-Start Delay
- **Issue:** Render web services spin down after 15 minutes of inactivity. Initial API calls take 50 to 90 seconds to respond.
- **Workaround:** The frontend application gracefully handles pending states and notifies the user while the backend container wakes up.
