//SPDX-License-Identifier: Unlicensed
// Vektor SWAP Command (Uniswap V3)

pragma solidity ^0.8.6;

import "../../../interfaces/Commands/Swap/UniswapV3/ICSwapUniswapV3.sol";
import "../../../interfaces/Commands/Swap/UniswapV3/ISwapRouter.sol";
import "./CSwapBase.sol";

contract CSwapUniswapV3 is CSwapBase, ICSwapUniswapV3 {
    function _getContractName() internal pure override returns (string memory) {
        return "CSwapUniswapV3";
    }

    function sell(
        uint256 amountIn,
        IERC20 tokenIn,
        IERC20 tokenOut,
        uint256 minAmountOut,
        UniswapV3SwapParams calldata params
    ) external payable {
        uint256 balanceBefore = _preSwap(tokenIn, tokenOut, address(params.router), amountIn);

        address receiver = params.receiver == address(0) ? address(this) : params.receiver;
        //solhint-disable-next-line not-rely-on-time
        uint256 deadline = params.deadline == 0 ? block.timestamp + 1 : params.deadline;

        ISwapRouter(params.router).exactInput(
            ISwapRouter.ExactInputParams({
                path: params.path,
                recipient: receiver,
                deadline: deadline,
                amountIn: amountIn,
                amountOutMinimum: minAmountOut
            })
        );

        _postSwap(balanceBefore, tokenOut, minAmountOut);
    }

    function buy(
        uint256 amountOut,
        IERC20 tokenOut,
        IERC20 tokenIn,
        uint256 maxAmountIn,
        UniswapV3SwapParams calldata params
    ) external payable {
        uint256 balanceBefore = _preSwap(tokenIn, tokenOut, address(params.router), maxAmountIn);

        address receiver = params.receiver == address(0) ? address(this) : params.receiver;
        //solhint-disable-next-line not-rely-on-time
        uint256 deadline = params.deadline == 0 ? block.timestamp + 1 : params.deadline;

        ISwapRouter(params.router).exactOutput(
            ISwapRouter.ExactOutputParams({
                path: params.path,
                recipient: receiver,
                deadline: deadline,
                amountOut: amountOut,
                amountInMaximum: maxAmountIn
            })
        );

        _postSwap(balanceBefore, tokenOut, amountOut);
    }
}
