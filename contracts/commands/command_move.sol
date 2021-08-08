// SPDX-License-Identifier: GPL-3.0-or-later
// Vektor MOVE COMMAND
// Version 0.0.1
// Not production-safe

pragma solidity ^0.8.6;

interface IERC20 {
    function transferFrom(
        address sender,
        address recipient,
        uint256 amount
    ) external returns (bool);
}

contract CMove {
    
    function move(IERC20 _token, address _from, address _to, uint256 _amount) external returns (bool) {
        return _token.transferFrom(_from, _to, _amount);
    }
    // Need to add pre + post balance checks

}

// Need to consider moving non-erc20 tokens eg erc721 / 1155
// Also need to add supporting interfaces to invoker contract