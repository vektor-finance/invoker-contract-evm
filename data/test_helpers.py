import binascii
import pickle
from contextlib import contextmanager
from enum import Enum
from functools import wraps

import brownie
from brownie import interface, web3
from eth_abi import encode_single
from eth_utils import keccak

from data.chain import get_chain_id


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


def get_balance_slot(token, network):
    user = "0x1234567890123456789012345678901234567890"
    token = interface.ERC20Detailed(token)

    tx = token.balanceOf.transact(user, {"from": user})
    trace = tx.trace
    sha_opcode = [t for t in trace if t["op"] == "SHA3"][-1]

    word_offset = int(sha_opcode["stack"][-1], 16) // 32
    assert (
        sha_opcode["stack"][-2]
        == "0000000000000000000000000000000000000000000000000000000000000040"
    )
    balances_slot = int("0x" + sha_opcode["memory"][word_offset + 1], 16)

    storage_address = sha_opcode["address"]

    for subcall in tx.subcalls[::-1]:
        if subcall["op"] == "DELEGATECALL":
            storage_address = subcall["from"]
        else:
            break

    return storage_address, balances_slot


class MintStrategy(Enum):
    NATIVE = 0
    BALANCES = 1
    BENEFACTOR = 2


BENEFACTORS = {
    "1": {
        "0x028171bca77440897b824ca71d1c56cac55b68a3": "0x0d33c811d0fcc711bcb388dfb3a152de445be66f",
        "0xbcca60bb61934080951369a648fb03df4f96263c": "0xbe67bb1aa7bacfc5d40d963d47e11e3d382a56bd",
        "0x3ed3b47dd13ec9a98b44e6204a523e766b225811": "0x87d48c565d0d85770406d248efd7dc3cbd41e729",
        "0x6c5024cd4f8a59110119c56f8933403a539555eb": "0xa2a3cae63476891ab2d640d9a5a800755ee79d6e",
        "0xae7ab96520de3a18e5e111b5eaab095312d7fe84": "0x7f39c581f595b53c5cb19bd0b3f8da6c935e2ca0",
        "0x6c3f90f043a72fa612cbac8115ee7e52bde6e490": "0xbfcf63294ad7105dea65aa58f8ae5be2d9d0952a",
        "0xd533a949740bb3306d119cc777fa900ba034cd52": "0x5f3b5dfeb7b28cdbd7faba78963ee202a494e2a2",
        "0xc4ad29ba4b3c580e6d59105fff484999997675ff": "0xdefd8fdd20e0f34115c7018ccfb655796f6b2168",
        "0x075b1bb99792c9e1041ba13afef80c91a1e70fb3": "0x13c1542a468319688b89e323fe9a3be3a90ebb27",
        "0x674c6ad92fd080e4004b2312b45f796a192d27a0": "0x868d94b174bed780717cf62e7ed31653638d5948",
        "0x9d409a0a012cfba9b15f6d4b36ac57a46966ab9a": "0x66ca70f1a348bdc66bb201e09eae4009d1d1e7e8",
        "0x8751d4196027d4e6da63716fa7786b5174f04c15": "0x042b32ac6b453485e357938bdc38e0340d4b9276",
        "0x683923db55fead99a79fa01a27eec3cb19679cc3": "0xafbd7bd91b4c1dd289ee47a4f030fbedfa7abc12",
        "0x65f7ba4ec257af7c55fd5854e5f6356bbd0fb8ec": "0xf977814e90da44bfa03b6295a0616a897441acec",
        "0x3472a5a71965499acd81997a54bba8d852c6e53d": "0xd0a7a8b98957b9cd3cfb9c0425abe44551158e9e",
        "0x2a8e1e676ec238d8a992307b495b45b3feaa5e86": "0x87650d7bbfc3a9f10587d7778206671719d9910d",
        "0x9fcf418b971134625cdf38448b949c8640971671": "0x3fb78e61784c9c637d560ede23ad57ca1294c14a",
        "0xf0a93d4994b3d98fb5e3a2f90dbc2d69073cb86b": "0xbcb91e689114b9cc865ad7871845c95241df4105",
        "0xd01ef7c0a5d8c432fc2d1a85c66cf2327362e5c6": "0xc437df90b37c1db6657339e31bfe54627f0e7181",
    }
}

NATIVES = {
    "1": [
        "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE",
        "0xeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee",
    ]
}

OVERRIDES = {
    "1": {
        "0x3432b6a60d23ca0dfca7761b7ab56459d9c964d0": (
            MintStrategy.BENEFACTOR,
            "0xc8418af6358ffdda74e09ca9cc3fe03ca6adc5b0",
        )
    }
}


@cached
def get_mint_strategy(token, network):

    if token in OVERRIDES[network]:
        return OVERRIDES[network][token]

    user = "0x1234567890123456789012345678901234567890"

    if token.lower() in NATIVES[network]:
        return (MintStrategy.NATIVE, None)

    try:
        balance_contract, balance_slot = get_balance_slot(token, network)
        user_slot = get_storage_key(user, balance_slot)
        encoded_value = "0x" + encode_single("uint256", 123456789).hex()
        web3.provider.make_request(
            "hardhat_setStorageAt", [balance_contract, user_slot, encoded_value]
        )
        assert interface.ERC20Detailed(token).balanceOf(user) == 123456789
        return (MintStrategy.BALANCES, (balance_contract, balance_slot))
    except (AssertionError):
        if token.lower() in BENEFACTORS[network]:
            return (MintStrategy.BENEFACTOR, BENEFACTORS[network][token.lower()])
        else:
            raise ValueError(
                f"Need to add benefactor data for {interface.ERC20Detailed(token).name()}"
                f" - {token} - {network}"
            )


def strip_zeros(val):
    # If the storage slot has a leading 0, hardhat gives us an error
    # this removes any leading zeroes
    return hex(int(val, 16))


def mint_tokens_for(token, user, amount=0):
    if hasattr(user, "address"):
        user = user.address
    if hasattr(token, "address"):
        token = token.address

    active_network = str(get_chain_id())
    strategy, params = get_mint_strategy(token, active_network)

    if strategy == MintStrategy.NATIVE:
        if amount == 0:
            amount = 1e18
        web3.provider.make_request("hardhat_setBalance", [user, hex(int(amount))])
        return amount

    elif strategy == MintStrategy.BALANCES:
        token = interface.ERC20Detailed(token)
        if amount == 0:
            amount = 10 ** token.decimals()

        user_slot = strip_zeros(get_storage_key(user, params[1]))
        encoded_value = "0x" + encode_single("uint256", int(amount)).hex()
        web3.provider.make_request("hardhat_setStorageAt", [params[0], user_slot, encoded_value])

    elif strategy == MintStrategy.BENEFACTOR:
        token = interface.ERC20Detailed(token)
        if amount == 0:
            amount = 10 ** token.decimals()

        token.transfer(user, amount, {"from": params})

    return amount
