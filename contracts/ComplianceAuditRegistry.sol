// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/**
 * @title ComplianceAuditRegistry
 * @notice Enterprise-grade financial audit registry supporting batch hashing, findings categorization, and verification.
 */
contract ComplianceAuditRegistry {
    error Unauthorized();
    error AlreadyAnchored();
    error AuditNotFound();
    error InvalidHash();

    struct FindingsCount {
        uint16 critical;
        uint16 high;
        uint16 medium;
        uint16 low;
        uint16 informational;
    }

    struct BatchAuditRecord {
        bytes32 batchHash;
        string projectId;
        address auditor;
        uint256 timestamp;
        uint256 recordCount;
        uint256 totalVolumeCents; // Volume stored in cents (to prevent floating point)
        FindingsCount findings;
        string metadataURI; // IPFS CID or HTTPS URL to audit summary report
    }

    address public owner;
    mapping(bytes32 => BatchAuditRecord) private _audits;
    bytes32[] private _allHashes;

    event BatchAuditAnchored(
        bytes32 indexed batchHash,
        string indexed projectId,
        address indexed auditor,
        uint256 timestamp,
        uint256 recordCount,
        uint256 totalVolumeCents,
        string metadataURI
    );

    modifier onlyOwner() {
        if (msg.sender != owner) revert Unauthorized();
        _;
    }

    constructor() {
        owner = msg.sender;
    }

    /**
     * @notice Anchors a completed financial audit batch on-chain.
     */
    function anchorBatchAudit(
        bytes32 batchHash,
        string calldata projectId,
        uint256 recordCount,
        uint256 totalVolumeCents,
        FindingsCount calldata findings,
        string calldata metadataURI
    ) external {
        if (batchHash == bytes32(0)) revert InvalidHash();
        if (_audits[batchHash].timestamp != 0) revert AlreadyAnchored();

        _audits[batchHash] = BatchAuditRecord({
            batchHash: batchHash,
            projectId: projectId,
            auditor: msg.sender,
            timestamp: block.timestamp,
            recordCount: recordCount,
            totalVolumeCents: totalVolumeCents,
            findings: findings,
            metadataURI: metadataURI
        });

        _allHashes.push(batchHash);

        emit BatchAuditAnchored(
            batchHash,
            projectId,
            msg.sender,
            block.timestamp,
            recordCount,
            totalVolumeCents,
            metadataURI
        );
    }

    /**
     * @notice Verifies and retrieves audit record metadata for a given batch hash.
     */
    function getAudit(bytes32 batchHash)
        external
        view
        returns (BatchAuditRecord memory)
    {
        BatchAuditRecord memory record = _audits[batchHash];
        if (record.timestamp == 0) revert AuditNotFound();
        return record;
    }

    /**
     * @notice Quick boolean check whether an audit batch hash is permanently anchored.
     */
    function isAnchored(bytes32 batchHash) external view returns (bool) {
        return _audits[batchHash].timestamp != 0;
    }

    /**
     * @notice Returns the total count of audited batches anchored.
     */
    function totalAnchoredAudits() external view returns (uint256) {
        return _allHashes.length;
    }
}
