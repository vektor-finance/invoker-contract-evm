// SPDX-License-Identifier: Unlicensed

pragma solidity ^0.8.6;

import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
import "@openzeppelin/contracts/token/ERC721/IERC721.sol";

contract CMove {
    using SafeERC20 for IERC20;

    /**
        @notice Allows a user to move their tokens to the invoker
        @dev Uses OpenZepellin SafeERC20, and validates balance before and after transfer
            to protect users from unknowingly transferring deflationary tokens.
            Solidity compiler 0.8 has built in overflow checks
            Please note: user needs to approve invoker contract first
        @param _token The contract address for the ERC20 token
        @param _amount The amount of tokens to transfer
    **/
    function moveERC20In(IERC20 _token, uint256 _amount) external payable {
        uint256 balanceBefore = _token.balanceOf(address(this));
        _token.safeTransferFrom(msg.sender, address(this), _amount);
        uint256 balanceAfter = _token.balanceOf(address(this));
        require(balanceAfter == balanceBefore + _amount, "CMove: Deflationary token");
    }

    /**
        @notice Allows a user to move their tokens from the invoker to another address
        @dev Uses OpenZepellin SafeERC20, and validates balance before and after transfer
            to protect users from unknowingly transferring deflationary tokens.
            Solidity compiler 0.8 has built in overflow checks
        @param _token The contract address for the ERC20 token
        @param _to  The address you wish to send the tokens to
        @param _amount The amount of tokens to transfer
    **/
    function moveERC20Out(
        IERC20 _token,
        address _to,
        uint256 _amount
    ) external payable {
        uint256 balanceBefore = _token.balanceOf(_to);
        _token.safeTransfer(_to, _amount);
        uint256 balanceAfter = _token.balanceOf(_to);
        require(balanceAfter == balanceBefore + _amount, "CMove: Deflationary token");
    }

    /**
        @notice Allows a user to move entire balance of a token from the invoker to another address
        @dev Uses OpenZepellin SafeERC20, and validates balance before and after transfer
            to protect users from unknowingly transferring deflationary tokens.
            Solidity compiler 0.8 has built in overflow checks
        @param _token The contract address for the ERC20 token
        @param _to  The address you wish to send the tokens to
    **/
    function moveAllERC20Out(IERC20 _token, address _to) external payable {
        uint256 amount = _token.balanceOf(address(this));
        if (amount > 0) {
            uint256 balanceBefore = _token.balanceOf(_to);
            _token.safeTransfer(_to, amount);
            uint256 balanceAfter = _token.balanceOf(_to);
            require(balanceAfter == balanceBefore + amount, "CMove: Deflationary token");
        }
    }

    /**
        @notice Allows a user to move their native asset to another address
        @dev The transferred amount of native is specified by _amount rather than msg.value
            This is intentional to allow users to make multiple native transfers
        @param _to The address you wish to send native to
        @param _amount The amount of native to transfer (in Wei)
    **/
    function moveNative(address _to, uint256 _amount) external payable {
        //solhint-disable-next-line avoid-low-level-calls
        (bool success, ) = _to.call{value: _amount}(new bytes(0));
        require(success, "CMove: Native transfer failed");
    }

    /**
        @notice Allows a user to move all the native asset in the Invoker to another address
        @dev The transferred amount of native is specified by current balance of the Invoker
        at the time of being called
        @param _to The address you wish to send native to
    **/
    function moveAllNativeOut(address _to) external payable {
        uint256 balance = address(this).balance;
        if (balance > 0) {
            //solhint-disable-next-line avoid-low-level-calls
            (bool success, ) = _to.call{value: balance}(new bytes(0));
            require(success, "CMove: Native transfer failed");
        }
    }

    /**
        @notice Allows a user to move an ERC721 token into the invoker
        @dev ERC721 ensures that transferred tokenId is vaild. Here we make an unsafe transfer
        which does not call `onERC721Received` on the invoker. ERC721 tokens will not be stuck
        on the invoker as we also provide a `moveERC721Out` function
        @param _token The contract address for the ERC721 token
        @param _tokenId The NFT identifier
    **/
    function moveERC721In(IERC721 _token, uint256 _tokenId) external payable {
        _token.transferFrom(msg.sender, address(this), _tokenId);
    }

    /**
        @notice Allows a user to move an ERC721 token from the invoker
        @dev We enforce that the receiving `_to` is able to receive the ERC721 token by performing
        a `safeTransferFrom`
        @param _token The contract address for the ERC721 token
        @param _tokenId The NFT identifier
        @param _to The address to receive the ERC721 token.
    **/
    function moveERC721Out(
        IERC721 _token,
        uint256 _tokenId,
        address _to
    ) external payable {
        _token.safeTransferFrom(address(this), _to, _tokenId);
    }
}
