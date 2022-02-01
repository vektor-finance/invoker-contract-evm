// SPDX-License-Identifier: GPL-3.0-or-later
// Utility contract to enable "PAUSER" as a role
// Uses OpenZeppelin AccessControl for roles

pragma solidity ^0.8.6;

import "@openzeppelin/contracts/access/AccessControl.sol";

contract PausableAccessControl is AccessControl {
    bytes32 public constant PAUSER = keccak256("PAUSER");
    bool public paused = false;

    event Paused(address _account);
    event Unpaused(address _account);

    constructor() {
        _setupRole(PAUSER, msg.sender);
    }

    modifier whenPaused() {
        require(paused, "PAC: Not paused");
        _;
    }

    modifier whenNotPaused() {
        require(!paused, "PAC: Paused");
    }

    function pause() external whenNotPaused {
        require(hasRole(PAUSER, msg.sender), "PAC: Invalid role");
        paused = true;
        emit Paused(msg.sender);
    }

    function unpause() external whenPaused {
        require(hasRole(PAUSER, msg.sender), "PAC: Invalid role");
        paused = false;
        emit Unpaused(msg.sender);
    }
}
