const hre = require("hardhat");

async function main() {
  const [deployer] = await hre.ethers.getSigners();
  console.log("--------------------------------------------------");
  console.log("Deploying contracts with account:", deployer.address);
  console.log("Account balance:", (await hre.ethers.provider.getBalance(deployer.address)).toString());

  // 1. Deploy baseline AuditRegistry (exact match with existing frontend ABI)
  const AuditRegistry = await hre.ethers.getContractFactory("AuditRegistry");
  const registry = await AuditRegistry.deploy();
  await registry.waitForDeployment();
  const registryAddress = await registry.getAddress();
  console.log("AuditRegistry deployed to:", registryAddress);

  // 2. Deploy enterprise ComplianceAuditRegistry
  const ComplianceRegistry = await hre.ethers.getContractFactory("ComplianceAuditRegistry");
  const complianceRegistry = await ComplianceRegistry.deploy();
  await complianceRegistry.waitForDeployment();
  const complianceAddress = await complianceRegistry.getAddress();
  console.log("ComplianceAuditRegistry deployed to:", complianceAddress);
  console.log("Network:", hre.network.name);
  console.log("--------------------------------------------------");
}

main().catch((error) => {
  console.error("Deployment failed:", error);
  process.exitCode = 1;
});
