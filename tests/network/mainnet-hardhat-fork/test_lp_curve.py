import pytest
from brownie import Contract, interface

from data.access_control import APPROVED_COMMAND
from data.chain import get_chain
from data.test_helpers import mint_tokens_for


@pytest.fixture(scope="module")
def clp_curve(invoker, deployer, CLPCurve):
    contract = deployer.deploy(CLPCurve)
    invoker.grantRole(APPROVED_COMMAND, contract, {"from": deployer})  # approve command
    yield contract


def test_deposit(invoker, cmove, alice, clp_curve):
    assets = get_chain()["assets"]
    USDC = [asset for asset in assets if asset["symbol"] == "USDC"][0]
    DAI = [asset for asset in assets if asset["symbol"] == "DAI"][0]
    USDT = [asset for asset in assets if asset["symbol"] == "USDT"][0]

    usdc = Contract.from_abi(USDC["name"], USDC["address"], interface.ERC20Detailed.abi)
    dai = Contract.from_abi(DAI["name"], DAI["address"], interface.ERC20Detailed.abi)
    usdt = Contract.from_abi(USDT["name"], USDT["address"], interface.ERC20Detailed.abi)

    curve_3pool = "0xbebc44782c7db0a1a60cb6fe97d0b483032ff1c7"
    curve_pool = Contract.from_abi("Curve 3pool", curve_3pool, interface.ICurvePool.abi)

    usdc_amount = 100e6
    dai_amount = 100e18
    usdt_amount = 100e6

    usdc.approve(invoker.address, usdc_amount, {"from": alice})
    dai.approve(invoker.address, dai_amount, {"from": alice})
    usdt.approve(invoker.address, usdt_amount, {"from": alice})

    mint_tokens_for(usdc, alice.address)
    mint_tokens_for(dai, alice.address)
    mint_tokens_for(usdt, alice.address)

    calldata_move_usdc = cmove.moveERC20In.encode_input(usdc.address, usdc_amount)
    calldata_move_dai = cmove.moveERC20In.encode_input(dai.address, dai_amount)
    calldata_move_usdt = cmove.moveERC20In.encode_input(usdt.address, usdt_amount)

    # need to specify which function due to function overloading
    expected_amount = curve_pool.calc_token_amount["uint256[3],bool"](
        [dai_amount, usdc_amount, usdt_amount], True
    )
    min_amount = expected_amount // 1.01

    # dai, usdc, usdt
    calldata_deposit = clp_curve.deposit.encode_input(
        [dai_amount, usdc_amount, usdt_amount],
        [dai, usdc, usdt],
        curve_pool,
        [min_amount],
    )

    invoker.invoke(
        [cmove, cmove, cmove, clp_curve],
        [calldata_move_usdc, calldata_move_dai, calldata_move_usdt, calldata_deposit],
        {"from": alice},
    )

    token_3pool = interface.ERC20Detailed("0x6c3f90f043a72fa612cbac8115ee7e52bde6e490")

    assert token_3pool.balanceOf(invoker) >= min_amount


def test_deposit_zap(invoker, cmove, clp_curve, alice):
    assets = get_chain()["assets"]
    USDC = [asset for asset in assets if asset["symbol"] == "USDC"][0]
    USDT = [asset for asset in assets if asset["symbol"] == "USDT"][0]

    usdc = Contract.from_abi(USDC["name"], USDC["address"], interface.ERC20Detailed.abi)
    usdt = Contract.from_abi(USDT["name"], USDT["address"], interface.ERC20Detailed.abi)

    curve_compound = "0xA2B47E3D5c44877cca798226B7B8118F9BFb7A56"
    curve_pool = Contract.from_abi("Compound pool", curve_compound, interface.ICurvePool.abi)
    curve_zap = "0xeB21209ae4C2c9FF2a86ACA31E123764A3B6Bc06"

    usdc_amount = 100e6
    usdt_amount = 100e6

    usdc.approve(invoker.address, usdc_amount, {"from": alice})
    usdt.approve(invoker.address, usdt_amount, {"from": alice})

    mint_tokens_for(usdc, alice.address)
    mint_tokens_for(usdt, alice.address)

    calldata_move_usdc = cmove.moveERC20In.encode_input(usdc.address, usdc_amount)
    calldata_move_usdt = cmove.moveERC20In.encode_input(usdt.address, usdt_amount)

    # need to specify which function due to function overloading
    expected_amount = curve_pool.calc_token_amount["uint256[2],bool"](
        [usdc_amount, usdt_amount], True
    )
    min_amount = expected_amount // 1.01

    # dai, usdc, usdt
    calldata_deposit = clp_curve.depositZap.encode_input(
        [usdc_amount, usdt_amount],
        [usdc, usdt],
        curve_zap,
        [min_amount],
    )

    invoker.invoke(
        [cmove, cmove, cmove, clp_curve],
        [calldata_move_usdc, calldata_move_usdt, calldata_deposit],
        {"from": alice},
    )

    token_compound = interface.ERC20Detailed("0x845838DF265Dcd2c412A1Dc9e959c7d08537f8a2")

    assert token_compound.balanceOf(invoker) >= min_amount
