// SPDX-License-Identifier: GPL-3.0-or-later
// Vektor SWAP COMMAND (Curve)
pragma solidity ^0.8.6;

import "../../interfaces/Commands/Swap/Curve/ICryptoPool.sol";
import "../../interfaces/Commands/Swap/Curve/ICSwapCurve.sol";
import "../../interfaces/Commands/Swap/Curve/ICurvePool.sol";
import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";

contract CSwapCurve is ICSwapCurve {
    using SafeERC20 for IERC20;

    // https://github.com/curvefi/curve-pool-registry/blob/master/contracts/Swaps.vy#L446
    function sell(
        uint256 amountIn,
        uint256 minAmountOut,
        address[2] calldata tokens,
        CurveSwapParams calldata params
    ) external payable {
        IERC20 tokenIn = IERC20(tokens[0]);
        IERC20 tokenOut = IERC20(tokens[1]);
        tokenIn.safeApprove(params.poolAddress, 0);
        tokenIn.safeApprove(params.poolAddress, amountIn);

        uint256 balanceBefore = tokenOut.balanceOf(address(this));

        if (params.swapType == 1) {
            // Stableswap `exchange`
            ICurvePool(params.poolAddress).exchange(
                int128(int256(params.tokenI)),
                int128(int256(params.tokenJ)),
                amountIn,
                0
            );
        } else if (params.swapType == 2) {
            // Stableswap `exchange_underlying`
            ICurvePool(params.poolAddress).exchange_underlying(
                int128(int256(params.tokenI)),
                int128(int256(params.tokenJ)),
                amountIn,
                0
            );
        } else if (params.swapType == 3) {
            // Cryptoswap `exchange`
            ICryptoPool(params.poolAddress).exchange(params.tokenI, params.tokenJ, amountIn, 0);
        } else if (params.swapType == 4) {
            // Cryptoswap `exchange_underlying`
            ICryptoPool(params.poolAddress).exchange_underlying(
                params.tokenI,
                params.tokenJ,
                amountIn,
                0
            );
        } else {
            revert("CSwapCurve: Unknown swapType");
        }

        uint256 balanceAfter = tokenOut.balanceOf(address(this));
        require(balanceAfter >= balanceBefore + minAmountOut, "CSwap: Slippage in");
    }

    // need to consider how to handle native eth (alternatively, enforce wrapped eth)
}
