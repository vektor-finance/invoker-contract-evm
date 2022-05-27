import pytest
from brownie import interface

from data.access_control import APPROVED_COMMAND
from data.test_helpers import mint_tokens_for


@pytest.fixture(scope="module")
def clp_uniswapv3(invoker, deployer, CLPUniswapV3):
    contract = deployer.deploy(CLPUniswapV3)
    invoker.grantRole(APPROVED_COMMAND, contract, {"from": deployer})  # approve command
    yield contract


def test_mint(invoker, clp_uniswapv3, alice, cmove, chain):
    nftm = interface.NonfungiblePositionManager("0xc36442b4a4522e871399cd717abdd847ab11fe88")

    tick_lower = 0
    tick_upper = 6000

    # WETH-USDC 0.3%
    uniswap_pool = interface.IUniswapV3Pool("0x8ad599c3A0ff1De082011EFDDc58f1908eb6e6D8")

    usdc = interface.ERC20Detailed("0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48")
    weth = interface.ERC20Detailed("0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2")

    mint_tokens_for(usdc, alice)
    mint_tokens_for(weth, alice)

    usdc_amount = 100e6
    weth_amount = 0.05e18

    usdc.approve(invoker, usdc_amount, {"from": alice})
    weth.approve(invoker, weth_amount, {"from": alice})

    calldata_move_usdc = cmove.moveERC20In.encode_input(usdc, usdc_amount)
    calldata_move_weth = cmove.moveERC20In.encode_input(weth, weth_amount)

    calldata_deposit = clp_uniswapv3.depositNew.encode_input(
        uniswap_pool,
        tick_lower,
        tick_upper,
        usdc_amount,
        weth_amount,
        (nftm, 0, 0, alice, chain.time() + 100),
    )

    tx = invoker.invoke(
        [cmove, cmove, clp_uniswapv3],
        [calldata_move_usdc, calldata_move_weth, calldata_deposit],
        {"from": alice},
    )

    assert "IncreaseLiquidity" in tx.events
    token_id = tx.events["IncreaseLiquidity"]["tokenId"]

    position = nftm.positions(token_id).dict()
    assert position["token0"] == usdc
    assert position["token1"] == weth
    assert position["fee"] == 3000
    assert position["tickLower"] == tick_lower
    assert position["tickUpper"] == tick_upper

    assert nftm.ownerOf(token_id) == alice
