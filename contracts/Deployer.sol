// SPDX-License-Identifier: Unlicensed
pragma solidity ^0.8.0;

import "@0xsequence/Create3.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

contract MasterDeployer is Ownable {
    event ContractDeployed(address _address);

    function deployCode(bytes calldata _code, bytes32 _salt) external onlyOwner {
        emit ContractDeployed(Create3.create3(_salt, _code));
    }
}
