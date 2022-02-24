# Will eventually move this file into test_swap

import pytest
from brownie import Contract

from data.access_control import APPROVED_COMMAND
from data.chain import get_chain


@pytest.fixture(scope="module")
def cswap_curve(invoker, deployer, CSwapCurve):
    contract = deployer.deploy(CSwapCurve)
    invoker.grantRole(APPROVED_COMMAND, contract, {"from": deployer})  # approve command
    yield contract


@pytest.fixture(scope="module")
def curve_pool(tokens_for_alice, request, interface, registry):
    dest_token = Contract.from_abi(
        request.param["name"], request.param["address"], interface.IERC20.abi
    )
    address = registry.find_pool_for_coins(tokens_for_alice, dest_token)
    if address != "0x0000000000000000000000000000000000000000":
        yield {
            "pool": Contract.from_abi("Curve Pool", address, interface.CurvePool.abi),
            "src_token": tokens_for_alice,
            "dest_token": dest_token,
        }
    else:
        pytest.skip(f"Pair does not exist for {tokens_for_alice._name} -> {dest_token._name}")


def pytest_generate_tests(metafunc):
    chain = get_chain()

    if "curve_pool" in metafunc.fixturenames:
        tokens = [asset for asset in chain["assets"] if asset.get("address")]
        token_names = [token["name"] for token in tokens]
        metafunc.parametrize("curve_pool", tokens, ids=token_names, indirect=True)


@pytest.fixture(scope="module")
def provider(interface):
    yield Contract.from_abi(
        "Curve Provider", "0x0000000022D53366457F9d5E68Ec105046FC4383", interface.CurveProvider.abi
    )


@pytest.fixture(scope="module")
def registry(provider, interface):
    yield Contract.from_abi("Curve Registry", provider.get_registry(), interface.CurveRegistry.abi)


def test_buy_with_curve(curve_pool, invoker, alice, cswap_curve, cmove, registry):
    # need to unselect unnecssary parametrized tests
    # review https://github.com/pytest-dev/pytest/issues/3730
    pool = curve_pool["pool"]
    src = curve_pool["src_token"]
    dst = curve_pool["dest_token"]
    print(f"{src._name} -> {dst._name}")
    value = 10 ** src.decimals()
    (i, j, underlying) = registry.get_coin_indices(pool, src, dst)
    amount_out = pool.get_dy(i, j, value)

    print(i, j, underlying, amount_out)

    src.approve(invoker, value, {"from": alice})
    calldata_move = cmove.moveERC20In.encode_input(src, value)
    calldata_swap = cswap_curve.swapCurve.encode_input(value, amount_out, [src, dst], pool, i, j)

    invoker.invoke([cmove, cswap_curve], [calldata_move, calldata_swap], {"from": alice})

    assert dst.balanceOf(invoker) >= amount_out
