// SPDX-License-Identifier: GPL-3.0-or-later
// Vektor logging contract
// Could have been incorporated directly into Invoker.sol but is a separate contract for readability
// All user interactions will emit events in the form of LogInvocation and LogStep
// These commands do add a gas overhead, further information provided on notion
// https://www.notion.so/vektorfinance/Invoker-Gas-Optimisation-cb1cdce4f8e04ec58bcf7c98ff5502e2
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
