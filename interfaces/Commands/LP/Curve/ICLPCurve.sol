//SPDX-License-Identifier: UNLICENSED

pragma solidity ^0.8.6;

interface ICLPCurve {
    enum CurveLPType {
        PLAIN_POOL,
        PLAIN_POOL_UNDERLYING_FLAG,
        HELPER_CONTRACT_NO_FLAG
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
