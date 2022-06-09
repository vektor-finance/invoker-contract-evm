//SPDX-License-Identifier: UNLICENSED

pragma solidity ^0.8.6;

import "../../../interfaces/Commands/Swap/Curve/ICryptoPool.sol";
import "../../../interfaces/Commands/Swap/Curve/ICurvePool.sol";
import "./CLPBase.sol";

interface ICLPCurve {
    enum CurveLPType {
        V1_ABI_LIQUIDITY,
        V1_ABI_UNDERLYING,
        V2_ABI_LIQUIDITY,
        V2_ABI_UNDERLYING
    }
    struct CurveLPDepositParams {
        uint256 minReceivedLiquidity;
        bool useHelperContract;
    }
    struct CurveLPWithdrawParams {
        uint256[] minimumReceived;
        bool useHelperContract;
    }
}

interface ICurveDepositZap {
    function add_liquidity(uint256[2] calldata amounts, uint256 min_mint_amount) external;

    function add_liquidity(uint256[3] calldata amounts, uint256 min_mint_amount) external;

    function add_liquidity(uint256[4] calldata amounts, uint256 min_mint_amount) external;

    function add_liquidity(uint256[5] calldata amounts, uint256 min_mint_amount) external;

    function add_liquidity(uint256[6] calldata amounts, uint256 min_mint_amount) external;

    function add_liquidity(uint256[7] calldata amounts, uint256 min_mint_amount) external;

    function add_liquidity(uint256[8] calldata amounts, uint256 min_mint_amount) external;

    function add_liquidity(
        uint256[2] calldata amounts,
        uint256 min_mint_amount,
        bool use_underlying
    ) external;

    function add_liquidity(
        uint256[3] calldata amounts,
        uint256 min_mint_amount,
        bool use_underlying
    ) external;

    function add_liquidity(
        uint256[4] calldata amounts,
        uint256 min_mint_amount,
        bool use_underlying
    ) external;

    function add_liquidity(
        uint256[5] calldata amounts,
        uint256 min_mint_amount,
        bool use_underlying
    ) external;

    function add_liquidity(
        uint256[6] calldata amounts,
        uint256 min_mint_amount,
        bool use_underlying
    ) external;

    function add_liquidity(
        uint256[7] calldata amounts,
        uint256 min_mint_amount,
        bool use_underlying
    ) external;

    function add_liquidity(
        uint256[8] calldata amounts,
        uint256 min_mint_amount,
        bool use_underlying
    ) external;

    function remove_liquidity(uint256 amount, uint256[2] calldata min_amounts) external;

    function remove_liquidity(uint256 amount, uint256[3] calldata min_amounts) external;

    function remove_liquidity(uint256 amount, uint256[4] calldata min_amounts) external;

    function remove_liquidity(uint256 amount, uint256[5] calldata min_amounts) external;

    function remove_liquidity(uint256 amount, uint256[6] calldata min_amounts) external;

    function remove_liquidity(uint256 amount, uint256[7] calldata min_amounts) external;

    function remove_liquidity(uint256 amount, uint256[8] calldata min_amounts) external;

    function remove_liquidity(
        uint256 amount,
        uint256[2] calldata min_amounts,
        bool use_underlying
    ) external;

    function remove_liquidity(
        uint256 amount,
        uint256[3] calldata min_amounts,
        bool use_underlying
    ) external;

    function remove_liquidity(
        uint256 amount,
        uint256[4] calldata min_amounts,
        bool use_underlying
    ) external;

    function remove_liquidity(
        uint256 amount,
        uint256[5] calldata min_amounts,
        bool use_underlying
    ) external;

    function remove_liquidity(
        uint256 amount,
        uint256[6] calldata min_amounts,
        bool use_underlying
    ) external;

    function remove_liquidity(
        uint256 amount,
        uint256[7] calldata min_amounts,
        bool use_underlying
    ) external;

    function remove_liquidity(
        uint256 amount,
        uint256[8] calldata min_amounts,
        bool use_underlying
    ) external;
}

