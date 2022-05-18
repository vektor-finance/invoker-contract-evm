import pytest
from brownie import Contract, interface

from data.access_control import APPROVED_COMMAND
from data.chain import get_chain
from data.test_helpers import mint_tokens_for


@pytest.fixture(scope="module")
def clp(invoker, deployer, CLPUniswapV2):
    contract = deployer.deploy(CLPUniswapV2)
    invoker.grantRole(APPROVED_COMMAND, contract, {"from": deployer})  # approve command
    yield contract


def test_deposit(invoker, cmove, alice, clp, uni_router):
    assets = get_chain()["assets"]
    WETH = [asset for asset in assets if asset["symbol"] == "WETH"][0]
    USDC = [asset for asset in assets if asset["symbol"] == "USDC"][0]
    weth = Contract.from_abi(WETH["name"], WETH["address"], interface.ERC20Detailed.abi)
    usdc = Contract.from_abi(USDC["name"], USDC["address"], interface.ERC20Detailed.abi)

    weth_amount = 1e18
    usdc_amount = 2041e6

    slippage = 0.50  # 50%

    min_weth_amount = weth_amount * (1 - slippage)
    min_usdc_amount = usdc_amount * (1 - slippage)

    # do approvals
    weth.approve(invoker.address, weth_amount, {"from": alice})
    usdc.approve(invoker.address, usdc_amount, {"from": alice})

    # Mint tokens for user
    mint_tokens_for(weth, alice.address)
    mint_tokens_for(usdc, alice.address)

    # build invoker command
    calldata_move_weth = cmove.moveERC20In.encode_input(weth.address, weth_amount)
    calldata_move_usdc = cmove.moveERC20In.encode_input(usdc.address, usdc_amount)
    calldata_deposit = clp.deposit.encode_input(
        weth_amount,
        weth,
        usdc_amount,
        usdc,
        (uni_router, min_weth_amount, min_usdc_amount, alice, 0),
    )

    if uni_router._name == "uniswap router":
        lp_address = "0xB4e16d0168e52d35CaCD2c6185b44281Ec28C9Dc"
    elif uni_router._name == "sushiswap router":
        lp_address = "0x397ff1542f962076d0bfe58ea045ffa2d347aca0"
    lp_token = Contract.from_abi(
        "WETH-USDC LP Token",
        lp_address,
        interface.ERC20Detailed.abi,
    )

    assert lp_token.balanceOf(alice) == 0

    invoker.invoke(
        [cmove, cmove, clp],
        [calldata_move_weth, calldata_move_usdc, calldata_deposit],
        {"from": alice},
    )

    assert lp_token.balanceOf(alice) >= 1
