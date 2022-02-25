"""
conftest for fixtures that are present during ALL tests (core + integrations)
Most fixtures will be generated in subfolders
"""
from pathlib import Path

import pytest
from brownie import Contract, interface
from brownie.project.main import get_loaded_projects

from data.anyswap import get_anyswap_tokens_for_chain
from data.chain import get_chain, get_chain_name, get_network, get_wnative_address

pytest_plugins = ["fixtures.accounts", "fixtures.vektor", "fixtures.chain"]


@pytest.fixture(autouse=True)
def isolation(fn_isolation):
    pass


# Contracts from config file

UNISWAP_ROUTER_V2_ABI = {"43114": interface.JoeRouterV2.abi}

DEFAULT_UNISWAP_ROUTER_V2_ABI = interface.IUniswapV2Router02.abi


@pytest.fixture(scope="module")
def uni_router(request, connected_chain):
    router = request.param
    chain_id = str(connected_chain["chain_id"])
    abi = UNISWAP_ROUTER_V2_ABI.get(chain_id, DEFAULT_UNISWAP_ROUTER_V2_ABI)
    yield Contract.from_abi(f"{router['venue']} router", router["address"], abi)


@pytest.fixture(scope="module")
def wnative(connected_chain):
    address = get_wnative_address(connected_chain)
    yield Contract.from_abi("Wrapped Native", address, interface.IWETH.abi)


@pytest.fixture(scope="module")
def token(request):
    token = request.param
    yield Contract.from_abi(token["name"], token["address"], interface.IERC20.abi)


@pytest.fixture(scope="module")
def anyswap_router_v4(request):
    router = request.param
    yield Contract.from_abi(
        f"{router['venue']} router", router["address"], interface.AnyswapV4Router.abi
    )


@pytest.fixture(scope="module")
def anyswap_token_v4(request):
    token = request.param
    yield {
        "router": Contract.from_abi(
            "AnyswapRouter", token["router"], interface.AnyswapV4Router.abi
        ),
        "underlying": Contract.from_abi(
            token["underlyingName"], token["underlyingAddress"], interface.IERC20.abi
        ),
        "anyToken": Contract.from_abi(
            f"any{token['underlyingName']}", token["anyAddress"], interface.AnyswapV5ERC20.abi
        ),
    }


@pytest.fixture(scope="module")
def mint_anyswap_token_v4(alice, request):
    token = request.param
    underlying = Contract.from_abi(
        token["underlyingName"], token["underlyingAddress"], interface.IERC20.abi
    )
    underlying.transfer(alice, 10 * (10 ** token["decimals"]), {"from": token["benefactor"]})
    yield {
        "router": Contract.from_abi(
            "AnyswapRouter", token["router"], interface.AnyswapV4Router.abi
        ),
        "underlying": underlying,
        "anyToken": Contract.from_abi(
            f"any{token['underlyingName']}", token["anyAddress"], interface.AnyswapV5ERC20.abi
        ),
    }


@pytest.fixture(scope="module")
def anyswap_token_dest_chain(request):
    return request.param


@pytest.fixture(scope="module")
def any_native_token(request):
    token = request.param
    yield {
        "address": token["anyAddress"],
        "token": Contract.from_abi(
            f"any{token['underlyingName']}",
            token["anyAddress"],
            interface.AnyswapV5ERC20.abi,
        ),
        "router": Contract.from_abi(
            "AnyswapRouter", token["router"], interface.AnyswapV4Router.abi
        ),
    }
    return request.param["anyAddress"]


@pytest.fixture(scope="module")
def tokens_for_alice(request, alice):
    token = request.param
    contract = Contract.from_abi(token["name"], token["address"], interface.ERC20Detailed.abi)
    contract.transfer(alice, 100 * (10 ** token["decimals"]), {"from": token["benefactor"]})
    yield contract


# pytest fixtures/collections


