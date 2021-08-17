// SPDX-License-Identifier: GPL-3.0-or-later
// Vektor SWAP COMMAND
// Version 0.0.1
// Not production-safe

pragma solidity ^0.8.6;

import "../../interfaces/IERC20.sol";
import "../../interfaces/IWeth.sol";

interface IROUTER {
    function swapExactTokensForTokens(
        uint256 amountIn,
        uint256 amountOutMin,
        address[] calldata path,
        address to,
        uint256 deadline
    ) external returns (uint256[] memory amounts);
}

contract CSwap {
    IWETH public immutable WETH;

    // When deploying on alternate networks, this should be specified in constructor

    constructor(address _weth) {
        WETH = IWETH(_weth);
    }

    function swapExactTokensForTokens(
        uint256 amountIn,
        uint256 amountOutMin,
        address[] calldata path
    ) external {
        require(path.length > 1, "invalid path");
        IROUTER router = IROUTER(0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D);
        IERC20 tokenIn = IERC20(path[0]);
        tokenIn.approve(address(router), amountIn);
        // solhint-disable-next-line not-rely-on-time
        router.swapExactTokensForTokens(
            amountIn,
            amountOutMin,
            path,
            msg.sender,
            block.timestamp + 1
        );
    }

    /**
        @notice Allows a user to wrap their ETH into WETH
        @dev The transferred amount of eth is specified by _amount rather than msg.value
            This is intentional to allow users to make multiple ETH transfers
            Note: User deposits ETH, but WETH given to invoker contract
                You can then MOVE this WETH
            Validation checks to support wrapping of native tokens that may not conform to WETH9
        @param _amount The amount of ETH to wrap (in Wei)
    **/
    function wrapEth(uint256 _amount) external payable {
        uint256 balanceBefore = WETH.balanceOf(address(this));
        WETH.deposit{value: _amount}();
        uint256 balanceAfter = WETH.balanceOf(address(this));
        require(balanceAfter == balanceBefore + _amount, "CSwap: Error wrapping ETH");
    }

    /**
        @notice Allows a user to unwrap their WETH into ETH
        @dev Transferred amount is specified by _amount
            Note: The WETH must be located on the invoker contract
                The returned ETH will be sent to the invoker contract
                This will then need to be MOVED to the user
            Validation checks to support unwrapping of native tokens that may not conform to WETH9
        @param _amount The amount of WETH to unwrap (in Wei)
    **/
    function unwrapEth(uint256 _amount) external {
        uint256 balanceBefore = address(this).balance;
        WETH.withdraw(_amount);
        uint256 balanceAfter = address(this).balance;
        require(balanceAfter == balanceBefore + _amount, "CSwap: Error unwrapping WETH");
    }
}
