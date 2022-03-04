// SPDX-License-Identifier: GPL-3.0-or-later
// Vektor SWAP COMMAND

pragma solidity ^0.8.6;

import "../../interfaces/IUniswapV2Router02.sol";
import "../../interfaces/IWeth.sol";
import "../../interfaces/Commands/Swap/UniswapV2/ICSwapUniswapV2.sol";
import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";

contract CSwapUniswapV2 is ICSwapUniswapV2 {
    using SafeERC20 for IERC20;

    // swapIn
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

    // swapOut
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
