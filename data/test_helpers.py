import binascii
import pickle
from contextlib import contextmanager
from functools import wraps

import brownie
from brownie import interface, network, web3
from eth_abi import encode_single
from eth_utils import keccak


@contextmanager
def isolate_fixture():
    brownie.chain.snapshot()
    try:
        yield
    finally:
        brownie.chain.revert()


class DisableTrace(object):
    def __init__(self, web3) -> None:
        self.web3 = web3
        self.initial_traces = web3._supports_traces

    def __enter__(self):
        self.web3._supports_traces = False

    def __exit__(self, type, value, traceback):
        self.web3._supports_traces = self.initial_traces


def cached(func):
    try:
        with open("data/balances_cache.pkl", "rb") as infile:
            func.cache = pickle.load(infile)
    except FileNotFoundError:
        func.cache = {}

    @wraps(func)
    def wrapper(*args):
        try:
            return func.cache[args]
        except KeyError:
            func.cache[args] = result = func(*args)
            with open("data/balances_cache.pkl", "wb") as outfile:
                pickle.dump(func.cache, outfile)
            return result

    return wrapper


def bytes32(i):
    return binascii.unhexlify("%064x" % i)


def get_storage_key(address, storage_slot):
    user = int(address, 16)
    key = bytes32(user) + bytes32(storage_slot)
    return "0x" + keccak(key).hex()


@cached
def get_balance_slot(token, network):
    user = "0x1234567890123456789012345678901234567890"
    token = interface.ERC20Detailed(token)

    trace = token.balanceOf.transact(user, {"from": user}).trace
    sha_opcode = [t for t in trace if t["op"] == "SHA3"][-1]

    word_offset = int(sha_opcode["stack"][-1], 16) // 32
    assert (
        sha_opcode["stack"][-2]
        == "0000000000000000000000000000000000000000000000000000000000000040"
    )

    balances_slot = int("0x" + sha_opcode["memory"][word_offset], 16)

    return balances_slot


ETH = ["0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE", "0xeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee"]


def mint_tokens_for(token, user, amount=0):
    if hasattr(user, "address"):
        user = user.address

    if token in ETH:
        if amount == 0:
            encoded_value = "0x" + encode_single("uint256", int(1e18)).hex()
        else:
            encoded_value = "0x" + encode_single("uint256", amount).hex()
        web3.provider.make_request("hardhat_setBalance", [user, encoded_value])
        return amount

    token = interface.ERC20Detailed(token)
    active_network = network.show_active()
    if amount == 0:
        amount = 10 ** token.decimals()

    balance_slot = get_balance_slot(token.address, active_network)
    user_slot = get_storage_key(user, balance_slot)
    encoded_value = "0x" + encode_single("uint256", amount).hex()
    web3.provider.make_request("hardhat_setStorageAt", [token.address, user_slot, encoded_value])

    return amount
