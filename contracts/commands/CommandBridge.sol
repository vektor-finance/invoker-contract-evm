// SPDX-License-Identifier: GPL-3.0-or-later
// Vektor BRIDGE COMMAND
// Version 0.0.1
// Not production-safe

pragma solidity ^0.8.6;

import "../../interfaces/IAnyswapV5Router.sol";
import "../../interfaces/IWeth.sol";
import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";

contract CBridge {
    using SafeERC20 for IERC20;

    IWETH public immutable WETH;

    IAnyswapV4Router public immutable ANYSWAP_ROUTER;

    constructor(
        address _weth,
        address _anyWETH,
        address _router
    ) {
        WETH = IWETH(_weth);
        ANY_WETH = IERC20(_anyWETH);
        ANYSWAP_ROUTER = IAnyswapV5Router(_router);
    }

    function bridgeNative(
        uint256 amount,
        address destinationAddress,
        uint256 destinationChainID
    ) external payable {
        WETH.deposit{value: amount}();
        WETH.approve(address(ANYSWAP_ROUTER), amount);
        ANYSWAP_ROUTER.anySwapOutUnderlying(
            address(ANY_WETH),
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
        token.approve(address(ANYSWAP_ROUTER), 0);
        token.approve(address(ANYSWAP_ROUTER), amount);
        ANYSWAP_ROUTER.anySwapOutUnderlying(
            address(anyToken),
            destinationAddress,
            amount,
            destinationChainID
        );
    }
}
