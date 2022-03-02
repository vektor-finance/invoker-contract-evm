// SPDX-License-Identifier: GPL-3.0-or-later
// Vektor SWAP COMMAND (Curve)
pragma solidity ^0.8.6;

import "../../interfaces/Commands/Swap/Curve/ICryptoPool.sol";
import "../../interfaces/Commands/Swap/Curve/ICSwapCurve.sol";
import "../../interfaces/Commands/Swap/Curve/ICurvePool.sol";
import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";

// interfaces necessary for get_input_amount
// if we disable BUY, can remove these
interface IRegistry {
    function get_coin_indices(
        address _pool,
        address _from,
        address _to
    )
        external
        view
        returns (
            int128 i,
            int128 j,
            bool is_underlying
        );

    function get_A(address _pool) external view returns (uint256);

    function get_fees(address _pool) external view returns (uint256[2] memory);

    function get_n_coins(address _pool) external view returns (uint256[2] memory);

    function get_underlying_balances(address _pool) external view returns (uint256[8] memory);

    function get_underlying_decimals(address _pool) external view returns (uint256[8] memory);

    function get_rates(address _pool) external view returns (uint256[8] memory);

    function get_decimals(address _pool) external view returns (uint256[8] memory);

    function get_balances(address _pool) external view returns (uint256[8] memory);
}

interface ICalculator {
    function get_dx(
        int128 n_coins,
        uint256[8] calldata balances,
        uint256 amp,
        uint256 fee,
        uint256[8] calldata rates,
        uint256[8] calldata precisions,
        bool is_underlying,
        int128 i,
        int128 j,
        uint256 dy
    ) external view returns (uint256);
}

