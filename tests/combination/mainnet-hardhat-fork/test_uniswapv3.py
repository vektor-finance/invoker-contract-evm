import pytest
from brownie import ZERO_ADDRESS

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
    print(encoded)
    return encoded


FEE_AMOUNT_LOW = 500
FEE_AMOUNT_MEDIUM = 3000
FEE_AMOUNT_HIGH = 10000


def test_sell_invoker(cswap_uniswapv3, invoker, alice, tokens_for_alice, token, cmove):
    amount_in = tokens_for_alice.balanceOf(alice)

    min_amount_out = 0
    path = encode_path([tokens_for_alice.address, token.address], [FEE_AMOUNT_MEDIUM])

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
