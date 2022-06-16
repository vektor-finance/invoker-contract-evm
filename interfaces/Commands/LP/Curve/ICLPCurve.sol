//SPDX-License-Identifier: UNLICENSED

pragma solidity ^0.8.6;

interface ICLPCurve {
    enum CurveLPType {
        CURVE_POOL,
        CURVE_POOL_UNDERLYING,
        HELPER_CONTRACT
    }

    struct CurveLPDepositParams {
        uint256 minReceivedLiquidity;
        CurveLPType lpType;
    }
    struct CurveLPWithdrawParams {
        uint256[] minimumReceived;
        CurveLPType lpType;
        address curveWithdrawAddress;
    }
}
