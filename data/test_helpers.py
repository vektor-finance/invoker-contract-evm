from contextlib import contextmanager

import brownie

from data.chain import get_chain


def mint_tokens_for(minted_token, user) -> int:
    chain = get_chain()
    tokens = [asset for asset in chain["assets"] if asset.get("address")]
    for token in tokens:
        if minted_token.address.lower() == token["address"].lower():
            balance = minted_token.balanceOf(token["benefactor"])
            minted_token.transfer(user, balance, {"from": token["benefactor"]})
            return balance
    raise ValueError("could not find token")


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
