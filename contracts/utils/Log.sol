// SPDX-License-Identifier: Unlicensed
pragma solidity ^0.8.6;

contract Log {
    // An invocation will emit a log any time a user calls invoke()
    event LogInvocation(address indexed user, bytes4 indexed sigHash, bytes params, uint256 value);
    // For every command within the invocation, there will be a separate emitted event
    event LogStep(address indexed user, bytes4 indexed sigHash, bytes params);

    modifier logInvocation() {
        emit LogInvocation(msg.sender, msg.sig, msg.data, msg.value);
        _;
    }

    function logStep(bytes calldata params) internal {
        // Extract the function selector from calldata to allow for indexing
        bytes4 sigHash = (bytes4(params[0]) |
            (bytes4(params[1]) >> 8) |
            (bytes4(params[2]) >> 16) |
            (bytes4(params[3]) >> 24));
        emit LogStep(msg.sender, sigHash, params);
    }
}
