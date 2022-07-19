from enum import IntEnum

import pytest

from data.test_helpers import mint_tokens_for


class InterestRateMode(IntEnum):
    STABLE = 1
    VARIABLE = 2


@pytest.fixture
def data_provider(Contract, interface):
    yield Contract.from_abi(
        "Aave Data Provider",
        "0x057835Ad21a177dbdd3090bB1CAE03EaCF78Fc6d",
        interface.AaveDataProvider.abi,
    )


@pytest.fixture
def get_aave_tokens(data_provider, interface):
    def _get_aave_token(token):
        (a_token, stable_debt, variable_debt) = data_provider.getReserveTokensAddresses(token)
        return (
            interface.AaveToken(a_token),
            interface.AaveDebtToken(stable_debt),
            interface.AaveDebtToken(variable_debt),
        )

    return _get_aave_token


def test_supply(clend_aavev2, invoker, get_aave_tokens, alice, Contract, interface):
    token = Contract("USDC")
    (atoken, _, _) = get_aave_tokens(token)

    mint_tokens_for(token, alice, 100e6)

    calldata_supply = clend_aavev2.supply.encode_input(token, 100e6, alice)

    invoker.invoke([clend_aavev2], [calldata_supply], {"from": alice})
    assert atoken.balanceOf(alice) == 100e6


def test_withdraw(clend_aavev2, invoker, get_aave_tokens, alice, Contract, interface):
    token = Contract("USDC")
    (atoken, _, _) = get_aave_tokens(token)

    mint_tokens_for(atoken, invoker, 100e6)

    calldata_withdraw = clend_aavev2.withdraw.encode_input(atoken, 100e6, alice)
    invoker.invoke([clend_aavev2], [calldata_withdraw], {"from": alice})

    # this doesn't work, why?
    assert token.balanceOf(alice) == 100e6


def test_borrow_and_repay(clend_aavev2, invoker, get_aave_tokens, alice, Contract, interface):
    token = Contract("USDC")
    (atoken, _, variable_debt) = get_aave_tokens(token)

    mint_tokens_for(token, invoker, 100e6)

    calldata_supply = clend_aavev2.supply.encode_input(token, 100e6, alice)

    invoker.invoke([clend_aavev2], [calldata_supply], {"from": alice})
    assert atoken.balanceOf(alice) == 100e6

    variable_debt.approveDelegation(invoker, 2**256 - 1, {"from": alice})
    calldata_borrow = clend_aavev2.borrow.encode_input(token, 1e6, InterestRateMode.VARIABLE)
    invoker.invoke([clend_aavev2], [calldata_borrow], {"from": alice})
    assert token.balanceOf(alice) == 1e6

    calldata_repay = clend_aavev2.repay.encode_input(token, 1e6, InterestRateMode.VARIABLE)
    token.transfer(invoker, 1e6, {"from": alice})
    invoker.invoke([clend_aavev2], [calldata_repay], {"from": alice})
    assert token.balanceOf(alice) == 0
