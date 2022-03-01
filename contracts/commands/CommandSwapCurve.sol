// SPDX-License-Identifier: GPL-3.0-or-later
// Vektor SWAP COMMAND (Curve)
pragma solidity ^0.8.6;

import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";

interface ICurvePool {
    function exchange(
        int128 i,
        int128 j,
        uint256 dx,
        uint256 min_dy
    ) external;

    function exchange_underlying(
        int128 i,
        int128 j,
        uint256 dx,
        uint256 min_dy
    ) external;
}

interface ICryptoPool {
    function exchange(
        uint256 i,
        uint256 j,
        uint256 dx,
        uint256 min_dy
    ) external;

    function exchange_underlying(
        uint256 i,
        uint256 j,
        uint256 dx,
        uint256 min_dy
    ) external;
}

contract CSwapCurve {
    using SafeERC20 for IERC20;

    // https://github.com/curvefi/curve-pool-registry/blob/master/contracts/Swaps.vy#L446
    function swapCurve(
        uint256 _amountIn,
        uint256 _minAmountOut,
        address[2] calldata _tokens,
        address _pool,
        uint256[3] calldata _swapParams
    ) external payable {
        IERC20 tokenIn = IERC20(_tokens[0]);
        IERC20 tokenOut = IERC20(_tokens[1]);
        tokenIn.safeApprove(_pool, 0);
        tokenIn.safeApprove(_pool, _amountIn);

        uint256 balanceBefore = tokenOut.balanceOf(address(this));

        if (_swapParams[2] == 1) {
            // Stableswap `exchange`
            ICurvePool(_pool).exchange(
                int128(int256(_swapParams[0])),
                int128(int256(_swapParams[1])),
                _amountIn,
                0
            );
        } else if (_swapParams[2] == 2) {
            // Stableswap `exchange_underlying`
            ICurvePool(_pool).exchange_underlying(
                int128(int256(_swapParams[0])),
                int128(int256(_swapParams[1])),
                _amountIn,
                0
            );
        } else if (_swapParams[2] == 3) {
            // Cryptoswap `exchange`
            ICryptoPool(_pool).exchange(_swapParams[0], _swapParams[1], _amountIn, 0);
        } else if (_swapParams[2] == 4) {
            // Cryptoswap `exchange_underlying`
            ICryptoPool(_pool).exchange_underlying(_swapParams[0], _swapParams[1], _amountIn, 0);
        } else {
            revert("CSwapCurve: Unknown swapParam");
        }

        uint256 balanceAfter = tokenOut.balanceOf(address(this));
        require(balanceAfter >= balanceBefore + _minAmountOut, "CSwap: Slippage in");
    }

    // need to consider how to handle native eth (alternatively, enforce wrapped eth)
}
