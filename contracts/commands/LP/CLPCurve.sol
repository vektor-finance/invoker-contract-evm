//SPDX-License-Identifier: UNLICENSED

pragma solidity ^0.8.6;

import "../../../interfaces/Commands/Swap/Curve/ICryptoPool.sol";
import "../../../interfaces/Commands/Swap/Curve/ICurvePool.sol";
import "../../../interfaces/Commands/LP/Curve/ICLPCurve.sol";
import "../../../interfaces/Commands/LP/Curve/ICurveDepositZap.sol";
import "./CLPBase.sol";

contract CLPCurve is CLPBase, ICLPCurve {
    function _getContractName() internal pure override returns (string memory) {
        return "CLPCurve";
    }

    function deposit(
        IERC20[] calldata tokens,
        uint256[] calldata amounts,
        address pool,
        CurveLPDepositParams calldata params
    ) external payable {
        _requireMsg(amounts.length == tokens.length, "amounts+tokens length not equal");
        // for loop `i` cannot overflow, so we use unchecked block to save gas
        unchecked {
            for (uint256 i; i < tokens.length; ++i) {
                if (amounts[i] > 0) {
                    _approveToken(tokens[i], pool, amounts[i]);
                }
            }
        }
        if (amounts.length == 2) {
            uint256[2] memory _tokenAmounts = [amounts[0], amounts[1]];
            ICurvePool(pool).add_liquidity(_tokenAmounts, params.minReceivedLiquidity);
        } else if (amounts.length == 3) {
            uint256[3] memory _tokenAmounts = [amounts[0], amounts[1], amounts[2]];
            ICurvePool(pool).add_liquidity(_tokenAmounts, params.minReceivedLiquidity);
        } else if (amounts.length == 4) {
            uint256[4] memory _tokenAmounts = [amounts[0], amounts[1], amounts[2], amounts[3]];
            ICurvePool(pool).add_liquidity(_tokenAmounts, params.minReceivedLiquidity);
        } else {
            _revertMsg("unsupported length");
        }
    }

    function depositHelper(
        IERC20[] calldata tokens,
        uint256[] calldata amounts,
        address depositAddress,
        CurveLPDepositParams calldata params
    ) external payable {
        _requireMsg(amounts.length == tokens.length, "amounts+tokens length not equal");
        // for loop `i` cannot overflow, so we use unchecked block to save gas
        unchecked {
            for (uint256 i; i < tokens.length; ++i) {
                _approveToken(tokens[i], depositAddress, amounts[i]);
            }
        }
        if (amounts.length == 2) {
            uint256[2] memory _tokenAmounts = [amounts[0], amounts[1]];
            if (params.useHelperContract) {
                ICurveDepositZap(depositAddress).add_liquidity(
                    _tokenAmounts,
                    params.minReceivedLiquidity
                );
            } else {
                ICurveDepositZap(depositAddress).add_liquidity(
                    _tokenAmounts,
                    params.minReceivedLiquidity,
                    true
                );
            }
        } else if (amounts.length == 3) {
            uint256[3] memory _tokenAmounts = [amounts[0], amounts[1], amounts[2]];
            if (params.useHelperContract) {
                ICurveDepositZap(depositAddress).add_liquidity(
                    _tokenAmounts,
                    params.minReceivedLiquidity
                );
            } else {
                ICurveDepositZap(depositAddress).add_liquidity(
                    _tokenAmounts,
                    params.minReceivedLiquidity,
                    true
                );
            }
        } else if (amounts.length == 4) {
            uint256[4] memory _tokenAmounts = [amounts[0], amounts[1], amounts[2], amounts[3]];
            if (params.useHelperContract) {
                ICurveDepositZap(depositAddress).add_liquidity(
                    _tokenAmounts,
                    params.minReceivedLiquidity
                );
            } else {
                ICurveDepositZap(depositAddress).add_liquidity(
                    _tokenAmounts,
                    params.minReceivedLiquidity,
                    true
                );
            }
        } else {
            _revertMsg("unsupported length");
        }
        // need to continue for further permutations
        // need to calculate % likelihood of each size
    }

    function withdraw(
        ICurvePool pool,
        uint256 liquidity,
        uint256[] calldata minimumReceived
    ) external payable {
        if (minimumReceived.length == 2) {
            uint256[2] memory _tokenAmounts = [minimumReceived[0], minimumReceived[1]];
            pool.remove_liquidity(liquidity, _tokenAmounts);
        } else if (minimumReceived.length == 3) {
            uint256[3] memory _tokenAmounts = [
                minimumReceived[0],
                minimumReceived[1],
                minimumReceived[2]
            ];
            pool.remove_liquidity(liquidity, _tokenAmounts);
        } else if (minimumReceived.length == 4) {
            uint256[4] memory _tokenAmounts = [
                minimumReceived[0],
                minimumReceived[1],
                minimumReceived[2],
                minimumReceived[3]
            ];
            pool.remove_liquidity(liquidity, _tokenAmounts);
        } else {
            _revertMsg("unsupported length");
        }
    }

    function withdrawHelper(
        IERC20 LPToken,
        address withdrawAddress,
        uint256 liquidity,
        CurveLPWithdrawParams calldata params
    ) external payable {
        _approveToken(LPToken, withdrawAddress, liquidity);
        if (params.minimumReceived.length == 2) {
            uint256[2] memory _tokenAmounts = [
                params.minimumReceived[0],
                params.minimumReceived[1]
            ];
            if (params.useHelperContract) {
                ICurveDepositZap(withdrawAddress).remove_liquidity(liquidity, _tokenAmounts);
            } else {
                ICurveDepositZap(withdrawAddress).remove_liquidity(liquidity, _tokenAmounts, true);
            }
        } else if (params.minimumReceived.length == 3) {
            uint256[3] memory _tokenAmounts = [
                params.minimumReceived[0],
                params.minimumReceived[1],
                params.minimumReceived[2]
            ];
            if (params.useHelperContract) {
                ICurveDepositZap(withdrawAddress).remove_liquidity(liquidity, _tokenAmounts);
            } else {
                ICurveDepositZap(withdrawAddress).remove_liquidity(liquidity, _tokenAmounts, true);
            }
        } else if (params.minimumReceived.length == 4) {
            uint256[4] memory _tokenAmounts = [
                params.minimumReceived[0],
                params.minimumReceived[1],
                params.minimumReceived[2],
                params.minimumReceived[3]
            ];
            if (params.useHelperContract) {
                ICurveDepositZap(withdrawAddress).remove_liquidity(liquidity, _tokenAmounts);
            } else {
                ICurveDepositZap(withdrawAddress).remove_liquidity(liquidity, _tokenAmounts, true);
            }
        } else {
            _revertMsg("unsupported length");
        }
    }
}