contract CSwapCurve is ICSwapCurve {
    using SafeERC20 for IERC20;

    IRegistry public immutable REGISTRY;
    ICalculator public immutable CALCULATOR;

    constructor(IRegistry registry, ICalculator calculator) {
        REGISTRY = registry;
        CALCULATOR = calculator;
    }

    // https://github.com/curvefi/curve-pool-registry/blob/master/contracts/Swaps.vy#L446
    function sell(
        uint256 amountIn,
        uint256 minAmountOut,
        address[2] calldata tokens,
        CurveSwapParams calldata params
    ) external payable {
        IERC20 tokenIn = IERC20(tokens[0]);
        IERC20 tokenOut = IERC20(tokens[1]);
        tokenIn.safeApprove(params.poolAddress, 0);
        tokenIn.safeApprove(params.poolAddress, amountIn);

        uint256 balanceBefore = tokenOut.balanceOf(address(this));

        if (params.swapType == 1) {
            // Stableswap `exchange`
            ICurvePool(params.poolAddress).exchange(
                int128(int256(params.tokenI)),
                int128(int256(params.tokenJ)),
                amountIn,
                0
            );
        } else if (params.swapType == 2) {
            // Stableswap `exchange_underlying`
            ICurvePool(params.poolAddress).exchange_underlying(
                int128(int256(params.tokenI)),
                int128(int256(params.tokenJ)),
                amountIn,
                0
            );
        } else if (params.swapType == 3) {
            // Cryptoswap `exchange`
            ICryptoPool(params.poolAddress).exchange(params.tokenI, params.tokenJ, amountIn, 0);
        } else if (params.swapType == 4) {
            // Cryptoswap `exchange_underlying`
            ICryptoPool(params.poolAddress).exchange_underlying(
                params.tokenI,
                params.tokenJ,
                amountIn,
                0
            );
        } else {
            revert("CSwapCurve: Unknown swapType");
        }

        uint256 balanceAfter = tokenOut.balanceOf(address(this));
        require(balanceAfter >= balanceBefore + minAmountOut, "CSwap: Slippage in");
    }

    // TODO: fix this
    // `inputAmount` should be calculated on-chain
    // currently calculated in python for prototyping
    function buy(
        uint256 amountOut,
        uint256 maxAmountIn,
        address[2] calldata tokens,
        CurveSwapParams calldata params,
        uint256 inputAmount
    ) external payable {
        IERC20 tokenIn = IERC20(tokens[0]);
        IERC20 tokenOut = IERC20(tokens[1]);
        // Add 1 wei as rounding error may reduce amount of tokens received
        // uint256 inputAmount = 1 +
        //     get_input_amount(
        //         params.poolAddress,
        //         amountOut,
        //         GIAParams({
        //             i: int128(int256(params.tokenI)),
        //             j: int128(int256(params.tokenJ)),
        //             is_underlying: params.swapType % 2 == 0
        //         })
        //     );

        require(inputAmount <= maxAmountIn, "CSwap: Slippage out");

        tokenIn.safeApprove(params.poolAddress, 0);
        tokenIn.safeApprove(params.poolAddress, inputAmount);

        uint256 balanceBefore = tokenOut.balanceOf(address(this));

        if (params.swapType == 1) {
            // Stableswap `exchange`
            ICurvePool(params.poolAddress).exchange(
                int128(int256(params.tokenI)),
                int128(int256(params.tokenJ)),
                inputAmount,
                0
            );
        } else if (params.swapType == 2) {
            // Stableswap `exchange_underlying`
            ICurvePool(params.poolAddress).exchange_underlying(
                int128(int256(params.tokenI)),
                int128(int256(params.tokenJ)),
                inputAmount,
                0
            );
        } else if (params.swapType == 3) {
            // Cryptoswap `exchange`
            ICryptoPool(params.poolAddress).exchange(params.tokenI, params.tokenJ, inputAmount, 0);
        } else if (params.swapType == 4) {
            // Cryptoswap `exchange_underlying`
            ICryptoPool(params.poolAddress).exchange_underlying(
                params.tokenI,
                params.tokenJ,
                inputAmount,
                0
            );
        } else {
            revert("CSwapCurve: Unknown swapType");
        }

        // TODO: potentially unnecessary check
        uint256 balanceAfter = tokenOut.balanceOf(address(this));
        require(balanceAfter >= balanceBefore + amountOut, "CSwap: Slippage in");
    }

    // structs needed to prevent stack too deep errors
    struct CalculatorParams {
        uint256 n_coins;
        uint256[8] balances;
        uint256 amp;
        uint256 fee;
        uint256[8] rates;
        uint256[8] decimals;
        int128 i;
        int128 j;
    }

    struct GIAParams {
        int128 i;
        int128 j;
        bool is_underlying;
    }

    // https://etherscan.io/address/0xd1602f68cc7c4c7b59d686243ea35a9c73b0c6a2#code
    // TODO: this should be a 'view' function, but leaving it as a transaction
    // to allow for stack tracing in brownie
    function get_input_amount(
        address pool,
        uint256 amount,
        GIAParams memory params
    ) public returns (uint256) {
        CalculatorParams memory vars;

        vars.amp = REGISTRY.get_A(pool);
        vars.fee = REGISTRY.get_fees(pool)[0];

        vars.n_coins = REGISTRY.get_n_coins(pool)[params.is_underlying ? 1 : 0];
        if (params.is_underlying) {
            vars.balances = REGISTRY.get_underlying_balances(pool);
            vars.decimals = REGISTRY.get_underlying_decimals(pool);
            for (uint256 x = 0; x < 8; x++) {
                if (x == vars.n_coins) {
                    break;
                }
                vars.rates[x] = 10**18;
            }
        } else {
            vars.balances = REGISTRY.get_balances(pool);
            vars.decimals = REGISTRY.get_decimals(pool);
            vars.rates = REGISTRY.get_rates(pool);
        }
        for (uint256 x = 0; x < 8; x++) {
            if (x == vars.n_coins) {
                break;
            }
            vars.decimals[x] = 10**(18 - vars.decimals[x]);
        }

        return
            CALCULATOR.get_dx(
                int128(int256(vars.n_coins)),
                vars.balances,
                vars.amp,
                vars.fee,
                vars.rates,
                vars.decimals,
                params.is_underlying,
                params.i,
                params.j,
                amount
            );
    }

    // need to consider how to handle native eth (alternatively, enforce wrapped eth)
}
