//SPDX-License-Identifier: UNLICENSED

pragma solidity ^0.8.6;

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
