import hypothesis
import pytest
from brownie import ZERO_ADDRESS, Contract, interface
from brownie.exceptions import VirtualMachineError
from brownie.test import given, strategy
from hypothesis.errors import UnsatisfiedAssumption

from data.access_control import APPROVED_COMMAND
from data.strategies import receiver_strategy, token_strategy
from data.test_helpers import isolate_fixture, mint_tokens_for


@pytest.fixture(scope="module")
def cswap_uniswapv2(invoker, deployer, CSwapUniswapV2):
    contract = deployer.deploy(CSwapUniswapV2)
    invoker.grantRole(APPROVED_COMMAND, contract, {"from": deployer})  # approve command
    yield contract


def generate_univ2_swap(data):
    a = data.draw(token_strategy(), label="Input Token")
    b = data.draw(token_strategy(), label="Output Token")
    hypothesis.assume(a["address"] != b["address"])
    user = data.draw(strategy("address"), label="User")
    input_token = Contract.from_abi(a["name"], a["address"], interface.ERC20Detailed.abi)
    output_token = Contract.from_abi(b["name"], b["address"], interface.ERC20Detailed.abi)
    max_amount = mint_tokens_for(input_token, user)
    decimals = a["decimals"] - b["decimals"]
    amount = data.draw(
        strategy("uint256", max_value=min(max_amount, 2 ** 112), min_value=10 ** decimals),
        label="Input Amount",
    )
    receiver = data.draw(receiver_strategy(), label="Receiver")
    return (input_token, output_token, user, amount, receiver)


@given(data=hypothesis.strategies.data())
def test_sell_invoker(data, uni_router, invoker, cmove, cswap_uniswapv2):
    with isolate_fixture():
        (input_token, output_token, user, amount_in, receiver) = generate_univ2_swap(data)
        path = [input_token, output_token]

        try:
            (_, amount_out) = uni_router.getAmountsOut(amount_in, path)
        except VirtualMachineError:
            raise UnsatisfiedAssumption

        hypothesis.assume(amount_out > 0)

        input_token.approve(invoker, amount_in, {"from": user})
        calldata_move_in = cmove.moveERC20In.encode_input(input_token, amount_in)
        calldata_sell = cswap_uniswapv2.sell.encode_input(
            amount_in, input_token, output_token, amount_out, (uni_router, path, receiver, 0)
        )
        calldata_move_out = cmove.moveAllERC20Out.encode_input(output_token, user)

        commands = [cmove, cswap_uniswapv2]
        calldatas = [calldata_move_in, calldata_sell]

        if receiver == ZERO_ADDRESS:
            commands.append(cmove)
            calldatas.append(calldata_move_out)

        invoker.invoke(
            commands,
            calldatas,
            {"from": user},
        )

        assert output_token.balanceOf(receiver) >= amount_out


@given(data=hypothesis.strategies.data())
def test_buy_invoker(data, uni_router, invoker, cmove, cswap_uniswapv2):
    with isolate_fixture():
        (input_token, output_token, user, amount_in, receiver) = generate_univ2_swap(data)
        starting_balance = input_token.balanceOf(user)
        path = [input_token, output_token]

        try:
            (_, amount_out) = uni_router.getAmountsOut(amount_in, path)
        except VirtualMachineError:
            raise UnsatisfiedAssumption

        hypothesis.assume(amount_out > 0)

        amount_out //= 2

        try:
            (amount_in, _) = uni_router.getAmountsIn(amount_out, path)
        except VirtualMachineError:
            raise UnsatisfiedAssumption

        hypothesis.assume(amount_in > 0)

        input_token.approve(invoker, amount_in, {"from": user})

        calldata_move_in = cmove.moveERC20In.encode_input(input_token, amount_in)
        calldata_buy = cswap_uniswapv2.buy.encode_input(
            amount_out,
            output_token,
            input_token,
            amount_in,
            (uni_router, path, receiver, 0),
        )
        calldata_sweep_out = cmove.moveAllERC20Out.encode_input(input_token, user)
        calldata_move_out = cmove.moveERC20Out.encode_input(output_token, user, amount_out)

        commands = [cmove, cswap_uniswapv2]
        calldatas = [calldata_move_in, calldata_buy]

        if receiver == ZERO_ADDRESS:
            commands.extend([cmove, cmove])
            calldatas.extend([calldata_sweep_out, calldata_move_out, calldata_move_out])

        invoker.invoke(
            commands,
            calldatas,
            {"from": user},
        )
        assert starting_balance - input_token.balanceOf(user) <= amount_in
        assert output_token.balanceOf(receiver) >= amount_out
