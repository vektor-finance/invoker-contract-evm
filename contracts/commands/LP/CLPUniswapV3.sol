// SPDX-License-Identifier: Unlicensed
pragma solidity ^0.8.6;

import "./CLPBase.sol";

interface IUniswapV3Pool {
    function factory() external view returns (address);

    function token0() external view returns (address);

    function token1() external view returns (address);

    function fee() external view returns (uint24);
}

interface INonfungiblePositionManager {
    struct IncreaseLiquidityParams {
        uint256 tokenId;
        uint256 amount0Desired;
        uint256 amount1Desired;
        uint256 amount0Min;
        uint256 amount1Min;
        uint256 deadline;
    }
    struct MintParams {
        address token0;
        address token1;
        uint24 fee;
        int24 tickLower;
        int24 tickUpper;
        uint256 amount0Desired;
        uint256 amount1Desired;
        uint256 amount0Min;
        uint256 amount1Min;
        address recipient;
        uint256 deadline;
    }

    function mint(MintParams calldata params)
        external
        payable
        returns (
            uint256 tokenId,
            uint128 liquidity,
            uint256 amount0,
            uint256 amount1
        );
}

interface ICLPUniswapV3 {
    struct UniswapV3LPDepositParams {
        address router;
        uint256 amountAMin;
        uint256 amountBMin;
        address receiver;
        uint256 deadline;
    }
}

contract CLPUniswapV3 is CLPBase, ICLPUniswapV3 {
    function _getContractName() internal pure override returns (string memory) {
        return "CLPUniswapV3";
    }

    function deposit(
        uint256 tokenId,
        uint256 amountA,
        uint256 amountB,
        UniswapV3LPDepositParams calldata params
    ) external payable {}

    function depositNew(
        IUniswapV3Pool pool,
        int24 tickLower,
        int24 tickUpper,
        uint256 amountA,
        uint256 amountB,
        UniswapV3LPDepositParams calldata params
    ) external payable {
        _approveToken(IERC20(pool.token0()), params.router, amountA);
        _approveToken(IERC20(pool.token1()), params.router, amountB);

        // receiver needs to be able to receive NFT
        INonfungiblePositionManager(params.router).mint(
            INonfungiblePositionManager.MintParams({
                token0: pool.token0(), //todo: check if these use SLOAD
                token1: pool.token1(), //todo: check if these use SLOAD
                fee: pool.fee(), //todo: check if these use SLOAD
                tickLower: tickLower,
                tickUpper: tickUpper,
                amount0Desired: amountA,
                amount1Desired: amountB,
                amount0Min: params.amountAMin,
                amount1Min: params.amountBMin,
                recipient: params.receiver,
                deadline: params.deadline
            })
        );
    }
}
