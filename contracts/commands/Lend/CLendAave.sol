// SPDX-License-Identifier: Unlicensed
pragma solidity ^0.8.9;

import {CLendBase, IERC20} from "./CLendBase.sol";
import {IAaveLendingPool as ILendingPool} from "../../../interfaces/Commands/Lend/IAaveLendingPool.sol";
import {IAaveToken} from "../../../interfaces/Commands/Lend/IAaveToken.sol";

contract CLendAave is CLendBase {
    uint16 public constant REFERRAL_CODE = 0;

    function _getContractName() internal pure override returns (string memory) {
        return "CLendAave";
    }

    function supply(
        ILendingPool lendingPool,
        IERC20 asset,
        uint256 amount,
        address receiver
    ) external payable {
        _tokenApprove(asset, address(lendingPool), amount);
        lendingPool.deposit(address(asset), amount, receiver, REFERRAL_CODE);
    }

    function withdraw(
        ILendingPool lendingPool,
        IAaveToken aAsset,
        uint256 amount,
        address receiver
    ) external payable {
        address underlyingAsset = aAsset.UNDERLYING_ASSET_ADDRESS();
        lendingPool.withdraw(underlyingAsset, amount, receiver);
    }

    function borrow(
        ILendingPool lendingPool,
        IERC20 asset,
        uint256 amount,
        uint256 interestRateMode
    ) external payable {
        lendingPool.borrow(address(asset), amount, interestRateMode, REFERRAL_CODE, msg.sender);
    }

    function repay(
        ILendingPool lendingPool,
        IERC20 asset,
        uint256 amount,
        uint256 interestRateMode
    ) external payable {
        _tokenApprove(asset, address(lendingPool), amount);
        lendingPool.repay(address(asset), amount, interestRateMode, msg.sender);
    }
}
