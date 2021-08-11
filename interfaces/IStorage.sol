// SPDX-License-Identifier: GPL-3.0-or-later

pragma solidity ^0.8.6;

interface IStorage {
    // READ OPERATIONS

    function read(bytes32 _key) external view returns (bytes32);

    function readAddress(bytes32 _key) external view returns (address);

    function readUint256(bytes32 _key) external view returns (uint256);

    function readBool(bytes32 _key) external view returns (bool);

    // WRITE OPERATIONS

    function write(bytes32 _key, bytes32 _value) external;

    function writeUint256(bytes32 _key, uint256 _value) external;

    function writeAddress(bytes32 _key, address _value) external;

    function writeBool(bytes32 _key, bool _value) external;
}