def pytest_ignore_collect(path):
    project = get_loaded_projects()[0]
    path = Path(path).relative_to(project._path)

    path_parts = path.parts[1:-1]

    if path.is_dir():
        return None

    network = get_network()

    # ignore core tests unless you are on 'hardhat' network (dev)
    if path_parts[:1] == ("core",):
        return network != "hardhat"

    # ignore integration tests if on 'hardhat' network (dev)
    if path_parts[:1] == ("integration",):
        return network == "hardhat"

    if path_parts[:1] == ("combination",):
        return network != path_parts[1]


def pytest_generate_tests(metafunc):

    chain = get_chain()

    if chain["id"] == "dev":
        return

    if "token" in metafunc.fixturenames:
        tokens = [asset for asset in chain["assets"] if asset.get("address")]
        token_names = [token["name"] for token in tokens]
        metafunc.parametrize("token", tokens, ids=token_names, indirect=True)

    if "tokens_for_alice" in metafunc.fixturenames:
        tokens = [asset for asset in chain["assets"] if asset.get("address")]
        token_names = [token["name"] for token in tokens]
        metafunc.parametrize("tokens_for_alice", tokens, ids=token_names, indirect=True)

    if "uni_router" in metafunc.fixturenames:
        routers = [
            contract
            for contract in chain["contracts"]
            if "uniswap_router_v2_02" in contract.get("interfaces")
        ]
        router_names = [router["venue"] for router in routers]
        metafunc.parametrize("uni_router", routers, ids=router_names, indirect=True)

    if "anyswap_router_v4" in metafunc.fixturenames:
        routers = [
            contract
            for contract in chain["contracts"]
            if "anyswap_router_v4" in contract.get("interfaces")
        ]
        router_names = [router["venue"] for router in routers]
        metafunc.parametrize("anyswap_router_v4", routers, ids=router_names, indirect=True)

    if "anyswap_token_v4" in metafunc.fixturenames:
        anyswap_tokens = get_anyswap_tokens_for_chain(chain)
        if anyswap_tokens is None:
            pytest.skip("No native token to bridge")
        tokens = [asset for asset in anyswap_tokens if asset.get("anyAddress")]
        token_names = [token["underlyingName"] for token in tokens]
        metafunc.parametrize("anyswap_token_v4", tokens, ids=token_names, indirect=True)

    if "mint_anyswap_token_v4" in metafunc.fixturenames:
        anyswap_tokens = get_anyswap_tokens_for_chain(chain)
        if anyswap_tokens is None:
            pytest.skip("No native token to bridge")
        any_tokens = [asset for asset in anyswap_tokens if asset.get("anyAddress")]
        all_tokens = [asset for asset in chain["assets"] if asset.get("address")]
        for token in any_tokens:
            for a in all_tokens:
                if token["underlyingAddress"] in a["address"]:
                    token["benefactor"] = a["benefactor"]
                    token["decimals"] = a["decimals"]
        token_names = [token["underlyingName"] for token in any_tokens]
        metafunc.parametrize("mint_anyswap_token_v4", any_tokens, ids=token_names, indirect=True)

    if "anyswap_token_dest_chain" in metafunc.fixturenames:
        anyswap_tokens = get_anyswap_tokens_for_chain(chain)
        if anyswap_tokens is None:
            pytest.skip("No anyswap tokens specified")
        all_dest = []
        for token in anyswap_tokens:
            for dest_chain in token.get("destChains"):
                if dest_chain not in all_dest:
                    all_dest.append(dest_chain)
        metafunc.parametrize(
            "anyswap_token_dest_chain", all_dest, indirect=True, ids=get_chain_name
        )

    if "any_native_token" in metafunc.fixturenames:
        wrapped_native = get_wnative_address(chain)
        anyswap_tokens = get_anyswap_tokens_for_chain(chain)
        any_native = [
            token for token in anyswap_tokens if token["underlyingAddress"] == wrapped_native
        ]
        native_names = [token["underlyingName"] for token in any_native]
        if any_native is []:
            pytest.skip("Cannot bridge native token using anyswap")
        metafunc.parametrize("any_native_token", any_native, ids=native_names, indirect=True)
