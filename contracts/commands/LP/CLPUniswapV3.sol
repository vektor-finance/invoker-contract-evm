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
    function approve(address to, uint256 tokenId) external;

    function ownerOf(uint256 tokenId) external returns (address);

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

    struct DecreaseLiquidityParams {
        uint256 tokenId;
        uint128 liquidity;
        uint256 amount0Min;
        uint256 amount1Min;
        uint256 deadline;
    }

    struct CollectParams {
        uint256 tokenId;
        address recipient;
        uint128 amount0Max;
        uint128 amount1Max;
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

    function positions(uint256 tokenId)
        external
        view
        returns (
            uint96 nonce,
            address operator,
            address token0,
            address token1,
            uint24 fee,
            int24 tickLower,
            int24 tickUpper,
            uint128 liquidity,
            uint256 feeGrowthInside0LastX128,
            uint256 feeGrowthInside1LastX128,
            uint128 tokensOwed0,
            uint128 tokensOwed1
        );

    function increaseLiquidity(IncreaseLiquidityParams calldata params)
        external
        payable
        returns (
            uint128 liquidity,
            uint256 amount0,
            uint256 amount1
        );

    function decreaseLiquidity(DecreaseLiquidityParams calldata params)
        external
        payable
        returns (uint256 amount0, uint256 amount1);

    function collect(CollectParams calldata params)
        external
        payable
        returns (uint256 amount0, uint256 amount1);

    function burn(uint256 tokenId) external payable;
}

interface ICLPUniswapV3 {
    struct UniswapV3LPDepositParams {
        address router;
        uint256 amountAMin;
        uint256 amountBMin;
        address receiver;
        uint256 deadline;
    }
    struct UniswapV3LPWithdrawParams {
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

    /**
        @dev PositionManager ensures NFT not minted to zero address
     **/
    function deposit(
        uint256 tokenId,
        uint256 amountA,
        uint256 amountB,
        UniswapV3LPDepositParams calldata params
    ) external payable {
        (
            ,
            ,
            address token0,
            address token1,
            uint24 fee,
            ,
            ,
            ,
            ,
            ,
            ,

        ) = INonfungiblePositionManager(params.router).positions(tokenId);

        _approveToken(IERC20(token0), params.router, amountA);
        _approveToken(IERC20(token1), params.router, amountB);

        INonfungiblePositionManager(params.router).increaseLiquidity(
            INonfungiblePositionManager.IncreaseLiquidityParams(
                tokenId,
                amountA,
                amountB,
                params.amountAMin,
                params.amountBMin,
                params.deadline
            )
        );
    }

    /**
        @dev PositionManager ensures NFT not minted to zero address
     **/
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

    function withdraw(
        uint256 tokenId,
        uint128 liquidity,
        UniswapV3LPWithdrawParams calldata params
    ) external payable {
        _requireMsg(
            INonfungiblePositionManager(params.router).ownerOf(tokenId) == msg.sender,
            "not your position"
        );
        INonfungiblePositionManager(params.router).decreaseLiquidity(
            INonfungiblePositionManager.DecreaseLiquidityParams({
                tokenId: tokenId,
                liquidity: liquidity,
                amount0Min: params.amountAMin,
                amount1Min: params.amountBMin,
                deadline: params.deadline
            })
        );
        INonfungiblePositionManager(params.router).collect(
            INonfungiblePositionManager.CollectParams({
                tokenId: tokenId,
                recipient: params.receiver,
                amount0Max: type(uint128).max,
                amount1Max: type(uint128).max
            })
        );
    }

    function withdrawAll(uint256 tokenId, UniswapV3LPWithdrawParams calldata params)
        external
        payable
    {
        _requireMsg(
            INonfungiblePositionManager(params.router).ownerOf(tokenId) == msg.sender,
            "not your position"
        );
        (, , , , , , , uint128 liquidity, , , , ) = INonfungiblePositionManager(params.router)
            .positions(tokenId);

        INonfungiblePositionManager(params.router).decreaseLiquidity(
            INonfungiblePositionManager.DecreaseLiquidityParams({
                tokenId: tokenId,
                liquidity: liquidity,
                amount0Min: params.amountAMin,
                amount1Min: params.amountBMin,
                deadline: params.deadline
            })
        );

        INonfungiblePositionManager(params.router).collect(
            INonfungiblePositionManager.CollectParams({
                tokenId: tokenId,
                recipient: params.receiver,
                amount0Max: type(uint128).max,
                amount1Max: type(uint128).max
            })
        );

        INonfungiblePositionManager(params.router).burn(tokenId);
    }
}
