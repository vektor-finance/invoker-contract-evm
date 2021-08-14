// SPDX-License-Identifier: GPL-3.0-or-later
// Vektor MOVE COMMAND
// Version 0.0.1
// Not production-safe

pragma solidity ^0.8.6;

import "../../interfaces/IStorage.sol";
import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";

contract CMove {
    using SafeERC20 for IERC20;

    /**
        @notice Allows a user to move their tokens to another address
        @dev Uses OpenZepellin SafeERC20, and validates balance before and after transfer
            to protect users from unknowingly transferring deflationary tokens.
            Solidity compiler 0.8 has built in overflow checks
            Please note: user needs to approve invoker contract first
        @param _token The contract address for the ERC20 token
        @param _to  The address you wish to send the tokens to
        @param _amount The amount of tokens to transfer
    **/
    function move(
        IERC20 _token,
        address _to,
        uint256 _amount
    ) external {
        uint256 balanceBefore = _token.balanceOf(_to);
        address _from = msg.sender;
        _token.transferFrom(_from, _to, _amount);
        uint256 balanceAfter = _token.balanceOf(_to);
        require(balanceAfter == balanceBefore + _amount, "CMove: Invalid balance after move");
    }
}

// Need to consider moving non-erc20 tokens eg erc721 / 1155
// Also need to add supporting interfaces to invoker contract
