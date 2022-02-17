// SPDX-License-Identifier: GPL-3.0-or-later
// Vektor BRIDGE COMMAND
// Version 0.0.1
// Not production-safe

pragma solidity ^0.8.6;

import "../../interfaces/IAnyswapV4Router.sol";
import "../../interfaces/IWeth.sol";
import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";

contract CBridge {
    using SafeERC20 for IERC20;

    IWETH public immutable WNATIVE;

    IERC20 public immutable ANY_WNATIVE;

    constructor(IWETH _wnative, IERC20 _anyWNATIVE) {
        WNATIVE = _wnative;
        ANY_WNATIVE = _anyWNATIVE;
    }

    function bridgeNative(
        IAnyswapV4Router router,
        uint256 amount,
        address destinationAddress,
        uint256 destinationChainID
    ) external payable {
        WNATIVE.deposit{value: amount}();
        WNATIVE.approve(address(router), amount);
        router.anySwapOutUnderlying(
            address(ANY_WNATIVE),
            destinationAddress,
            amount,
            destinationChainID
        );
    }

    function bridgeERC20(
        IAnyswapV4Router router,
        IERC20 fromToken,
        IERC20 anyToken,
        uint256 amount,
        address destinationAddress,
        uint256 destinationChainID
    ) external payable {
        IERC20 token = fromToken;
        token.safeApprove(address(router), 0);
        token.safeApprove(address(router), amount);
        router.anySwapOutUnderlying(
            address(anyToken),
            destinationAddress,
            amount,
            destinationChainID
        );
    }
}
