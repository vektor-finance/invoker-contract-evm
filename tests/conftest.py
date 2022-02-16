"""
conftest for fixtures that are present during ALL tests (core + integrations)
Most fixtures will be generated in subfolders
"""
from pathlib import Path

import pytest
from brownie import Contract, interface
from brownie._config import CONFIG
from brownie.project.main import get_loaded_projects

from data.access_control import APPROVED_COMMAND
from data.anyswap import get_anyswap_native_for_chain, get_anyswap_tokens_for_chain
from data.chain import get_chain_from_network_name, get_chain_name


# User accounts
@pytest.fixture(autouse=True)
def isolation(fn_isolation):
    pass


@pytest.fixture(scope="module")
def deployer(accounts):
    yield accounts[0]


@pytest.fixture(scope="module")
def alice(accounts):
    yield accounts[1]


@pytest.fixture(scope="module")
def bob(accounts):
    yield accounts[2]


# Vektor contracts


@pytest.fixture(scope="module")
def invoker(deployer, Invoker):
    yield deployer.deploy(Invoker)


@pytest.fixture(scope="module")
def cswap(invoker, deployer, CSwap, weth, uni_router):
    contract = deployer.deploy(CSwap, weth.address, uni_router.address)
    invoker.grantRole(APPROVED_COMMAND, contract, {"from": deployer})  # approve command
    yield contract


@pytest.fixture(scope="module")
def cmove(deployer, invoker, CMove):
    contract = deployer.deploy(CMove)
    invoker.grantRole(APPROVED_COMMAND, contract, {"from": deployer})  # approve command
    yield contract


@pytest.fixture(scope="module")
def cbridge(deployer, invoker, CBridge, anyswap_router_v4, any_native_address, weth):
    contract = deployer.deploy(CBridge, weth, any_native_address, anyswap_router_v4.address)
    invoker.grantRole(APPROVED_COMMAND, contract, {"from": deployer})
    yield contract


# Contracts from config file


@pytest.fixture(scope="module")
def uni_router(request):
    router = request.param
    yield Contract.from_abi(
        f"{router['venue']}Router", router["address"], interface.IUniswapV2Router02.abi
    )


@pytest.fixture(scope="module")
def weth(request):
    yield Contract.from_abi("Wrapped Native", request.param["address"], interface.IWETH.abi)


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
        "router": token["router"],
        "underlying": Contract.from_abi(
            token["underlyingName"], token["underlyingAddress"], interface.IERC20.abi
        ),
        "anyToken": Contract.from_abi(
            f"any{token['underlyingName']}", token["anyAddress"], interface.AnyswapV5ERC20.abi
        ),
    }


@pytest.fixture(scope="module")
def anyswap_token_dest_chain(request):
    return request.param


@pytest.fixture(scope="module")
def any_native_address(request):
    return request.param


@pytest.fixture(scope="module")
def tokens_for_alice(request, alice):
    token = request.param
    contract = Contract.from_abi(token["name"], token["address"], interface.ERC20Detailed.abi)
    contract.transfer(alice, 100 * (10 ** token["decimals"]), {"from": token["benefactor"]})
    yield contract


# pytest fixtures/collections

_network = ""
_chain = {}


def pytest_sessionstart():
    global _chain, _network
    _network = CONFIG.settings["networks"]["default"]
    if CONFIG.argv["network"]:
        _network = CONFIG.argv["network"]
    (_chain, _) = get_chain_from_network_name(_network)


def pytest_ignore_collect(path):
    project = get_loaded_projects()[0]
    path = Path(path).relative_to(project._path)

    path_parts = path.parts[1:-1]

    if path.is_dir():
        return None

    # ignore core tests unless you are on 'hardhat' network (dev)
    if path_parts[:1] == ("core",):
        return _network != "hardhat"

    # ignore integration tests if on 'hardhat' network (dev)
    if path_parts[:1] == ("integration",):
        return _network == "hardhat"

    if path_parts[:1] == ("combination",):
        return _network != path_parts[1]


def pytest_generate_tests(metafunc):

    if _chain["id"] == "dev":
        return

    if "token" in metafunc.fixturenames:
        tokens = [asset for asset in _chain["assets"] if asset.get("address")]
        token_names = [token["name"] for token in tokens]
        metafunc.parametrize("token", tokens, ids=token_names, indirect=True)

    if "tokens_for_alice" in metafunc.fixturenames:
        tokens = [asset for asset in _chain["assets"] if asset.get("address")]
        token_names = [token["name"] for token in tokens]
        metafunc.parametrize("tokens_for_alice", tokens, ids=token_names, indirect=True)

    if "uni_router" in metafunc.fixturenames:
        routers = [
            contract
            for contract in _chain["contracts"]
            if "uniswap_router_v2_02" in contract.get("interfaces")
        ]
        router_names = [router["venue"] for router in routers]
        metafunc.parametrize("uni_router", routers, ids=router_names, indirect=True)

    if "weth" in metafunc.fixturenames:
        wrapped_natives = [asset for asset in _chain["assets"] if asset.get("wrapped_native")]
        wrapped_names = [token["name"] for token in wrapped_natives]
        metafunc.parametrize("weth", wrapped_natives, ids=wrapped_names, indirect=True)

    if "anyswap_router_v4" in metafunc.fixturenames:
        routers = [
            contract
            for contract in _chain["contracts"]
            if "anyswap_router_v4" in contract.get("interfaces")
        ]
        router_names = [router["venue"] for router in routers]
        metafunc.parametrize("anyswap_router_v4", routers, ids=router_names, indirect=True)

    if "anyswap_token_v4" in metafunc.fixturenames:
        anyswap_tokens = get_anyswap_tokens_for_chain(_chain["chain_id"])
        if anyswap_tokens is None:
            pytest.skip()
        tokens = [asset for asset in anyswap_tokens if asset.get("anyAddress")]
        token_names = [token["underlyingName"] for token in tokens]
        metafunc.parametrize("anyswap_token_v4", tokens, ids=token_names, indirect=True)

    if "anyswap_token_dest_chain" in metafunc.fixturenames:
        anyswap_tokens = get_anyswap_tokens_for_chain(_chain["chain_id"])
        if anyswap_tokens is None:
            pytest.skip()
        all_dest = []
        for token in anyswap_tokens:
            for chain in token.get("destChains"):
                if chain not in all_dest:
                    all_dest.append(chain)
        metafunc.parametrize(
            "anyswap_token_dest_chain", all_dest, indirect=True, ids=get_chain_name
        )

    if "any_native_address" in metafunc.fixturenames:
        native_address = get_anyswap_native_for_chain(_chain["chain_id"])
        if native_address is None:
            pytest.skip()
        metafunc.parametrize("any_native_address", [native_address], indirect=True)
