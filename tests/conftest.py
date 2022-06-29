"""
conftest for fixtures that are present during ALL tests (core + integrations)
Most fixtures will be generated in subfolders
"""
from pathlib import Path
from typing import Set

import pytest
from brownie import Contract, interface
from brownie.exceptions import VirtualMachineError
from brownie.project.main import get_loaded_projects
from eth_account import Account
from eth_account.messages import encode_structured_data

from data.anyswap import get_anyswap_tokens_for_chain
from data.chain import get_chain, get_chain_name, get_network, get_wnative_address
from data.curve import CurvePool
from data.test_helpers import BenefactorError

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
    yield Contract.from_abi(token["name"], token["address"], interface.ERC20Detailed.abi)


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
    contract.transfer(alice, 10 * (10 ** token["decimals"]), {"from": token["benefactor"]})
    yield contract


# pytest fixtures/collections


def is_list_unique(_list):
    return len(set(_list)) == len(_list)


def pytest_collection_modifyitems(items):
    for item in items.copy():
        try:
            params = item.callspec.params
        except Exception:
            continue

        for marker in item.iter_markers(name="only_curve_pool_tokens"):
            tokens = [params[x]["address"] for x in marker.args]
            if not is_list_unique(tokens):
                items.remove(item)
                continue
            pool_coins = params["curve_pool"].coins
            if not all(token in pool_coins for token in tokens):
                items.remove(item)

        for marker in item.iter_markers(name="dedupe"):
            tokens = [params[x]["address"] for x in marker.args]
            if not is_list_unique(tokens):
                items.remove(item)


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

    if path_parts[:1] == ("network",):
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
                if token["underlyingAddress"].lower() in a["address"].lower():
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


@pytest.fixture
def sign_eip2612_permit():
    def sign_eip2612_permit(
        token: Contract,
        owner: Account,  # NOTE: Must be a eth_key account, not Brownie
        spender: str,
        allowance: int = 2**256 - 1,  # Allowance to set with `permit`
        deadline: int = 0,  # 0 means no time limit
        override_nonce: int = None,
    ):
        name = "Uniswap V2"
        version = "1"
        chain_id = 1

        if override_nonce:
            nonce = override_nonce
        else:
            nonce = token.nonces(owner.address)
        data = {
            "types": {
                "EIP712Domain": [
                    {"name": "name", "type": "string"},
                    {"name": "version", "type": "string"},
                    {"name": "chainId", "type": "uint256"},
                    {"name": "verifyingContract", "type": "address"},
                ],
                "Permit": [
                    {"name": "owner", "type": "address"},
                    {"name": "spender", "type": "address"},
                    {"name": "value", "type": "uint256"},
                    {"name": "nonce", "type": "uint256"},
                    {"name": "deadline", "type": "uint256"},
                ],
            },
            "domain": {
                "name": name,
                "version": version,
                "chainId": chain_id,
                "verifyingContract": str(token),
            },
            "primaryType": "Permit",
            "message": {
                "owner": owner.address,
                "spender": spender,
                "value": allowance,
                "nonce": nonce,
                "deadline": deadline,
            },
        }
        permit = encode_structured_data(data)
        return owner.sign_message(permit).signature

    return sign_eip2612_permit


bad_token_pools: Set[CurvePool] = set()
bad_pools: Set[CurvePool] = set()


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    result = outcome.get_result()
    if result.nodeid.split("::")[0] == "tests/integration/commands/test_swap_curve.py":
        if result.when == "call" and result.failed:
            if "pool" in item.fixturenames:
                pool = item.funcargs["pool"]
                exc_info = call.excinfo
                if exc_info.errisinstance(AssertionError) or exc_info.errisinstance(
                    VirtualMachineError
                ):
                    bad_pools.add(pool)
                if exc_info.errisinstance(BenefactorError):
                    bad_token_pools.add(pool)


@pytest.hookimpl(hookwrapper=True)
def pytest_terminal_summary(terminalreporter, exitstatus: int, config):
    yield
    terminalreporter.section("Custom Errors")
    if len(bad_token_pools) > 0:
        terminalreporter.write("---BAD TOKEN POOLS---\n")
        terminalreporter.write(f"{[pool.pool_address for pool in bad_token_pools]}")
        terminalreporter.ensure_newline()
    if len(bad_pools) > 0:
        terminalreporter.write("---BAD POOLS---\n")
        terminalreporter.write(f"{[pool.pool_address for pool in bad_pools]}")
