// SPDX-License-Identifier: GPL-3.0-or-later
pragma solidity ^0.8.6;

contract Log {
    event LogInvocation(address indexed user, bytes4 indexed sigHash, bytes params, uint256 value);
    event LogVeks(address indexed user, bytes4 indexed sigHash, bytes params, uint256 value);

    modifier logFunctionCall() {
        emit LogInvocation(msg.sender, msg.sig, msg.data, msg.value);
        _;
    }

    function logVeks(bytes calldata params) internal {
        bytes4 sigHash = (bytes4(params[0]) |
            (bytes4(params[1]) >> 8) |
            (bytes4(params[2]) >> 16) |
            (bytes4(params[3]) >> 24));
        emit LogVeks(msg.sender, sigHash, params, msg.value);
    }
}
