//SPDX-License-Identifier: Unlicensed
// Vektor SWAP Command (Uniswap V3)

pragma solidity ^0.8.6;

import "../../interfaces/Commands/Swap/UniswapV3/ICSwapUniswapV3.sol";
import "../../interfaces/Commands/Swap/UniswapV3/ISwapRouter.sol";
import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";

contract CSwapUniswapV3 is ICSwapUniswapV3 {
    // We have hardcoded ROUTER as there aren't any uni v3 forks.
    // Maybe we should take this as a parameter?

    using SafeERC20 for IERC20;

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

        tokenIn.safeApprove(address(ROUTER), 0); // To support tether
        tokenIn.safeApprove(address(ROUTER), amountIn);
        uint256 balanceBefore = tokenOut.balanceOf(address(this));

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

        uint256 balanceAfter = tokenOut.balanceOf(address(this));
        require(balanceAfter >= balanceBefore + minAmountOut, "CSwapUniswapV3: Slippage in");
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
