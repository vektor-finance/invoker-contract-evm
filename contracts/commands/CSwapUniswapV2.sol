// SPDX-License-Identifier: GPL-3.0-or-later
// Vektor SWAP COMMAND

pragma solidity ^0.8.6;

import "../../interfaces/IUniswapV2Router02.sol";
import "../../interfaces/IWeth.sol";
import "../../interfaces/Commands/Swap/UniswapV2/ICSwapUniswapV2.sol";
import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";

contract CSwapUniswapV2 is ICSwapUniswapV2 {
    using SafeERC20 for IERC20;

    /** @notice Use this function to perform VXL SELL.
        @dev This function sells an EXACT amount of `tokenIn` to receive `tokenOut`.
        If the price is worse than a threshold, the transaction will revert.
        This function was previously known as 'swapUniswapIn'
        @param amountIn The exact amount of `tokenIn` to sell.
        @param tokenIn The token to sell. Note: This must be an ERC20 token.
        @param tokenOut The token that the user wishes to receive. Note: This must be an ERC20 token.
        @param minAmountOut The minimum amount of `tokenOut` the user wishes to receive.
        @param params Additional parameters to specify UniswapV2 specific parameters. See ICSwapUniswapV2.sol
     */
    function sell(
        uint256 amountIn,
        IERC20 tokenIn,
        IERC20 tokenOut,
        uint256 minAmountOut,
        UniswapV2SwapParams calldata params
    ) external payable {
        require(params.path[0] == address(tokenIn), "CSwapUniswapV2: invalid path");
        require(
            params.path[params.path.length - 1] == address(tokenOut),
            "CSwapUniswapV2: invalid path"
        );
        tokenIn.safeApprove(params.router, 0); // To support tether
        tokenIn.safeApprove(params.router, amountIn);
        address receiver = params.receiver == address(0) ? address(this) : params.receiver;
        //solhint-disable-next-line not-rely-on-time
        uint256 deadline = params.deadline == 0 ? block.timestamp + 1 : params.deadline;
        uint256 balanceBefore = tokenOut.balanceOf(receiver);
        IUniswapV2Router02(params.router).swapExactTokensForTokens(
            amountIn,
            minAmountOut,
            params.path,
            receiver,
            deadline
        );
        uint256 balanceAfter = tokenOut.balanceOf(receiver);
        require(balanceAfter >= balanceBefore + minAmountOut, "CSwapUniswapV2: Slippage in");
    }

    /** @notice Use this function to perform VXL BUY.
        @dev This function buys an EXACT amount of `tokenOut` by spending `tokenIn`.
        If the price is worse than a threshold, the transaction will revert.
        This function was previously known as 'swapUniswapOut`
        @param amountOut The exact amount of `tokenOut` to buy.
        @param tokenOut The token to buy. Note: This must be an ERC20 token.
        @param tokenIn The token that the user wishes to spend. Note: This must be an ERC20 token.
        @param maxAmountIn The maximum amount of `tokenIn` that the user wishes to spend.
        @param params Additional parameters to specify UniswapV2 specific parameters. See ICSwapUniswapV2.sol
     */
    function buy(
        uint256 amountOut,
        IERC20 tokenOut,
        IERC20 tokenIn,
        uint256 maxAmountIn,
        UniswapV2SwapParams calldata params
    ) external payable {
        require(params.path[0] == address(tokenIn), "CSwapUniswapV2: invalid path");
        require(
            params.path[params.path.length - 1] == address(tokenOut),
            "CSwapUniswapV2: invalid path"
        );
        tokenIn.safeApprove(params.router, 0); // To support tether
        tokenIn.safeApprove(params.router, maxAmountIn);
        address receiver = params.receiver == address(0) ? address(this) : params.receiver;
        //solhint-disable-next-line not-rely-on-time
        uint256 deadline = params.deadline == 0 ? block.timestamp + 1 : params.deadline;
        uint256 balanceBefore = tokenIn.balanceOf(receiver);
        IUniswapV2Router02(params.router).swapTokensForExactTokens(
            amountOut,
            maxAmountIn,
            params.path,
            receiver,
            deadline
        );
        uint256 balanceAfter = tokenIn.balanceOf(receiver);
        require(balanceAfter + maxAmountIn >= balanceBefore, "CSwapUniswapV2: Slippage out");
    }
}
