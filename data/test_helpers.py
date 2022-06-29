import binascii
import pickle
from contextlib import contextmanager
from enum import Enum
from functools import wraps

import brownie
from brownie import interface, web3
from brownie.exceptions import VirtualMachineError
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
        "0xbcca60bb61934080951369a648fb03df4f96263c": "0x87d48c565d0d85770406d248efd7dc3cbd41e729",
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
    },
    "10": {
        "0x1337bedc9d22ecbe766df105c9623922a27963ec": "0x061b87122ed14b9526a813209c8a59a633257bab"
    },
    "137": {
        "0x27f8d03b3a2196956ed754badc28d73be8830a6e": "0xe6c23289ba5a9f0ef31b8eb36241d5c800889b7b",
        "0x1a13f4ca1d028320a707d99520abfefca3998b7f": "0xd4f6d570133401079d213ecf4a14fa0b4bfb5b9c",
        "0x60d55f02a771d515e077c9c2403a1ef324885cec": "0xeab7831c96876433db9b8953b4e7e8f66c3125c3",
        "0x5c2ed810328349100a66b82b78a1791b101c9d61": "0x92215849c439e1f8612b6646060b4e3e5ef822cc",
        "0xe7a24ef0c5e95ffb0f6684b813a78f2a3ad7d171": "0x92215849c439e1f8612b6646060b4e3e5ef822cc",
        "0x28424507fefb6f7f8e9d3860f56504e4e5f5f390": "0x92215849c439e1f8612b6646060b4e3e5ef822cc",
        "0x013f9c3fac3e2759d7e90aca4f9540f75194a0d7": "0xd30dcad4c32091d3b7c7582329787671abcc65fb",
        "0xad326c253a84e9805559b73a08724e11e49ca651": "0x1e1506b8cf84f8d1c2dbf474bcb6fec36467c478",
        "0x1ddcaa4ed761428ae348befc6718bcb12e63bfaa": "0xda43bfd7ecc6835aa6f1761ced30b986a574c0d2",
        "0xa8d394fe7380b8ce6145d5f85e6ac22d4e91acde": "0x7a602815908e1615393148a7880a7fc9e57949ae",
    },
    "250": {
        "0x27e611fd27b276acbd5ffd632e5eaebec9761e40": "0x15bb164f9827de760174d3d3dad6816ef50de13c",
        "0x07e6332dd090d287d3489245038daf987955dcfb": "0x49c93a95dbcc9a6a4d8f77e59c038ce5020e82f8",
        "0xe578c856933d8e1082740bf7661e379aa2a30b26": "0xd1a992417a0abffa632cbde4da9f5dcf85caa858",
        "0x940f41f0ec9ba1a34cf001cc03347ac092f5f6b5": "0xec51fffe35f5b2b841103cfc5d4f5eb22c8fa33e",
        "0xd02a30d33153877bc20e5721ee53dedee0422b2f": "0xf7b9c402c4d6c2edba04a7a515b53d11b1e9b2cc",
        "0xb42bf10ab9df82f9a47b86dd76eee4ba848d0fa2": "0x9b9e258b3dace1d814f697a9d9816c5e4a8b6736",
    },
    "42161": {
        "0x7f90122bf0700f9e7e1f688fe926940e8839f353": "0xbf7e49483881c76487b0989cd7d9a8239b20ca41",
        "0xcab86f6fb6d1c2cbeeb97854a0c023446a075fe3": "0x0a824b5d4c96ea0ec46306efbd34bf88fe1277e0",
        "0x1ddcaa4ed761428ae348befc6718bcb12e63bfaa": "0x76b44e0cf9bd024dbed09e1785df295d59770138",
        "0x2d871631058827b703535228fb9ab5f35cf19e76": "0x5180db0237291a6449dda9ed33ad90a38787621c",
        "0x625e7708f30ca75bfd92586e17077590c60eb4cd": "0xc9032419aa502fafa107775dca8b7d07575d9db5",
        "0x6ab707aca953edaefbc4fd23ba73294241490620": "0x4fb361c9ce167d4049a50b42cf1db57161820cbd",
        "0x82e64f49ed5ec1bc6e43dad4fc8af9bb3a2312ee": "0x8cd67407f05526c57760d0e911d60c57b7e85c8e",
    },
    "43114": {
        "0x47afa96cdc9fab46904a55a6ad4bf6660b53c38a": "0x467b92af281d14cb6809913ad016a607b5ba8a36",
        "0x46a51127c3ce23fb7ab1de06226147f446e4a857": "0x467b92af281d14cb6809913ad016a607b5ba8a36",
        "0x532e6537fea298397212f09a61e03311686f548e": "0x467b92af281d14cb6809913ad016a607b5ba8a36",
        "0x686bef2417b6dc32c50a3cbfbcc3bb60e1e9a15d": "0x16a7da911a4dd1d83f3ff066fe28f3c792c50d90",
        "0x1337bedc9d22ecbe766df105c9623922a27963ec": "0x4620d46b4db7fb04a01a75ffed228bc027c9a899",
        "0x53f7c5869a859f0aec3d334ee8b4cf01e3492f21": "0xb755b949c126c04e0348dd881a5cf55d424742b2",
        "0x6807ed4369d9399847f306d7d835538915fa749d": "0xa867c1aca4b5f1e0a66cf7b1fe33525d57608854",
        "0xc25ff1af397b76252d6975b4d7649b35c0e60f69": "0x06960627461629409a087af6da50fe4d38d74f7e",
        "0x18cb11c9f2b6f45a7ac0a95efd322ed4cf9eeebf": "0xa5ad811c4b2bd8161090e97c946e1a2003989599",
        "0x28690ec942671ac8d9bc442b667ec338ede6dfd3": "0xd39016475200ab8957e9c772c949ef54bda69111",
    },
    "100": {
        "0x1337bedc9d22ecbe766df105c9623922a27963ec": "0xb721cc32160ab0da2614cc6ab16ed822aeebc101",
        "0x6ac78efae880282396a335ca2f79863a1e6831d4": "0x53811010085382d49ef12bcc55902bbfceb57790",
    },
}

NATIVES = [
    "0xeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee",
]

OVERRIDES = {
    "1": {
        "0x3432b6a60d23ca0dfca7761b7ab56459d9c964d0": (
            MintStrategy.BENEFACTOR,
            "0xc8418af6358ffdda74e09ca9cc3fe03ca6adc5b0",
        )
    },
    "10": {},
    "137": {},
    "250": {},
    "42161": {},
    "43114": {},
    "100": {},
}


class BenefactorError(Exception):
    pass


@cached
def get_mint_strategy(token, network):

    if token in OVERRIDES[network]:
        return OVERRIDES[network][token]

    user = "0x1234567890123456789012345678901234567890"

    if token.lower() in NATIVES:
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
            raise BenefactorError(f"{interface.ERC20Detailed(token).name()} - {token} - {network}")


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

        try:
            token.transfer(user, amount, {"from": params})
        except VirtualMachineError:
            raise BenefactorError(f"{token.name()} - {token.address} - {active_network}")

    return amount
