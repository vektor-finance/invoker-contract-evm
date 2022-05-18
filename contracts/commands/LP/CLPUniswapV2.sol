// SPDX-License-Identifier: UNLICENSED

pragma solidity ^0.8.6;

import "./CLPBase.sol";
import "../../../interfaces/Commands/LP/UniswapV2/IUniswapV2Router02.sol";
import "../../../interfaces/Commands/LP/UniswapV2/IUniswapV2Factory.sol";

interface ICLPUniswapV2 {
    struct UniswapV2LPParams {
        address router;
        uint256 amountAMin;
        uint256 amountBMin;
        address receiver;
        uint256 deadline;
    }
}

contract CLPUniswapV2 is CLPBase, ICLPUniswapV2 {
    function _getContractName() internal pure override returns (string memory) {
        return "CLPUniswapV2";
    }

    function deposit(
        uint256 amountA,
        IERC20 tokenA,
        uint256 amountB,
        IERC20 tokenB,
        UniswapV2LPParams calldata params
    ) external payable {
        address receiver = params.receiver == address(0) ? address(this) : params.receiver;
        //solhint-disable-next-line not-rely-on-time
        uint256 deadline = params.deadline == 0 ? block.timestamp + 1 : params.deadline;

        address factory = IUniswapV2Router02(params.router).factory();
        address desiredLP = IUniswapV2Factory(factory).getPair(address(tokenA), address(tokenB));
        uint256 balanceBefore = IERC20(desiredLP).balanceOf(receiver);

        _tokenApprove(tokenA, address(params.router), amountA);
        _tokenApprove(tokenB, address(params.router), amountB);
        IUniswapV2Router02(params.router).addLiquidity(
            address(tokenA),
            address(tokenB),
            amountA,
            amountB,
            params.amountAMin,
            params.amountBMin,
            receiver,
            deadline
        );
        // How do we enforce that this was a valid outcome?
        // Potential security risks: what if somebody passes invalid router?
        // Should we 'check'/enforce receipt of LP token?
        uint256 balanceAfter = IERC20(desiredLP).balanceOf(receiver);
        require(balanceAfter < balanceBefore, "CLPUniswapV2: error receiving LP token");
        // This is perhaps a redundant check, given that the following attack vector exists:
        // Create "exploit" contract and pass this as the router parameter
        // exploit contract looks like this: (vyper)
        /*
            * exploit_contract.vy

            def factory() -> address:
                return self
            def getPair(a: address, b: address) -> address:
                return self.exploit_contract2
            
            * exploit_contract2.vy

            def addLiquidity(tokenA: address, 
                tokenB: address,
                amountADesired: uint256,
                amountBDesired: uint256,
                amountAMin: uint256,
                amountBMin: uint256,
                to: address,
                deadline: uint256
            ) -> (uint256, uint256):
                AAmount: uint256 = ERC20(tokenA).allowance(msg.sender, self)
                ERC20(tokenA).transferFrom(msg.sender, self, AAmount)
                BAmount: uint256 = ERC20(tokenB).allowance(msg.sender, self)
                ERC20(tokenB).transferFrom(msg.sender, self, AAmount)
                self.mint(msg.sender,1)
        */
    }

    function withdraw() external payable {}
}

function addLiquidity(
    address tokenA,
    address tokenB,
    uint256 amountADesired,
    uint256 amountBDesired,
    uint256 amountAMin,
    uint256 amountBMin,
    address to,
    uint256 deadline
) {}

function removeLiquidity(
    address tokenA,
    address tokenB,
    uint256 liquidity,
    uint256 amountAMin,
    uint256 amountBMin,
    address to,
    uint256 deadline
) {}
