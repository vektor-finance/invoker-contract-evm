# Will eventually move this file into test_swap

import pytest
from brownie import Contract

from data.chain import get_chain


@pytest.fixture(scope="module")
def curve_pool(token, request, interface, registry):
    dest_token = Contract.from_abi(
        request.param["name"], request.param["address"], interface.IERC20.abi
    )
    address = registry.find_pool_for_coins(token, dest_token)
    if address != "0x0000000000000000000000000000000000000000":
        yield {
            "pool": Contract.from_abi("Curve Pool", address, interface.ISwapTemplateCurve.abi),
            "src_token": token,
            "dest_token": dest_token,
        }
    else:
        pytest.skip(f"Pair does not exist for {token._name} -> {dest_token._name}")


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


def test_buy_with_curve(token, curve_pool):
    print(token, curve_pool)
    pass
