# Will eventually move this file into test_swap

import brownie
import pytest
from brownie import Contract

from data.access_control import APPROVED_COMMAND
from data.chain import get_chain
from data.curve import CurveAssetType, get_curve_pools


@pytest.fixture(scope="module")
def cswap_curve(invoker, deployer, CSwapCurve):

    contract = deployer.deploy(CSwapCurve)
    invoker.grantRole(APPROVED_COMMAND, contract, {"from": deployer})  # approve command
    yield contract


@pytest.fixture(scope="module")
def curve_dest(request, interface):
    dest_token = Contract.from_abi(
        request.param["name"], request.param["address"], interface.ERC20Detailed.abi
    )
    yield dest_token


@pytest.fixture(scope="module")
def provider(interface):
    yield Contract.from_abi(
        "Curve Provider", "0x0000000022D53366457F9d5E68Ec105046FC4383", interface.CurveProvider.abi
    )


@pytest.fixture(scope="module")
def registry(provider, interface):
    yield Contract.from_abi("Curve Registry", provider.get_registry(), interface.CurveRegistry.abi)


@pytest.fixture(scope="function")
def curve_pool(request):
    yield request.param


def pytest_generate_tests(metafunc):
    chain = get_chain()

    if "curve_pool" in metafunc.fixturenames:
        pools = get_curve_pools(chain["chain_id"])
        if pools is None:
            pytest.skip("No Curve Pools")
        pool_names = [pool.name for pool in pools]
        metafunc.parametrize("curve_pool", pools, ids=pool_names, indirect=True)
    if "curve_dest" in metafunc.fixturenames:
        tokens = [asset for asset in chain["assets"] if asset.get("address")]
        token_names = [token["name"] for token in tokens]
        metafunc.parametrize("curve_dest", tokens, ids=token_names, indirect=True)


@pytest.mark.only_curve_pool_tokens("tokens_for_alice", "curve_dest")
def test_sell_with_curve(
    curve_pool,
    tokens_for_alice,
    curve_dest,
    invoker,
    alice,
    cswap_curve,
    cmove,
    interface,
    registry,
):

    value = 10 ** tokens_for_alice.decimals()
    underlying = False
    is_crypto_pool = curve_pool.asset_type == CurveAssetType.CRYPTO
    pool = curve_pool.swap_address
    (i, j, underlying) = registry.get_coin_indices(pool, tokens_for_alice, curve_dest)
    params = [pool, i, j, None]

    if is_crypto_pool:
        pool = Contract.from_abi("Curve Crypto Pool", pool, interface.CurveCryptoPool.abi)
    else:
        pool = Contract.from_abi("Curve Pool", pool, interface.CurvePool.abi)

    if underlying:
        amount_out = int(pool.get_dy_underlying(i, j, value) // 1.01)
    else:
        amount_out = int(pool.get_dy(i, j, value) // 1.01)

    params[3] = (is_crypto_pool * 2) + underlying

    tokens_for_alice.approve(invoker, value, {"from": alice})
    calldata_move = cmove.moveERC20In.encode_input(tokens_for_alice, value)
    calldata_swap = cswap_curve.sell.encode_input(
        value, tokens_for_alice, curve_dest, amount_out, params
    )

    invoker.invoke([cmove, cswap_curve], [calldata_move, calldata_swap], {"from": alice})

    assert curve_dest.balanceOf(invoker) >= amount_out


@pytest.mark.only_curve_pool_tokens("tokens_for_alice", "curve_dest")
def test_buy_with_curve(
    curve_pool,
    tokens_for_alice,
    curve_dest,
    invoker,
    alice,
    cswap_curve,
    cmove,
    interface,
    registry,
):

    value = 10 ** tokens_for_alice.decimals()
    underlying = False
    is_crypto_pool = curve_pool.asset_type == CurveAssetType.CRYPTO
    pool = curve_pool.swap_address
    (i, j, underlying) = registry.get_coin_indices(pool, tokens_for_alice, curve_dest)
    params = [pool, i, j, None]

    if is_crypto_pool:
        pool = Contract.from_abi("Curve Crypto Pool", pool, interface.CurveCryptoPool.abi)
    else:
        pool = Contract.from_abi("Curve Pool", pool, interface.CurvePool.abi)

    if underlying:
        amount_out = int(pool.get_dy_underlying(i, j, value) // 1.01)
    else:
        amount_out = int(pool.get_dy(i, j, value) // 1.01)

    params[3] = (is_crypto_pool * 2) + underlying

    tokens_for_alice.approve(invoker, value, {"from": alice})
    calldata_move = cmove.moveERC20In.encode_input(tokens_for_alice, value)

    # These are the same parameters for sell, just changed for buy
    calldata_swap = cswap_curve.buy.encode_input(
        value, tokens_for_alice, curve_dest, amount_out, params
    )

    with brownie.reverts("CSwapCurve:buy not supported"):
        invoker.invoke([cmove, cswap_curve], [calldata_move, calldata_swap], {"from": alice})
