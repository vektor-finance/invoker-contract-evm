// SPDX-License-Identifier: UNLICENSED

pragma solidity ^0.8.6;

interface ICLPUniswapV2 {
    struct UniswapV2LPParams {
        address router;
        uint256 amountAMin;
        uint256 amountBMin;
        address receiver;
        uint256 deadline;
    }
}
