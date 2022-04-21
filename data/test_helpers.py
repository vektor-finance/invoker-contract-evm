import binascii
from contextlib import contextmanager

import brownie
from eth_abi import encode_single
from eth_account import Account
from eth_utils import keccak

from data.chain import get_chain


def bytes32(i):
    return binascii.unhexlify("%064x" % i)


def get_storage_key(address, storage_slot):
    user = int(str(address), 16)
    key = bytes32(user) + bytes32(storage_slot)
    return "0x" + keccak(key).hex()


def mint_tokens_for(minted_token, user) -> int:
    if isinstance(user, Account):
        user = user.address
    chain = get_chain()
    tokens = [asset for asset in chain["assets"] if asset.get("address")]
    for token in tokens:
        if minted_token.address.lower() == token["address"].lower():
            if token.get("benefactor"):
                balance = minted_token.balanceOf(token["benefactor"])
                minted_token.transfer(user, balance, {"from": token["benefactor"]})
                return balance
            elif "balances_slot" in token:
                storage_key = get_storage_key(user, token["balances_slot"])
                mint_value = 100_000000000000000000
                brownie.web3.provider.make_request(
                    "hardhat_setStorageAt",
                    [
                        minted_token.address,
                        storage_key,
                        "0x" + encode_single("uint256", mint_value).hex(),
                    ],
                )
                return mint_value
            else:
                raise KeyError(f"token {token['name']} does not have benefactor/balances_slot")

    raise ValueError("could not find token")


@contextmanager
def isolate_fixture():
    brownie.chain.snapshot()
    try:
        yield
    finally:
        brownie.chain.revert()
