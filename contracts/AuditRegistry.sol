// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/**
 * @title AuditRegistry
 * @notice Immutable on-chain registry for cryptographic financial audit hashes.
 * @dev Matches the exact ABI exported in dapp.config.json for 100% backward compatibility.
 */
contract AuditRegistry {
    address public owner;

    struct AuditRecord {
        bytes32 dataHash;
        uint256 timestamp;
        address registeredBy;
        bool exists;
    }

    // Mapping: recordKey => AuditRecord
    // where recordKey = keccak256(abi.encodePacked(projectId, dataHash))
    mapping(bytes32 => AuditRecord) private records;

    event AuditRecordRegistered(
        bytes32 indexed recordKey,
        string indexed projectId,
        bytes32 dataHash,
        uint256 timestamp,
        address indexed registeredBy
    );

    modifier onlyOwner() {
        require(msg.sender == owner, "Only owner can call this function");
        _;
    }

    constructor() {
        owner = msg.sender;
    }

    /**
     * @notice Registers a new immutable audit record hash on-chain.
     * @param projectId Identifier for the audited project or organization.
     * @param dataHash 32-byte cryptographic hash of the audit dataset or summary.
     */
    function registerAuditRecord(string calldata projectId, bytes32 dataHash) external {
        require(bytes(projectId).length > 0, "Project ID cannot be empty");
        require(dataHash != bytes32(0), "Data hash cannot be zero");

        bytes32 recordKey = keccak256(abi.encodePacked(projectId, dataHash));
        require(!records[recordKey].exists, "Audit record already registered");

        records[recordKey] = AuditRecord({
            dataHash: dataHash,
            timestamp: block.timestamp,
            registeredBy: msg.sender,
            exists: true
        });

        emit AuditRecordRegistered(recordKey, projectId, dataHash, block.timestamp, msg.sender);
    }

    /**
     * @notice Queries whether an audit record hash is registered and retrieves its metadata.
     * @param projectId Identifier for the audited project or organization.
     * @param dataHash 32-byte cryptographic hash of the audit dataset.
     * @return isVerified True if record exists and is authentic.
     * @return timestamp Block timestamp when the record was anchored.
     * @return registeredBy Address of the auditor who anchored the record.
     */
    function verifyAuditRecord(string calldata projectId, bytes32 dataHash)
        external
        view
        returns (
            bool isVerified,
            uint256 timestamp,
            address registeredBy
        )
    {
        bytes32 recordKey = keccak256(abi.encodePacked(projectId, dataHash));
        AuditRecord memory rec = records[recordKey];
        if (!rec.exists) {
            return (false, 0, address(0));
        }
        return (true, rec.timestamp, rec.registeredBy);
    }
}
