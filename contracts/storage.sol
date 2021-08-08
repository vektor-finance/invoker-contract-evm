// SPDX-License-Identifier: GPL-3.0-or-later
// Vektor storage
// Version 0.0.1
// Not production-safe

// Needed to persist variables between executions
// Variables are stored in cache mapping with key and value

pragma solidity ^0.8.6;

contract Storage {
    mapping(bytes32 => bytes32) cache;

    function read(bytes32 _key) public view returns (bytes32) {
        return cache[_key];
    }

    function write(bytes32 _key, bytes32 _value) public {
        cache[_key] = _value;
    }
}