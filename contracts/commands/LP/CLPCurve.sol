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
        CurveLPType lpType;
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
        if (params.lpType == CurveLPType.V1_ABI_LIQUIDITY) {
            ICurvePool(pool).add_liquidity(amounts, params.minReceivedLiquidity);
        }
    }

    function depositZap(
        uint256[] calldata amounts,
        IERC20[] calldata tokens,
        address zap,
        CurveLPWithdrawParams calldata params
    ) external payable {}
}
