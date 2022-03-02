# Will eventually move this file into test_swap

import pytest
from brownie import Contract

from data.access_control import APPROVED_COMMAND
from data.chain import get_chain
from data.curve import CURVE_ASSET_TYPE_CRYPTO, get_curve_pools


@pytest.fixture(scope="module")
def cswap_curve(invoker, deployer, CSwapCurve, provider):
    # Exchanges contract
    # CurveCalculator
    contract = deployer.deploy(
        CSwapCurve, provider.get_registry(), "0xc1DB00a8E5Ef7bfa476395cdbcc98235477cDE4E"
    )
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
        pool_names = [pool.name for pool in pools]
        metafunc.parametrize("curve_pool", pools, ids=pool_names, indirect=True)
    if "curve_dest" in metafunc.fixturenames:
        tokens = [asset for asset in chain["assets"] if asset.get("address")]
        token_names = [token["name"] for token in tokens]
        metafunc.parametrize("curve_dest", tokens, ids=token_names, indirect=True)


"""
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
    target_decimals = curve_dest.decimals()

    value = 10 ** target_decimals
    # underlying = False
    is_crypto_pool = curve_pool.asset_type == CURVE_ASSET_TYPE_CRYPTO
    pool = curve_pool.swap_address
    (i, j, underlying) = registry.get_coin_indices(pool, tokens_for_alice, curve_dest)
    params = [pool, i, j, None]

    if is_crypto_pool:
        pytest.skip()

    if is_crypto_pool:
        pool = Contract.from_abi("Curve Crypto Pool", pool, interface.CurveCryptoPool.abi)
    else:
        pool = Contract.from_abi("Curve Pool", pool, interface.CurvePool.abi)

    # if underlying:
    #     amount_out = int(pool.get_dy_underlying(i, j, value) // 1.01)
    # else:
    #     amount_out = int(pool.get_dy(i, j, value) // 1.01)

    try:
        # amount_in = cswap_curve.get_input_amount(pool, value, (i, j, underlying))
        if underlying:
            amount_in = pool.get_dy_underlying(j, i, value)
        else:
            amount_in = pool.get_dy(j, i, value)
    except VirtualMachineError:
        pytest.skip("cant get amounts")

    nin = amount_in / (10 ** tokens_for_alice.decimals())
    assert nin > 0.95

    params[3] = (is_crypto_pool * 2) + underlying + 1

    bal = tokens_for_alice.balanceOf(alice)
    tokens_for_alice.approve(invoker, bal, {"from": alice})
    calldata_move = cmove.moveERC20In.encode_input(tokens_for_alice, bal)

    input_amount = 1 + amount_in // (1 - pool.fee() / 0.5e10)

    calldata_swap = cswap_curve.buy.encode_input(
        value,
        int(amount_in // 0.99),
        [tokens_for_alice, curve_dest],
        params,
        input_amount,
    )

    invoker.invoke([cmove, cswap_curve], [calldata_move, calldata_swap], {"from": alice})

    print(f"Tried to buy {value / (10 ** target_decimals)} {curve_dest._name} tokens")
    print(f"Received {curve_dest.balanceOf(invoker) / (10 ** target_decimals)}")
    ratio = 100 * curve_dest.balanceOf(invoker) / value
    assert ratio == 100


"""


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
    is_crypto_pool = curve_pool.asset_type == CURVE_ASSET_TYPE_CRYPTO
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

    params[3] = (is_crypto_pool * 2) + underlying + 1

    tokens_for_alice.approve(invoker, value, {"from": alice})
    calldata_move = cmove.moveERC20In.encode_input(tokens_for_alice, value)
    calldata_swap = cswap_curve.sell.encode_input(
        value, amount_out, [tokens_for_alice, curve_dest], params
    )

    invoker.invoke([cmove, cswap_curve], [calldata_move, calldata_swap], {"from": alice})

    assert curve_dest.balanceOf(invoker) >= amount_out
