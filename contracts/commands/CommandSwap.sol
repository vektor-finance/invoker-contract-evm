// SPDX-License-Identifier: GPL-3.0-or-later
// Vektor SWAP COMMAND
// Version 0.0.1
// Not production-safe

pragma solidity ^0.8.6;

import "../../interfaces/IERC20.sol";
import "../../interfaces/IWeth.sol";
import "../../interfaces/IUniswapV2Router02.sol";

contract CSwap {
    IWETH public constant WETH = IWETH(0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2);

    IUniswapV2Router02 public constant UNISWAP_ROUTER =
        IUniswapV2Router02(0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D);

    // When deploying on alternate networks, this should be specified in constructor

    function swapUniswapIn(
        uint256 _amountIn,
        uint256 _amountOutMin,
        address[] calldata _path
    ) external {
        require(_path.length > 1, "CSwap: invalid path");
        IERC20 tokenIn = IERC20(_path[0]);
        IERC20 tokenOut = IERC20(_path[_path.length - 1]);
        tokenIn.approve(address(UNISWAP_ROUTER), _amountIn);
        uint256 balanceBefore = tokenOut.balanceOf(address(this));
        UNISWAP_ROUTER.swapExactTokensForTokens(
            _amountIn,
            _amountOutMin,
            _path,
            address(this),
            //solhint-disable-next-line not-rely-on-time
            block.timestamp + 1
        );
        uint256 balanceAfter = tokenOut.balanceOf(address(this));
        require(balanceAfter > balanceBefore + _amountOutMin, "CSwap: Slippage in");
    }

    function swapUniswapOut(
        uint256 _amountOut,
        uint256 _amountInMax,
        address[] calldata _path
    ) external {
        require(_path.length > 1, "CSwap: invalid path");
        IERC20 tokenIn = IERC20(_path[0]);
        tokenIn.approve(address(UNISWAP_ROUTER), _amountInMax);
        uint256 balanceBefore = tokenIn.balanceOf(address(this));
        UNISWAP_ROUTER.swapTokensForExactTokens(
            _amountOut,
            _amountInMax,
            _path,
            address(this),
            //solhint-disable-next-line not-rely-on-time
            block.timestamp + 1
        );
        uint256 balanceAfter = tokenIn.balanceOf(address(this));
        require(balanceAfter > balanceBefore - _amountInMax, "CSwap: Slippage out");
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
