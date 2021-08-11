// SPDX-License-Identifier: GPL-3.0-or-later
// Vektor storage
// Version 0.0.1
// Not production-safe

// Needed to persist variables between executions
// Variables are stored in cache mapping with key and value

pragma solidity ^0.8.6;

contract Storage {
    mapping(bytes32 => bytes32) cache;

    // READ OPERATIONS

    function read(bytes32 _key) public view returns (bytes32) {
        return cache[_key];
    }

    function readAddress(bytes32 _key) public view returns (address) {
        return address(uint160(uint256(cache[_key])));
    }

    function readUint256(bytes32 _key) public view returns (uint256) {
        return uint256(cache[_key]);
    }

    function readBool(bytes32 _key) public view returns (bool) {
        if (cache[_key] == bytes32(uint256(1))) {
            return true;
        } else {
            return false;
        }
    }

    // WRITE OPERATIONS

    function write(bytes32 _key, bytes32 _value) public {
        cache[_key] = _value;
    }

    function writeUint256(bytes32 _key, uint256 _value) public {
        cache[_key] = bytes32(_value);
    }

    function writeAddress(bytes32 _key, address _value) public {
        cache[_key] = bytes32(uint256(uint160(_value)));
    }

    function writeBool(bytes32 _key, bool _value) public {
        if (_value) {
            cache[_key] = bytes32(uint256(1));
        } else {
            cache[_key] = bytes32(uint256(0));
        }
    }
}
