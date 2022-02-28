# Will eventually move this file into test_swap

import pytest
from brownie import Contract
from brownie.exceptions import VirtualMachineError

from data.access_control import APPROVED_COMMAND
from data.chain import get_chain


@pytest.fixture(scope="module")
def cswap_curve(invoker, deployer, CSwapCurve):
    contract = deployer.deploy(CSwapCurve)
    invoker.grantRole(APPROVED_COMMAND, contract, {"from": deployer})  # approve command
    yield contract


@pytest.fixture(scope="module")
def curve_dest(request, interface):
    dest_token = Contract.from_abi(
        request.param["name"], request.param["address"], interface.IERC20.abi
    )
    yield dest_token


def pytest_generate_tests(metafunc):
    chain = get_chain()

    if "curve_dest" in metafunc.fixturenames:
        tokens = [asset for asset in chain["assets"] if asset.get("address")]
        token_names = [token["name"] for token in tokens]
        metafunc.parametrize("curve_dest", tokens, ids=token_names, indirect=True)


@pytest.fixture(scope="module")
def provider(interface):
    yield Contract.from_abi(
        "Curve Provider", "0x0000000022D53366457F9d5E68Ec105046FC4383", interface.CurveProvider.abi
    )


@pytest.fixture(scope="module")
def registry(provider, interface):
    yield Contract.from_abi("Curve Registry", provider.get_registry(), interface.CurveRegistry.abi)


@pytest.fixture(scope="module")
def swap_registry(provider, interface):
    yield Contract.from_abi(
        "Swap Registry", provider.get_address(2), interface.CurveSwapRegistry.abi
    )


@pytest.fixture(scope="module")
def crypto_registry(provider, interface):
    yield Contract.from_abi(
        "Crypto Registry", provider.get_address(5), interface.CurveCryptoRegistry.abi
    )


def test_buy_with_curve(
    tokens_for_alice,
    curve_dest,
    invoker,
    alice,
    cswap_curve,
    cmove,
    swap_registry,
    crypto_registry,
    interface,
    registry,
):
    # need to unselect unnecssary parametrized tests
    # review https://github.com/pytest-dev/pytest/issues/3730

    value = 10 ** tokens_for_alice.decimals()

    (pool, _) = swap_registry.get_best_rate(tokens_for_alice, curve_dest, value)
    if pool == "0x0000000000000000000000000000000000000000":
        pytest.skip("No route available")

    underlying = False
    is_crypto_pool = False

    try:
        (i, j, underlying) = registry.get_coin_indices(pool, tokens_for_alice, curve_dest)
    except VirtualMachineError:
        (i, j) = crypto_registry.get_coin_indices(pool, tokens_for_alice, curve_dest)
        is_crypto_pool = True
    params = [i, j, 1]

    if is_crypto_pool:
        pool = Contract.from_abi("Curve Crypto Pool", pool, interface.CurveCryptoPool.abi)
    else:
        pool = Contract.from_abi("Curve Pool", pool, interface.CurvePool.abi)

    if underlying:
        amount_out = int(pool.get_dy_underlying(i, j, value) // 1.01)
    else:
        amount_out = int(pool.get_dy(i, j, value) // 1.01)

    params[2] = (is_crypto_pool * 2) + underlying + 1

    tokens_for_alice.approve(invoker, value, {"from": alice})
    calldata_move = cmove.moveERC20In.encode_input(tokens_for_alice, value)
    calldata_swap = cswap_curve.swapCurve.encode_input(
        value, amount_out, [tokens_for_alice, curve_dest], pool, params
    )

    invoker.invoke([cmove, cswap_curve], [calldata_move, calldata_swap], {"from": alice})

    assert curve_dest.balanceOf(invoker) >= amount_out
