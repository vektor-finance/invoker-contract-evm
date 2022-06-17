//SPDX-License-Identifier: UNLICENSED

pragma solidity ^0.8.6;

interface ICLPCurve {
    /**
        @notice Used to specify the necessary parameters for a Curve interaction
        @dev Users may either deposit/withdraw 'base' assets or 'underlying' assets into/from a curve pool.
            Some curve pools allow directly depositing 'underlying' assets, whilst other curve pools necessitate
            the usage of a 'helper' contract. 
            In order to accomodate different behaviour between different curve pools, the caller of this contract
            must explicitly state the desired behaviour:

            If depositing/withdrawing 'base' assets, this parameter MUST be BASE and the `curveDepositAddress`/`curveWithdrawAddress` parameter MUST be the address of the curve contract

            If depositing/withdrawing 'underlying assets', check whether the curve contract supports underlying assets:
                If underlying assets are supported, this parameter MUST be UNDERLYING and the `curveDepositAddress`/`curveWithdrawAddress` parameter MUST be the address of the curve contract
                If underlying assets are not supported, this parameter MUST be CONTRACT and the `curveDepositAddress`/`curveWithdrawAddress` parameter MUST be the address of the helper 'Deposit.vy' contract.

        @param BASE The user is interacting directly with the curve contract and depositing base assets.
        @param UNDERLYING The user is interacting directly with the curve contract and depositing underlying assets.
        @param HELPER The user is interacting with a curve `Deposit.vy` contract, and depositing underlying assets.
    */
    enum CurveLPType {
        BASE,
        UNDERLYING,
        HELPER
    }

    struct CurveLPDepositParams {
        uint256 minReceivedLiquidity;
        CurveLPType lpType;
        address curveDepositAddress;
    }
    struct CurveLPWithdrawParams {
        uint256[] minimumReceived;
        CurveLPType lpType;
        address curveWithdrawAddress;
    }
}
