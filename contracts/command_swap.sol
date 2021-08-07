// SPDX-License-Identifier: GPL-3.0-or-later
// Vektor SWAP COMMAND
// Version 0.0.1
// Not production-safe

pragma solidity ^0.8.6;

interface IERC20 {
    function approve(address spender, uint256 amount) external returns (bool);
}

interface IROUTER {
    function swapExactTokensForTokens(
        uint amountIn,
        uint amountOutMin,
        address[] calldata path,
        address to,
        uint deadline
    ) external returns (uint[] memory amounts);
}

contract CSwap {
    
    function swapExactTokensForTokens(uint256 amountIn, uint256 amountOutMin, address[] calldata path) external returns (uint[] memory amounts){
        require(path.length>1,"invalid path");
        IROUTER router = IROUTER(0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D);
        IERC20 tokenIn = IERC20(path[0]);
        tokenIn.approve(address(router), amountIn);
        router.swapExactTokensForTokens(amountIn, amountOutMin, path, msg.sender, block.timestamp+1); 
    }

}