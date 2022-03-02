pragma solidity ^0.8.0;

interface ICSwapUniswapV2 {
    struct UniswapV2SwapParams {
        address router;
        address[] path;
        address receiver;
        uint256 deadline;
    }
}
