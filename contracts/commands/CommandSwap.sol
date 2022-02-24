// SPDX-License-Identifier: GPL-3.0-or-later
// Vektor SWAP COMMAND
// Version 1.0.0
// Not production-safe

pragma solidity ^0.8.6;

import "../../interfaces/Commands/Swap/IUniswapV2Router02.sol";
import "../../interfaces/IWeth.sol";
import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";

contract CSwap {
    using SafeERC20 for IERC20;

    IWETH public immutable WNATIVE;

    IUniswapV2Router02 public immutable UNISWAP_ROUTER;

    // When deploying on alternate networks, the WNATIVE address should be specified in constructor
    constructor(address _wnative, address _router) {
        WNATIVE = IWETH(_wnative);
        UNISWAP_ROUTER = IUniswapV2Router02(_router);
    }

    /**
        @notice Allows a user to swap tokens using uniswap.
        @dev After swapping, the output tokens are returned to the invoker contract
        @param _amountIn the amount of input tokens to send
        @param _amountOutMin The minimum amount of tokens that must be received or else the function reverts
        @param _path An array of token addresses that determines the path the route takes
            For example: WETH -> WBTC -> LINK
            This should be optimised off-chain and then passed in this parameter
    **/
    function swapUniswapIn(
        uint256 _amountIn,
        uint256 _amountOutMin,
        address[] calldata _path
    ) external payable {
        require(_path.length > 1, "CSwap: invalid path");
        IERC20 tokenIn = IERC20(_path[0]);
        IERC20 tokenOut = IERC20(_path[_path.length - 1]);
        tokenIn.safeApprove(address(UNISWAP_ROUTER), 0); // To support tether
        tokenIn.safeApprove(address(UNISWAP_ROUTER), _amountIn);
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
        require(balanceAfter >= balanceBefore + _amountOutMin, "CSwap: Slippage in");
    }

    /**
        @notice Allows a user to swap tokens using uniswap.
        @dev After swapping, the output tokens are returned to the invoker contract
        @param _amountOut the amount of output tokens to receive
        @param _amountInMax The maximum amount of inputs tokens that can be required or else the function reverts
        @param _path An array of token addresses that determines the path the route takes
            For example: WETH -> WBTC -> LINK
            This should be optimised off-chain and then passed in this parameter
    **/
    function swapUniswapOut(
        uint256 _amountOut,
        uint256 _amountInMax,
        address[] calldata _path
    ) external payable {
        require(_path.length > 1, "CSwap: invalid path");
        IERC20 tokenIn = IERC20(_path[0]);
        tokenIn.safeApprove(address(UNISWAP_ROUTER), 0); // To support tether
        tokenIn.safeApprove(address(UNISWAP_ROUTER), _amountInMax);
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
        require(balanceAfter + _amountInMax >= balanceBefore, "CSwap: Slippage out");
    }

    /**
        @notice Allows a user to wrap their NATIVE into WNATIVE
        @dev The transferred amount of native is specified by _amount rather than msg.value
            This is intentional to allow users to make multiple native transfers
            Note: User deposits native, but WNATIVE given to invoker contract
                You can then MOVE this WNATIVE
            Validation checks to support wrapping of native tokens that may not conform to WETH9
        @param _amount The amount of NATIVE to wrap (in Wei)
    **/
    function wrapNative(uint256 _amount) external payable {
        uint256 balanceBefore = WNATIVE.balanceOf(address(this));
        WNATIVE.deposit{value: _amount}();
        uint256 balanceAfter = WNATIVE.balanceOf(address(this));
        require(balanceAfter == balanceBefore + _amount, "CSwap: Error wrapping NATIVE");
    }

    /**
        @notice Allows a user to unwrap their WNATIVE into NATIVE
        @dev Transferred amount is specified by _amount
            Note: The WNATIVE must be located on the invoker contract
                The returned NATIVE will be sent to the invoker contract
                This will then need to be MOVED to the user
            Validation checks to support unwrapping of native tokens that may not conform to WETH9
        @param _amount The amount of WNATIVE to unwrap (in Wei)
    **/
    function unwrapWrappedNative(uint256 _amount) external payable {
        uint256 balanceBefore = address(this).balance;
        WNATIVE.withdraw(_amount);
        uint256 balanceAfter = address(this).balance;
        require(balanceAfter == balanceBefore + _amount, "CSwap: Error unwrapping WNATIVE");
    }

    /**
        @notice Allows a user to unwrap their all their WNATIVE into NATIVE
        @dev Transferred amount is the total balance of WNATIVE
            Note: The WNATIVE must be located on the invoker contract
                The returned NATIVE will be sent to the invoker contract
                This will then need to be MOVED to the user
            Validation checks to support unwrapping of native tokens that may not conform to WETH9
    **/
    function unwrapAllWrappedNative() external payable {
        uint256 balance = WNATIVE.balanceOf(address(this));
        if (balance > 0) {
            uint256 balanceBefore = address(this).balance;
            WNATIVE.withdraw(balance);
            uint256 balanceAfter = address(this).balance;
            require(balanceAfter == balanceBefore + balance, "CSwap: Error unwrapping WNATIVE");
        }
    }
}
