from enum import IntEnum

import pytest
from brownie import ZERO_ADDRESS, interface, web3

from data.access_control import APPROVED_COMMAND


@pytest.fixture(scope="module")
def cswap_uniswapv3(invoker, deployer, CSwapUniswapV3):
    contract = deployer.deploy(CSwapUniswapV3)
    invoker.grantRole(APPROVED_COMMAND, contract, {"from": deployer})  # approve command
    yield contract


# https://github.com/Uniswap/v3-periphery/blob/9ca9575d09b0b8d985cc4d9a0f689f7a4470ecb7/test/shared/path.ts
def encode_path(path, fees):
    assert len(path) == len(fees) + 1
    encoded = "0x"
    for i in range(len(fees)):
        encoded += path[i][2:]
        encoded += hex(fees[i])[2:].rjust(6, "0")
    encoded += path[len(path) - 1][2:]
    return encoded


class FeeAmount(IntEnum):
    VERY_LOW = 100
    LOW = 500
    MEDIUM = 3000
    HIGH = 10000

    @staticmethod
    def list():
        return list(map(lambda c: c.value, FeeAmount))

    @staticmethod
    def labels():
        return list(map(lambda c: "FEE_" + c.name, FeeAmount))


class UniswapV3Quoter:
    def __init__(self, address):
        self.web3contract = web3.eth.contract(address=address, abi=interface.Quoter.abi)

    def quote_exact_input(self, path, amount_in):
        try:
            return self.web3contract.functions.quoteExactInput(path, amount_in).call()
        except ValueError:
            return None


@pytest.fixture(scope="module")
def quoter():
    yield UniswapV3Quoter("0xb27308f9F90D607463bb33eA1BeBb41C27CE5AB6")


@pytest.mark.parametrize("fees", FeeAmount.list(), ids=FeeAmount.labels())
@pytest.mark.dedupe("tokens_for_alice", "token")
def test_sell_invoker(
    cswap_uniswapv3, invoker, alice, tokens_for_alice, token, cmove, fees, quoter
):

    amount_in = tokens_for_alice.balanceOf(alice)

    path = encode_path([tokens_for_alice.address, token.address], [fees])

    min_amount_out = quoter.quote_exact_input(path, amount_in)

    if min_amount_out is None:
        pytest.skip("Can't get output price")

    tokens_for_alice.approve(invoker, amount_in, {"from": alice})

    calldata_move_in = cmove.moveERC20In.encode_input(tokens_for_alice, amount_in)
    calldata_sell = cswap_uniswapv3.sell.encode_input(
        amount_in, tokens_for_alice, token, min_amount_out, (path, ZERO_ADDRESS, 0)
    )
    calldata_move_out = cmove.moveAllERC20Out.encode_input(token, alice)

    invoker.invoke(
        [cmove, cswap_uniswapv3, cmove],
        [calldata_move_in, calldata_sell, calldata_move_out],
        {"from": alice},
    )

    assert token.balanceOf(alice) >= min_amount_out
