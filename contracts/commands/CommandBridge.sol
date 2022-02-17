// SPDX-License-Identifier: GPL-3.0-or-later
// Vektor BRIDGE COMMAND
// Version 0.0.1
// Not production-safe

pragma solidity ^0.8.6;

import "../../interfaces/IAnyswapV4Router.sol";
import "../../interfaces/IAnyswapV3ERC20.sol";
import "../../interfaces/IWeth.sol";
import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";

contract CBridge {
    using SafeERC20 for IERC20;

    IWETH public immutable WNATIVE;

    IAnyswapV3ERC20 public immutable ANY_WNATIVE;

    /**
        @notice Constructor params for CBridge
        @param _wnative The canonical 'wrapped native' erc20 asset on this network
        @param _anyWNATIVE The `anyToken` for the '_wnative' token
        @dev Although it is possible to derive '_wnative' from '_anyWNATIVE' by calling 'any.underlying()'
            This ensures no accidental deployments
    **/
    constructor(IWETH _wnative, IAnyswapV3ERC20 _anyWNATIVE) {
        require(_anyWNATIVE.underlying() == address(_wnative), "CBridge: Invalid tokens");
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
