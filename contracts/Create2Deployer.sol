// SPDX-License-Identifier: UNLICENSED

pragma solidity ^0.8.6;

import "@openzeppelin/contracts/utils/Create2.sol";

contract Create2Deployer {
    mapping(address => uint256) public isAuthorisedToDeploy;

    bytes public deployArgs;

    event ContractDeployed(address deployedAddress);
    event UserAuthorised(address indexed user);
    event UserRevoked(address indexed user);

    constructor(address authorisedDeployer) {
        isAuthorisedToDeploy[authorisedDeployer] = 1;
        emit UserAuthorised(authorisedDeployer);
    }

    modifier onlyAuthorised() {
        require(isAuthorisedToDeploy[msg.sender] == 1, "NOT_AUTHORISED");
        _;
    }

    function authoriseUser(address user) external onlyAuthorised {
        isAuthorisedToDeploy[user] = 1;
        emit UserAuthorised(user);
    }

    function revokeUser(address user) external onlyAuthorised {
        isAuthorisedToDeploy[user] = 0;
        emit UserRevoked(user);
    }

    function deployNewContract(
        bytes calldata bytecode,
        bytes32 salt,
        uint256 value,
        bytes calldata _deployArgs
    ) external payable onlyAuthorised returns (address newContract) {
        deployArgs = _deployArgs;
        newContract = Create2.deploy(value, salt, bytecode);
        emit ContractDeployed(newContract);
        delete deployArgs;
    }
}
