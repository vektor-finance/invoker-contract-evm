// SPDX-License-Identifier: GPL-3.0-or-later
// Vektor SWAP COMMAND (Curve)
// Version 1.0.0
// Not production-safe
pragma solidity ^0.8.6;

import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
import "../../interfaces/Commands/Swap/ISwapTemplateCurve.sol";
import "../../interfaces/Commands/Swap/ICurveRegistry.sol";

contract CSwapCurve {
    using SafeERC20 for IERC20;

    event Log(uint256 a);

    ICurveRegistry public immutable CURVE_REGISTRY;

    constructor(ICurveRegistry _registry) {
        CURVE_REGISTRY = _registry;
    }

    function swapCurve(
        uint256 _amountIn,
        uint256 _minAmountOut,
        address[2] calldata _tokens,
        address _pool
    ) external payable {
        IERC20 tokenIn = IERC20(_tokens[0]);
        IERC20 tokenOut = IERC20(_tokens[1]);
        tokenIn.safeApprove(_pool, 0);
        tokenIn.safeApprove(_pool, _amountIn);
        ISwapTemplateCurve POOL = ISwapTemplateCurve(_pool);
        uint256 balanceBefore = tokenOut.balanceOf(address(this));
        (int128 i, int128 j, bool isUnderlying) = CURVE_REGISTRY.get_coin_indices(
            _pool,
            _tokens[0],
            _tokens[1]
        );
        emit Log(address(this).balance);
        emit Log(balanceBefore);
        if (isUnderlying) {
            POOL.exchange_underlying(i, j, _amountIn, _minAmountOut);
        } else {
            POOL.exchange(i, j, _amountIn, _minAmountOut);
        }
        uint256 balanceAfter = tokenOut.balanceOf(address(this));
        emit Log(address(this).balance);
        emit Log(balanceAfter);
        require(balanceAfter >= balanceBefore + _minAmountOut, "CSwap: Slippage in");
    }

    // need to handle eth
    // need to handle underlying / other types of pools
}
