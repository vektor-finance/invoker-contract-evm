//SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.9;

interface IAaveToken {
    function UNDERLYING_ASSET_ADDRESS() external returns (address tokenAddress);
}
