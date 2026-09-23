const { expect } = require("chai");
const { ethers } = require("hardhat");

describe("AuditRegistry Smart Contracts", function () {
  let AuditRegistry, registry, owner, auditor, user;
  const projectId = "fintech-audit-2026-q3";
  const dummyHash = ethers.keccak256(ethers.toUtf8Bytes("canonical-audit-batch-data-001"));

  beforeEach(async function () {
    [owner, auditor, user] = await ethers.getSigners();
    AuditRegistry = await ethers.getContractFactory("AuditRegistry");
    registry = await AuditRegistry.deploy();
  });

  describe("Deployment", function () {
    it("Should set the correct deployer as owner", async function () {
      expect(await registry.owner()).to.equal(owner.address);
    });
  });

  describe("Audit Record Registration", function () {
    it("Should successfully register a new audit record and emit event", async function () {
      const recordKey = ethers.keccak256(
        ethers.solidityPacked(["string", "bytes32"], [projectId, dummyHash])
      );

      await expect(registry.connect(auditor).registerAuditRecord(projectId, dummyHash))
        .to.emit(registry, "AuditRecordRegistered");

      const [isVerified, timestamp, registeredBy] = await registry.verifyAuditRecord(projectId, dummyHash);
      expect(isVerified).to.be.true;
      expect(registeredBy).to.equal(auditor.address);
      expect(timestamp).to.be.greaterThan(0);
    });

    it("Should prevent registering duplicate audit records", async function () {
      await registry.connect(auditor).registerAuditRecord(projectId, dummyHash);
      await expect(
        registry.connect(auditor).registerAuditRecord(projectId, dummyHash)
      ).to.be.revertedWith("Audit record already registered");
    });

    it("Should revert if project ID is empty", async function () {
      await expect(
        registry.connect(auditor).registerAuditRecord("", dummyHash)
      ).to.be.revertedWith("Project ID cannot be empty");
    });

    it("Should revert if data hash is zero", async function () {
      await expect(
        registry.connect(auditor).registerAuditRecord(projectId, ethers.ZeroHash)
      ).to.be.revertedWith("Data hash cannot be zero");
    });
  });

  describe("Audit Verification", function () {
    it("Should return false for unregistered records", async function () {
      const nonExistentHash = ethers.keccak256(ethers.toUtf8Bytes("random-hash"));
      const [isVerified, timestamp, registeredBy] = await registry.verifyAuditRecord(projectId, nonExistentHash);
      expect(isVerified).to.be.false;
      expect(timestamp).to.equal(0n);
      expect(registeredBy).to.equal(ethers.ZeroAddress);
    });
  });
});
