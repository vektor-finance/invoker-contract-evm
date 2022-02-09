"""
conftest for fixtures that are present during ALL tests (core + integrations)
Most fixtures will be generated in subfolders
"""
from pathlib import Path

import pytest
from brownie._config import CONFIG
from brownie.project.main import get_loaded_projects

from data.access_control import APPROVED_COMMAND
from data.chain import get_chain_from_network_name


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


@pytest.fixture(scope="module", autouse=True)
def invoker(deployer, Invoker, cmove, cswap):
    contract = deployer.deploy(Invoker)
    contract.grantRole(APPROVED_COMMAND, cswap.address, {"from": deployer})
    yield contract


@pytest.fixture(scope="module", autouse=True)
def cswap(invoker, deployer, CSwap, weth, uni_router):
    contract = deployer.deploy(CSwap, weth.address, uni_router.address)
    invoker.grantRole(APPROVED_COMMAND, contract, {"from": deployer})  # approve commands
    yield contract


@pytest.fixture(scope="module", autouse=True)
def cmove(deployer, CMove):
    yield deployer.deploy(CMove)


# Integrations

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
    if path_parts[:1] == ("integrations",):
        return _network == "hardhat"

    if path_parts[:1] == ("combinations",):
        return _network != path_parts[1]


def pytest_generate_tests(metafunc):

    if _chain["id"] == "dev":
        return

    if "token" in metafunc.fixturenames:
        tokens = [asset for asset in _chain["assets"] if asset.get("address")]
        token_names = [token["name"] for token in tokens]
        metafunc.parametrize("token", tokens, ids=token_names, indirect=True)

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
