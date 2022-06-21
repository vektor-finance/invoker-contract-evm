//SPDX-License-Identifier: UNLICENSED

pragma solidity ^0.8.6;

import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/utils/Create2.sol";

contract Registry is Ownable {
    event ContractDeployed(address deployedAddress);

    function deployNewContract(
        bytes memory bytecode,
        bytes32 salt,
        uint256 value
    ) external onlyOwner returns (address newContract) {
        newContract = Create2.deploy(value, salt, bytecode);
        emit ContractDeployed(newContract);
    }

    function computeAddress(bytes32 bytecodeHash, bytes32 salt) external view returns (address) {
        return Create2.computeAddress(salt, bytecodeHash);
    }
}
