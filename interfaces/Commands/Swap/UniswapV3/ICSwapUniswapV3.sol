//SPDX-License-Identifier: Unlicensed
pragma solidity ^0.8.0;

interface ICSwapUniswapV3 {
    struct UniswapV3SwapParams {
        address router;
        bytes path;
        address receiver;
        uint256 deadline;
    }
}
