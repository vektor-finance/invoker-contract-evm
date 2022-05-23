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
    struct CurveLPWithdrawParams {
        CurveLPType lpType;
    }
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
            uint256[2] memory coin_amounts = [amounts[0], amounts[1]];
            ICurvePool(pool).add_liquidity(coin_amounts, params.minReceivedLiquidity);
        } else if (amounts.length == 3) {
            uint256[3] memory coin_amounts = [amounts[0], amounts[1], amounts[2]];
            ICurvePool(pool).add_liquidity(coin_amounts, params.minReceivedLiquidity);
        }
    }

    function depositZap(
        uint256[] calldata amounts,
        IERC20[] calldata tokens,
        address zap,
        CurveLPWithdrawParams calldata params
    ) external payable {}
}
