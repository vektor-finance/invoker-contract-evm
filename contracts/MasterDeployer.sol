// SPDX-License-Identifier: Unlicensed
pragma solidity ^0.8.0;

import "@0xsequence/Create3.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

/// @notice Lightweight deployer contract to allow consistent addresses across chains
/// @dev Utilises CREATE3 to decouple deployment address from bytecode
///     Address can be calculated off-chain by Create3.addressOf(salt)
///     Any contract which uses msg.sender within constructor will be pointing to
///     this factory contract, not the deployer! Be careful with access control.
contract MasterDeployer is Ownable {
    event ContractDeployed(address deployedAddress);

    /// @notice Deploy a contract with a specified salt
    /// @dev The deployed address is only dependent on salt, not on creation code.
    ///     If a contract is already deployed at that address, this call will fail
    /// @param _code The bytecode for the deployed contract
    /// @param _salt The salt used to generate the deployment address
    function deployCode(bytes memory _code, bytes32 _salt)
        external
        onlyOwner
        returns (address _contract)
    {
        _contract = Create3.create3(_salt, _code);
        emit ContractDeployed(_contract);
    }

    function addressOf(bytes32 _salt) external view returns (address) {
        return Create3.addressOf(_salt);
    }
}
