pragma solidity ^0.8.6;

import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";

contract CSwapCurve {
    using SafeERC20 for IERC20;

    function swapCurve(
        address _tokenIn,
        address _tokenOut,
        uint256 _amountIn,
        uint256 _minAmountOut,
        address _pool
    ) external payable {
        (int128 i, int128 j, bool isUnderlying) = REGISTRY.get_coin_indices(_tokenIn, _tokenOut);
        _tokenIn.safeApprove(_pool, 0);
        _tokenIn.safeApprove(_pool, _amountIn);
        POOL = POOL(_pool);
        uint256 balanceBefore = _tokenOut.balanceOf(address(this));
        if (isUnderlying) {}
    }
}
