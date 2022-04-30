// SPDX-License-Identifier: Unlicensed

pragma solidity ^0.8.6;

import "../../../interfaces/Commands/Bridge/ISynapseBridge.sol";
import "../../../interfaces/Commands/Wrap/IWeth.sol";
import "./CBridgeBase.sol";

/* 
    from nUSD -> to nUSD: deposit
    from X -> to nUSD: zapAndDeposit

    from X to NATIVE: depositETHAndSwap
    from nUSD -> X: depositAndSwap

    else
    X -> Y: zapAndDepositAndSwap
*/

contract CBridgeSynapse is CBridgeBase {
    // Synapse utilises both an AMM and a bridge to facilitate bridging.
    // Consider the following example:
    // Bridging Avalanche USDC.e to BNB Chain BUSD
    // 1. Avalanche USDC.e is swapped for Avalanche nUSD
    // 2. Avalanche nUSD is bridged to BNB Chain nUSD (in practice, it is burn on Avalanche and minted back on BNB Chain)
    // 3. BNB Chain nUSD is swapped for BNB Chain BUSD.

    // solhint-disable-next-line var-name-mixedcase
    IWETH public immutable WNATIVE;
    // solhint-disable-next-line var-name-mixedcase
    ISynapseBridge public immutable SYNAPSE_BRIDGE;

    /**
        @notice Constructor params for CBridge
        @param _wnative The canonical 'wrapped native' erc20 asset on this network
    **/
    constructor(IWETH _wnative, ISynapseBridge _synapse) {
        WNATIVE = _wnative;
        SYNAPSE_BRIDGE = _synapse;
    }

    /**
     * @notice Relays to nodes to transfers an ERC20 token cross-chain
     * @param amount Amount in native token decimals to transfer cross-chain pre-fees
     * @param destinationAddress address on other chain to bridge assets to
     * @param destinationChainId which chain to bridge assets onto
     **/
    function bridgeNative(
        uint256 amount,
        address destinationAddress,
        uint256 destinationChainId
    ) external payable {
        WNATIVE.deposit{value: amount}();
        _tokenApprove(IERC20(address(WNATIVE)), address(SYNAPSE_BRIDGE), amount);
        SYNAPSE_BRIDGE.deposit(destinationAddress, destinationChainId, address(WNATIVE), amount);
    }

    struct SynapseBridgeParams {
        uint8 tokenIndexFrom;
        uint8 tokenIndexTo;
        uint256 minDy;
        uint256 swapDeadline;
    }

    // Assume that user has already provided the token to be bridged.
    function bridgeERC20Swap(
        IERC20 fromToken,
        IERC20 toToken,
        uint256 amount,
        address destinationAddress,
        uint256 destinationChainId,
        SynapseBridgeParams calldata params
    ) external {
        _tokenApprove(fromToken, address(SYNAPSE_BRIDGE), amount);
        SYNAPSE_BRIDGE.depositAndSwap(
            destinationAddress,
            destinationChainId,
            toToken,
            amount,
            params.tokenIndexFrom,
            params.tokenIndexTo,
            params.minDy,
            params.deadline
        );
    }

    function bridgeERC20(
        IERC20 fromToken,
        uint256 amount,
        address destinationAddress,
        uint256 destinationChainId
    ) external {
        _tokenApprove(fromToken, address(SYNAPSE_BRIDGE), amount);
        SYNAPSE_BRIDGE.deposit(destinationAddress, destinationChainId, fromToken, amount);
    }
}
