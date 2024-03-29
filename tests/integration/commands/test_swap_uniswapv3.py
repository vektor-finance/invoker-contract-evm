import hypothesis
import pytest
from brownie import ZERO_ADDRESS, Contract, interface, web3
from brownie.test import given, strategy

from data.access_control import APPROVED_COMMAND
from data.chain import get_chain, is_uniswapv3_on_chain
from data.strategies import integration_strategy, receiver_strategy, token_strategy
from data.test_helpers import isolate_fixture, mint_tokens_for


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


# Parametrize this when other UNI V3 forks exist
UNI_V3_ROUTER = "0xE592427A0AEce92De3Edee1F18E0157C05861564"


class UniswapV3Quoter:
    """
    UniswapV3 Quoter.sol intentionally reverts and loads the quoted price into the revert message.
    Performing this using brownie will cause trigger 'debug_traceTransaction' to the node which
    results in TimeoutError.
    Future optimisation idea:
        Multicall these values
    """

    def __init__(self, address):
        self.web3contract = web3.eth.contract(address=address, abi=interface.Quoter.abi)

    def quote_exact_input(self, path, amount_in):
        try:
            return self.web3contract.functions.quoteExactInput(path, amount_in).call()
        except ValueError:
            return None

    def quote_exact_output(self, path, amount_out):
        try:
            return self.web3contract.functions.quoteExactOutput(path, amount_out).call()
        except ValueError:
            return None


@pytest.fixture(scope="module")
def quoter():
    yield UniswapV3Quoter("0xb27308f9F90D607463bb33eA1BeBb41C27CE5AB6")


def pytest_generate_tests(metafunc):
    chain = get_chain()

    if "quoter" in metafunc.fixturenames:
        enabled = is_uniswapv3_on_chain(chain)
        if not enabled:
            pytest.skip("No Uniswap V3")


def generate_univ3_swap(data):
    a = data.draw(token_strategy(), label="Input Token")
    b = data.draw(token_strategy(), label="Output Token")

    fee = data.draw(integration_strategy("uniswapv3_fee"), label="Uniswap V3 Fee")
    user = data.draw(strategy("address"), label="User")
    hypothesis.assume(a is not b)
    input_token = Contract.from_abi(a["name"], a["address"], interface.ERC20Detailed.abi)
    output_token = Contract.from_abi(b["name"], b["address"], interface.ERC20Detailed.abi)
    max_amount = mint_tokens_for(input_token, user)
    amount = data.draw(
        strategy("uint256", max_value=max_amount, min_value=10 ** a["decimals"]),
        label="Input Amount",
    )
    receiver = data.draw(receiver_strategy(), label="Receiver")
    return (input_token, output_token, fee, user, amount, receiver)


# When testing on polygon, or other networks with very few pools, we end up filtering
# out a lot of pools. We don't wan't these tests to error and instead accept that we
# might not have as many 'healthy' examples. When we implement a working venue router
# we can use this to ensure we focus tests on healthy pools.
@hypothesis.settings(suppress_health_check=[hypothesis.HealthCheck.filter_too_much])
@given(data=hypothesis.strategies.data())
def test_sell_invoker(data, cswap_uniswapv3, invoker, cmove, quoter):
    with isolate_fixture():
        (input_token, output_token, fee, user, amount_in, receiver) = generate_univ3_swap(data)
        path = encode_path([input_token.address, output_token.address], [fee])
        min_amount_out = quoter.quote_exact_input(path, amount_in)

        hypothesis.assume(min_amount_out is not None)
        hypothesis.assume(min_amount_out > 0)

        input_token.approve(invoker, amount_in, {"from": user})
        calldata_move_in = cmove.moveERC20In.encode_input(input_token, amount_in)
        calldata_sell = cswap_uniswapv3.sell.encode_input(
            amount_in,
            input_token,
            output_token,
            min_amount_out,
            (UNI_V3_ROUTER, path, receiver, 0),
        )
        calldata_move_out = cmove.moveAllERC20Out.encode_input(output_token, user)

        commands = [cmove, cswap_uniswapv3]
        calldatas = [calldata_move_in, calldata_sell]

        if receiver == ZERO_ADDRESS:
            commands.append(cmove)
            calldatas.append(calldata_move_out)

        invoker.invoke(
            commands,
            calldatas,
            {"from": user},
        )

        assert (
            output_token.balanceOf(user if receiver is ZERO_ADDRESS else receiver) >= min_amount_out
        )


# See above note re health
@hypothesis.settings(suppress_health_check=[hypothesis.HealthCheck.filter_too_much])
@given(data=hypothesis.strategies.data())
def test_buy_invoker(data, cswap_uniswapv3, invoker, cmove, quoter):
    with isolate_fixture():
        (input_token, output_token, fee, user, amount_in, receiver) = generate_univ3_swap(data)

        path = encode_path([input_token.address, output_token.address], [fee])
        reversed_path = encode_path([output_token.address, input_token.address], [fee])

        # Get the maximum amount you could buy
        amount_out = quoter.quote_exact_input(path, amount_in)

        hypothesis.assume(amount_out is not None)
        hypothesis.assume(amount_out > 0)

        amount_out //= 2
        max_amount_in = quoter.quote_exact_output(reversed_path, amount_out)

        input_token.approve(invoker, max_amount_in, {"from": user})

        calldata_move_in = cmove.moveERC20In.encode_input(input_token, max_amount_in)
        calldata_buy = cswap_uniswapv3.buy.encode_input(
            amount_out,
            output_token,
            input_token,
            max_amount_in,
            (UNI_V3_ROUTER, reversed_path, receiver, 0),
        )
        calldata_move_out = cmove.moveERC20Out.encode_input(output_token, user, amount_out)
        calldata_sweep_out = cmove.moveAllERC20Out.encode_input(input_token, user)

        starting_balance = input_token.balanceOf(user)

        commands = [cmove, cswap_uniswapv3]
        calldatas = [calldata_move_in, calldata_buy]

        if receiver == ZERO_ADDRESS:
            commands.extend([cmove, cmove])
            calldatas.extend([calldata_move_out, calldata_sweep_out])

        invoker.invoke(
            commands,
            calldatas,
            {"from": user},
        )

        assert starting_balance - input_token.balanceOf(user) <= amount_in
        assert output_token.balanceOf(user if receiver is ZERO_ADDRESS else receiver) >= amount_out
