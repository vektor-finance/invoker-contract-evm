// SPDX-License-Identifier: GPL-3.0-or-later
// Vektor SWAP COMMAND (Curve)
// Version 1.0.0
// Not production-safe
pragma solidity ^0.8.6;

import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
import "../../interfaces/Commands/Swap/ISwapTemplateCurve.sol";

contract CSwapCurve {
    using SafeERC20 for IERC20;

    function swapCurve(
        uint256 _amountIn,
        uint256 _minAmountOut,
        address[2] calldata _tokens,
        address _pool,
        int128 _i,
        int128 _j
    ) external payable {
        IERC20 tokenIn = IERC20(_tokens[0]);
        IERC20 tokenOut = IERC20(_tokens[1]);
        tokenIn.safeApprove(_pool, 0);
        tokenIn.safeApprove(_pool, _amountIn);
        ISwapTemplateCurve POOL = ISwapTemplateCurve(_pool);
        uint256 balanceBefore = tokenOut.balanceOf(address(this));
        POOL.exchange(_i, _j, _amountIn, _minAmountOut);
        uint256 balanceAfter = tokenOut.balanceOf(address(this));
        require(balanceAfter >= balanceBefore + _minAmountOut, "CSwap: Slippage in");
    }
}
