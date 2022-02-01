// SPDX-License-Identifier: GPL-3.0-or-later
// Vektor Invoker contract
// Not production-safe

pragma solidity ^0.8.6;

import "./utils/Address.sol";
import "./Storage.sol";

import "./utils/Log.sol";

import "@openzeppelin/contracts/access/AccessControl.sol";

contract Invoker is Storage, AccessControl, Log {
    using Address for address;

    bytes32 public constant APPROVED_COMMAND_IMPLEMENTATION =
        keccak256("APPROVED_COMMAND_IMPLEMENTATION");

    constructor() {
        _setupRole(DEFAULT_ADMIN_ROLE, msg.sender);
    }

    receive() external payable {
        //Otherwise we can't receive ETH
    }

    function invokeStatic(
        address _to,
        bytes calldata _data,
        uint256 _value
    ) external payable returns (bytes memory) {
        return _to.functionCallWithValue(_data, _value);
    }

    function invokeDelegate(address _to, bytes calldata _data)
        public
        payable
        returns (bytes memory)
    {
        require(hasRole(APPROVED_COMMAND_IMPLEMENTATION, _to), "Command not approved");
        logStep(_data);
        return _to.functionDelegateCall(_data);
    }

    function invoke(address[] calldata _tos, bytes[] calldata _datas)
        external
        payable
        logInvocation
        returns (bytes[] memory output)
    {
        require(_tos.length == _datas.length, "dev: to+data length not equal"); // dev: to+data length not equal
        output = new bytes[](_tos.length);
        for (uint256 i = 0; i < _tos.length; i++) {
            output[i] = invokeDelegate(_tos[i], _datas[i]);
        }
    }
}
