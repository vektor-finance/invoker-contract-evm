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
        @param _anyWNATIVE The 'anyToken' for the '_wnative' token
        @dev If native bridging is not supported, please use zero address for '_anyWNATIVE'
    **/
    constructor(IWETH _wnative, IAnyswapV3ERC20 _anyWNATIVE) {
        require(
            _anyWNATIVE.underlying() == address(_wnative) || address(_anyWNATIVE) == address(0),
            "CBridge: Invalid tokens"
        );
        WNATIVE = _wnative;
        ANY_WNATIVE = _anyWNATIVE;
    }

    /**
        @notice Bridge the native asset of this network to destination chain
        @param router The router necessary for this bridge (returned by Anyswap API)
        @param amount The amount of tokens (in Wei) to bridge
        @param destinationAddress The address which will receive the tokens
        @param destinationChainID The chainID of the destination network 
            note: the contract cannot verify that the address-chainID pair is valid
        @dev This wraps the native asset and tries to bridge the wrapped ERC20. 
            This route may not be available on every network. This is the responsibility of the caller to
            ensure that the route is valid. 
    **/
    function bridgeNative(
        IAnyswapV4Router router,
        uint256 amount,
        address destinationAddress,
        uint256 destinationChainID
    ) external payable {
        require(address(ANY_WNATIVE) != address(0), "CBridge: Cannot bridge Native");
        WNATIVE.deposit{value: amount}();
        WNATIVE.approve(address(router), amount);
        router.anySwapOutUnderlying(
            address(ANY_WNATIVE),
            destinationAddress,
            amount,
            destinationChainID
        );
    }

    /**
        @notice Bridge an ERC20 token from this network to destination chain
        @param router The router necessary for this bridge (returned by Anyswap API)
        @param fromToken The token you are attempting to bridge (also known as underlyingToken)
        @param anyToken The corresponding anyToken for your chosen asset.
        @param amount The amount of tokens (in Wei) to bridge
        @param destinationAddress The address which will receive the tokens
        @param destinationChainID The chainID of the destination network 
            note: the contract cannot verify that the address-chainID pair is valid
        @dev This route may not be available on every network. This is the responsibility of the caller to
            ensure that the route is valid. 
    **/
    function bridgeERC20(
        IAnyswapV4Router router,
        IERC20 fromToken,
        IERC20 anyToken,
        uint256 amount,
        address destinationAddress,
        uint256 destinationChainID
    ) external payable {
        fromToken.safeApprove(address(router), 0);
        fromToken.safeApprove(address(router), amount);
        router.anySwapOutUnderlying(
            address(anyToken),
            destinationAddress,
            amount,
            destinationChainID
        );
    }
}
