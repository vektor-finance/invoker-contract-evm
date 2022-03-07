// SPDX-License-Identifier: Unlicensed
pragma solidity ^0.8.6;

import "../../../interfaces/Commands/Swap/Curve/ICryptoPool.sol";
import "../../../interfaces/Commands/Swap/Curve/ICSwapCurve.sol";
import "../../../interfaces/Commands/Swap/Curve/ICurvePool.sol";
import "./CSwapBase.sol";

contract CSwapCurve is CSwapBase, ICSwapCurve {
    function _getContractName() internal pure override returns (string memory) {
        return "CSwapCurve";
    }

    // https://github.com/curvefi/curve-pool-registry/blob/master/contracts/Swaps.vy#L446
    function sell(
        uint256 amountIn,
        IERC20 tokenIn,
        IERC20 tokenOut,
        uint256 minAmountOut,
        CurveSwapParams calldata params
    ) external payable {
        uint256 balanceBefore = _preSwap(tokenIn, tokenOut, params.poolAddress, amountIn);

        if (params.swapType == 1) {
            // Stableswap `exchange`
            ICurvePool(params.poolAddress).exchange(
                int128(int256(params.tokenI)),
                int128(int256(params.tokenJ)),
                amountIn,
                minAmountOut
            );
        } else if (params.swapType == 2) {
            // Stableswap `exchange_underlying`
            ICurvePool(params.poolAddress).exchange_underlying(
                int128(int256(params.tokenI)),
                int128(int256(params.tokenJ)),
                amountIn,
                minAmountOut
            );
        } else if (params.swapType == 3) {
            // Cryptoswap `exchange`
            ICryptoPool(params.poolAddress).exchange(
                params.tokenI,
                params.tokenJ,
                amountIn,
                minAmountOut
            );
        } else if (params.swapType == 4) {
            // Cryptoswap `exchange_underlying`
            ICryptoPool(params.poolAddress).exchange_underlying(
                params.tokenI,
                params.tokenJ,
                amountIn,
                minAmountOut
            );
        } else {
            _revertMsg("Unknown swapType");
        }

        _postSwap(balanceBefore, tokenOut, minAmountOut);
    }

    function buy(
        uint256 amountOut,
        IERC20 tokenOut,
        IERC20 tokenIn,
        uint256 maxAmountIn,
        CurveSwapParams calldata params
    ) external payable {
        _revertMsg("buy not supported");
    }

    // need to consider how to handle native eth (alternatively, enforce wrapped eth)
}
