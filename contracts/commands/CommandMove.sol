// SPDX-License-Identifier: GPL-3.0-or-later
// Vektor MOVE COMMAND
// Version 0.0.1
// Not production-safe

pragma solidity ^0.8.6;

import "../../interfaces/IStorage.sol";
import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";

contract CMove {
    using SafeERC20 for IERC20;

    function move(
        IERC20 _token,
        address _to,
        uint256 _amount
    ) external {
        uint256 balanceBefore = _token.balanceOf(_to);
        address _from = msg.sender;
        _token.transferFrom(_from, _to, _amount);
        uint256 balanceAfter = _token.balanceOf(_to);
        // Solidity compiler 0.8 has built in overflow checks
        require(balanceAfter == balanceBefore + _amount, "CMove: Invalid balance");
    }
}

// Need to consider moving non-erc20 tokens eg erc721 / 1155
// Also need to add supporting interfaces to invoker contract
