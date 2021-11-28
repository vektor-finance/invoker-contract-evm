// SPDX-License-Identifier: GPL-3.0-or-later
// Vektor logging contract
// Could have been incorporated directly into Invoker.sol but is a separate contract for readability
// All user interactions will emit events in the form of LogInvocation and LogVeks
// These commands do add a gas overhead
// With logs:
// Invoker <Contract>
//    ├─ constructor  -  avg: 1184956  avg (confirmed): 1184956  low: 1184956  high: 1184956
//    ├─ invokeStatic -  avg:  132098  avg (confirmed):  132098  low:  132098  high:  132098
//    ├─ invoke       -  avg:  111746  avg (confirmed):  111542  low:   32297  high:  329434
//    └─ grantRole    -  avg:   50362  avg (confirmed):   49952  low:   29252  high:   56504
pragma solidity ^0.8.6;

contract Log {
    // An invocation will emit a log any time a user calls invoke()
    event LogInvocation(address indexed user, bytes4 indexed sigHash, bytes params, uint256 value);
    // For every command within the invocation, there will be a separate emitted event
    event LogVeks(address indexed user, bytes4 indexed sigHash, bytes params, uint256 value);

    modifier logInvocation() {
        emit LogInvocation(msg.sender, msg.sig, msg.data, msg.value);
        _;
    }

    function logVeks(bytes calldata params) internal {
        // Extract the function selector from calldata to allow for indexing
        bytes4 sigHash = (bytes4(params[0]) |
            (bytes4(params[1]) >> 8) |
            (bytes4(params[2]) >> 16) |
            (bytes4(params[3]) >> 24));
        emit LogVeks(msg.sender, sigHash, params, msg.value);
    }
}
