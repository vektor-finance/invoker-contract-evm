// SPDX-License-Identifier: GPL-3.0-or-later
// Vektor Invoker contract
// Not production-safe

pragma solidity ^0.8.6;

import "./utils/Address.sol";

contract Invoker {

    address public owner;
    using Address for address;

    constructor() {
        owner = msg.sender;
    }

    function invoke(address _to, bytes calldata _data, uint256 _value) external payable returns (bytes memory) {
        return _to.functionCallWithValue(_data, _value);
    }
}