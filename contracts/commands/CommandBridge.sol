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

    IAnyswapV4Router public immutable ANYSWAP_ROUTER;

    constructor(
        IWETH _wnative,
        IERC20 _anyWNATIVE,
        IAnyswapV4Router _router
    ) {
        WNATIVE = _wnative;
        ANY_WNATIVE = _anyWNATIVE;
        ANYSWAP_ROUTER = _router;
    }

    function bridgeNative(
        uint256 amount,
        address destinationAddress,
        uint256 destinationChainID
    ) external payable {
        WNATIVE.deposit{value: amount}();
        WNATIVE.approve(address(ANYSWAP_ROUTER), amount);
        ANYSWAP_ROUTER.anySwapOutUnderlying(
            address(ANY_WNATIVE),
            destinationAddress,
            amount,
            destinationChainID
        );
    }

    function bridgeERC20(
        IERC20 fromToken,
        IERC20 anyToken,
        uint256 amount,
        address destinationAddress,
        uint256 destinationChainID
    ) external payable {
        IERC20 token = fromToken;
        token.safeApprove(address(ANYSWAP_ROUTER), 0);
        token.safeApprove(address(ANYSWAP_ROUTER), amount);
        ANYSWAP_ROUTER.anySwapOutUnderlying(
            address(anyToken),
            destinationAddress,
            amount,
            destinationChainID
        );
    }
}
