// SPDX-License-Identifier: GPL-3.0-or-later
// Vektor Invoker contract
// Not production-safe

pragma solidity ^0.8.6;

import "./utils/Address.sol";
import "./storage.sol";

contract Invoker is Storage{

    address public owner;
    using Address for address;

    // Could probably replace this with the openzeppelin ownable contract
    // Although no access control currently in place
    constructor() {
        owner = msg.sender;
    }

    function invokeStatic(address _to, bytes calldata _data, uint256 _value) external payable returns (bytes memory) {
        return _to.functionCallWithValue(_data, _value);
    }

    function invokeDelegate(address _to, bytes calldata _data) external payable returns (bytes memory) {
        return _to.functionDelegateCall(_data);
    }

    function invoke(address[] calldata _tos, bytes[] calldata _datas) external payable returns(bytes[] memory output) {
        require(_tos.length == _datas.length, "to+data length not equal");
        output = new bytes[](_tos.length);
        for (uint256 i=0; i<_tos.length; i++) {
            output[i] = _tos[i].functionDelegateCall(_datas[i]);
        }
    }

}