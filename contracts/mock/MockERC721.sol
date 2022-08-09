// SPDX-License-Identifier: Unlicensed

pragma solidity ^0.8.9;

import "../external/OpenZeppelin/token/ERC721/ERC721.sol";

contract MockERC721 is ERC721 {
    constructor(string memory name, string memory symbol) ERC721(name, symbol) {}

    function mint(address _to, uint256 _tokenId) external {
        // note: this is unsafe. erc721 can be minted onto invalid receiver
        _mint(_to, _tokenId);
    }
}