contract CLPCurve is CLPBase, ICLPCurve {
    function _getContractName() internal pure override returns (string memory) {
        return "CLPCurve";
    }

    function deposit(
        uint256[] calldata amounts,
        IERC20[] calldata tokens,
        address pool,
        CurveLPDepositParams calldata params
    ) external payable {
        // for loop cannot overflow
        unchecked {
            for (uint256 i; i < tokens.length; ++i) {
                if (amounts[i] > 0) {
                    _approveToken(tokens[i], pool, amounts[i]);
                }
            }
        }
        if (amounts.length == 2) {
            uint256[2] memory coinAmounts = [amounts[0], amounts[1]];
            ICurvePool(pool).add_liquidity(coinAmounts, params.minReceivedLiquidity);
        } else if (amounts.length == 3) {
            uint256[3] memory coinAmounts = [amounts[0], amounts[1], amounts[2]];
            ICurvePool(pool).add_liquidity(coinAmounts, params.minReceivedLiquidity);
        } else if (amounts.length == 4) {
            uint256[4] memory coinAmounts = [amounts[0], amounts[1], amounts[2], amounts[3]];
            ICurvePool(pool).add_liquidity(coinAmounts, params.minReceivedLiquidity);
        } else {
            _revertMsg("unsupported length");
        }
    }

    function depositHelper(
        uint256[] calldata amounts,
        IERC20[] calldata tokens,
        address depositAddress,
        CurveLPDepositParams calldata params
    ) external payable {
        unchecked {
            for (uint256 i; i < tokens.length; ++i) {
                _approveToken(tokens[i], depositAddress, amounts[i]);
            }
        }
        if (amounts.length == 2) {
            uint256[2] memory coinAmounts = [amounts[0], amounts[1]];
            if (params.useHelperContract) {
                ICurveDepositZap(depositAddress).add_liquidity(
                    coinAmounts,
                    params.minReceivedLiquidity
                );
            } else {
                ICurveDepositZap(depositAddress).add_liquidity(
                    coinAmounts,
                    params.minReceivedLiquidity,
                    true
                );
            }
        } else if (amounts.length == 3) {
            uint256[3] memory coinAmounts = [amounts[0], amounts[1], amounts[2]];
            if (params.useHelperContract) {
                ICurveDepositZap(depositAddress).add_liquidity(
                    coinAmounts,
                    params.minReceivedLiquidity
                );
            } else {
                ICurveDepositZap(depositAddress).add_liquidity(
                    coinAmounts,
                    params.minReceivedLiquidity,
                    true
                );
            }
        } else if (amounts.length == 4) {
            uint256[4] memory coinAmounts = [amounts[0], amounts[1], amounts[2], amounts[3]];
            if (params.useHelperContract) {
                ICurveDepositZap(depositAddress).add_liquidity(
                    coinAmounts,
                    params.minReceivedLiquidity
                );
            } else {
                ICurveDepositZap(depositAddress).add_liquidity(
                    coinAmounts,
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
            uint256[2] memory coinAmounts = [minimumReceived[0], minimumReceived[1]];
            pool.remove_liquidity(liquidity, coinAmounts);
        } else if (minimumReceived.length == 3) {
            uint256[3] memory coinAmounts = [
                minimumReceived[0],
                minimumReceived[1],
                minimumReceived[2]
            ];
            pool.remove_liquidity(liquidity, coinAmounts);
        } else if (minimumReceived.length == 4) {
            uint256[4] memory coinAmounts = [
                minimumReceived[0],
                minimumReceived[1],
                minimumReceived[2],
                minimumReceived[3]
            ];
            pool.remove_liquidity(liquidity, coinAmounts);
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
            uint256[2] memory coinAmounts = [params.minimumReceived[0], params.minimumReceived[1]];
            if (params.useHelperContract) {
                ICurveDepositZap(withdrawAddress).remove_liquidity(liquidity, coinAmounts);
            } else {
                ICurveDepositZap(withdrawAddress).remove_liquidity(liquidity, coinAmounts, true);
            }
        } else if (params.minimumReceived.length == 3) {
            uint256[3] memory coinAmounts = [
                params.minimumReceived[0],
                params.minimumReceived[1],
                params.minimumReceived[2]
            ];
            if (params.useHelperContract) {
                ICurveDepositZap(withdrawAddress).remove_liquidity(liquidity, coinAmounts);
            } else {
                ICurveDepositZap(withdrawAddress).remove_liquidity(liquidity, coinAmounts, true);
            }
        } else if (params.minimumReceived.length == 4) {
            uint256[4] memory coinAmounts = [
                params.minimumReceived[0],
                params.minimumReceived[1],
                params.minimumReceived[2],
                params.minimumReceived[3]
            ];
            if (params.useHelperContract) {
                ICurveDepositZap(withdrawAddress).remove_liquidity(liquidity, coinAmounts);
            } else {
                ICurveDepositZap(withdrawAddress).remove_liquidity(liquidity, coinAmounts, true);
            }
        } else {
            _revertMsg("unsupported length");
        }
    }
}
