pragma solidity ^0.8.6;

contract Store {
    mapping(bytes32 => bytes32) public cache;

    constructor() {
        //ad3228b676f7d3cd4284a5443f17f1962b36e491b30a40b2405849e597ba5fb5
        cache[bytes32(uint256(0))] = bytes32(uint256(1));
        cache[bytes32(uint256(1))] = bytes32(uint256(3));
    }
}
