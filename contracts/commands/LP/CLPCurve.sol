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
    }
}

interface ICurveZap {
    function add_liquidity(uint256[2] calldata amounts, uint256 min_mint_amount) external;

    function add_liquidity(uint256[3] calldata amounts, uint256 min_mint_amount) external;

    function add_liquidity(uint256[4] calldata amounts, uint256 min_mint_amount) external;

    function add_liquidity(uint256[5] calldata amounts, uint256 min_mint_amount) external;

    function add_liquidity(uint256[6] calldata amounts, uint256 min_mint_amount) external;

    function add_liquidity(uint256[7] calldata amounts, uint256 min_mint_amount) external;

    function add_liquidity(uint256[8] calldata amounts, uint256 min_mint_amount) external;
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
        }
    }

    function depositZap(
        uint256[] calldata amounts,
        IERC20[] calldata tokens,
        address zap,
        CurveLPDepositParams calldata params
    ) external payable {
        unchecked {
            for (uint256 i; i < tokens.length; ++i) {
                _approveToken(tokens[i], zap, amounts[i]);
            }
        }
        if (amounts.length == 2) {
            uint256[2] memory coinAmounts = [amounts[0], amounts[1]];
            ICurveZap(zap).add_liquidity(coinAmounts, params.minReceivedLiquidity);
        } else if (amounts.length == 3) {
            uint256[3] memory coinAmounts = [amounts[0], amounts[1], amounts[2]];
            ICurveZap(zap).add_liquidity(coinAmounts, params.minReceivedLiquidity);
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
        }
    }
}