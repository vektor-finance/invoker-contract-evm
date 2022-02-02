// SPDX-License-Identifier: GPL-3.0-or-later
// Utility contract to enable "PAUSER" as a role
// Uses OpenZeppelin AccessControl for roles

pragma solidity ^0.8.6;

import "@openzeppelin/contracts/access/AccessControl.sol";

// PAC is implemented by inheriting this contract
contract PausableAccessControl is AccessControl {
    bytes32 public constant PAUSER = keccak256("ROLE_PAUSER");
    bool public paused = false;

    event Paused(address _account);
    event Unpaused(address _account);

    constructor() {
        // Default behaviour: deployer is the only pauser.
        // Additional pausers can be added/removed using grantRole and revokeRole
        // See documentation for OZ AccessControl for more information
        _setupRole(PAUSER, msg.sender);
    }

    modifier whenPaused() {
        require(paused, "PAC: Not paused");
        _;
    }

    modifier whenNotPaused() {
        require(!paused, "PAC: Paused");
        _;
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
