//SPDX-License-Identifier: Unlicensed
// Vektor SWAP Command (Uniswap V3)

pragma solidity ^0.8.6;

import "../../../interfaces/Commands/Swap/UniswapV3/ICSwapUniswapV3.sol";
import "../../../interfaces/Commands/Swap/UniswapV3/ISwapRouter.sol";
import "./CSwapBase.sol";

contract CSwapUniswapV3 is CSwapBase, ICSwapUniswapV3 {
    // We have hardcoded ROUTER as there aren't any uni v3 forks.
    // Maybe we should take this as a parameter?

    function _getContractName() internal pure override returns (string memory) {
        return "CSwapUniswapV3";
    }

    ISwapRouter public constant ROUTER = ISwapRouter(0xE592427A0AEce92De3Edee1F18E0157C05861564);

    function sell(
        uint256 amountIn,
        IERC20 tokenIn,
        IERC20 tokenOut,
        uint256 minAmountOut,
        UniswapV3SwapParams calldata params
    ) external payable {
        // check tokenIn
        // check tokenOut

        uint256 balanceBefore = _preSwap(tokenIn, tokenOut, address(ROUTER), amountIn);

        address receiver = params.receiver == address(0) ? address(this) : params.receiver;
        //solhint-disable-next-line not-rely-on-time
        uint256 deadline = params.deadline == 0 ? block.timestamp + 1 : params.deadline;

        ROUTER.exactInput(
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

    /*
    function buy(
        uint256 amountIn,
        IERC20 tokenIn,
        IERC20 tokenOut,
        uint256 minAmountOut,
        UniswapV3SwapParams calldata params
    ) external payable {}
    */
}
