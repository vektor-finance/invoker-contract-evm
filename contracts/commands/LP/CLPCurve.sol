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
        address depositAddress,
        CurveLPDepositParams calldata params
    ) external payable {
        _requireMsg(amounts.length == tokens.length, "amounts+tokens length not equal");
        // for loop `i` cannot overflow, so we use unchecked block to save gas
        unchecked {
            for (uint256 i; i < tokens.length; ++i) {
                if (amounts[i] > 0) {
                    _approveToken(tokens[i], depositAddress, amounts[i]);
                }
            }
        }
        if (amounts.length == 2) {
            uint256[2] memory _tokenAmounts = [amounts[0], amounts[1]];
            if (
                params.lpType == CurveLPType.PLAIN_POOL ||
                params.lpType == CurveLPType.HELPER_CONTRACT_NO_FLAG
            ) {
                ICurveDepositZap(depositAddress).add_liquidity(
                    _tokenAmounts,
                    params.minReceivedLiquidity
                );
            } else if (params.lpType == CurveLPType.PLAIN_POOL_UNDERLYING_FLAG) {
                ICurveDepositZap(depositAddress).add_liquidity(
                    _tokenAmounts,
                    params.minReceivedLiquidity,
                    true
                );
            }
        } else if (amounts.length == 3) {
            uint256[3] memory _tokenAmounts = [amounts[0], amounts[1], amounts[2]];
            if (
                params.lpType == CurveLPType.PLAIN_POOL ||
                params.lpType == CurveLPType.HELPER_CONTRACT_NO_FLAG
            ) {
                ICurveDepositZap(depositAddress).add_liquidity(
                    _tokenAmounts,
                    params.minReceivedLiquidity
                );
            } else if (params.lpType == CurveLPType.PLAIN_POOL_UNDERLYING_FLAG) {
                ICurveDepositZap(depositAddress).add_liquidity(
                    _tokenAmounts,
                    params.minReceivedLiquidity,
                    true
                );
            }
        } else if (amounts.length == 4) {
            uint256[4] memory _tokenAmounts = [amounts[0], amounts[1], amounts[2], amounts[3]];
            if (
                params.lpType == CurveLPType.PLAIN_POOL ||
                params.lpType == CurveLPType.HELPER_CONTRACT_NO_FLAG
            ) {
                ICurveDepositZap(depositAddress).add_liquidity(
                    _tokenAmounts,
                    params.minReceivedLiquidity
                );
            } else if (params.lpType == CurveLPType.PLAIN_POOL_UNDERLYING_FLAG) {
                ICurveDepositZap(depositAddress).add_liquidity(
                    _tokenAmounts,
                    params.minReceivedLiquidity,
                    true
                );
            }
        } else {
            _revertMsg("unsupported length");
        }
    }

    function withdraw(
        IERC20 LPToken,
        uint256 liquidity,
        CurveLPWithdrawParams calldata params
    ) external payable {
        if (params.lpType == CurveLPType.HELPER_CONTRACT_NO_FLAG) {
            _approveToken(LPToken, params.curveWithdrawAddress, liquidity);
        }
        if (params.minimumReceived.length == 2) {
            uint256[2] memory _tokenAmounts = [
                params.minimumReceived[0],
                params.minimumReceived[1]
            ];
            if (
                params.lpType == CurveLPType.PLAIN_POOL ||
                params.lpType == CurveLPType.HELPER_CONTRACT_NO_FLAG
            ) {
                ICurveDepositZap(params.curveWithdrawAddress).remove_liquidity(
                    liquidity,
                    _tokenAmounts
                );
            } else if (params.lpType == CurveLPType.PLAIN_POOL_UNDERLYING_FLAG) {
                ICurveDepositZap(params.curveWithdrawAddress).remove_liquidity(
                    liquidity,
                    _tokenAmounts,
                    true
                );
            }
        } else if (params.minimumReceived.length == 3) {
            uint256[3] memory _tokenAmounts = [
                params.minimumReceived[0],
                params.minimumReceived[1],
                params.minimumReceived[2]
            ];
            if (
                params.lpType == CurveLPType.PLAIN_POOL ||
                params.lpType == CurveLPType.HELPER_CONTRACT_NO_FLAG
            ) {
                ICurveDepositZap(params.curveWithdrawAddress).remove_liquidity(
                    liquidity,
                    _tokenAmounts
                );
            } else if (params.lpType == CurveLPType.PLAIN_POOL_UNDERLYING_FLAG) {
                ICurveDepositZap(params.curveWithdrawAddress).remove_liquidity(
                    liquidity,
                    _tokenAmounts,
                    true
                );
            }
        } else if (params.minimumReceived.length == 4) {
            uint256[4] memory _tokenAmounts = [
                params.minimumReceived[0],
                params.minimumReceived[1],
                params.minimumReceived[2],
                params.minimumReceived[3]
            ];
            if (
                params.lpType == CurveLPType.PLAIN_POOL ||
                params.lpType == CurveLPType.HELPER_CONTRACT_NO_FLAG
            ) {
                ICurveDepositZap(params.curveWithdrawAddress).remove_liquidity(
                    liquidity,
                    _tokenAmounts
                );
            } else if (params.lpType == CurveLPType.PLAIN_POOL_UNDERLYING_FLAG) {
                ICurveDepositZap(params.curveWithdrawAddress).remove_liquidity(
                    liquidity,
                    _tokenAmounts,
                    true
                );
            }
        } else {
            _revertMsg("unsupported length");
        }
    }
}
