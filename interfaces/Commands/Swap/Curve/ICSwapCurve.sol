pragma solidity ^0.8.0;

interface ICSwapCurve {
    struct CurveSwapParams {
        address poolAddress;
        uint256 tokenI;
        uint256 tokenJ;
        uint256 swapType;
    }
}
